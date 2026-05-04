"""Idempotently patch a vendored EasyABC easy_abc.py to wire in vi mode.

Usage:
    python3 patch.py <path-to-easy_abc.py>

Adds (only if not already present):
  1. ``import aui_compat`` near the top (silences wx 4.x AUI float crash).
  2. ``ViMode`` instantiation right after the editor's EVT_CHAR bind.
  3. ``_watch_timer`` setup right after the existing 2-second timer.
  4. ``_handle_vi_ex`` + watch helpers as new methods after ``OnSaveAs``.

Detects prior patches by string markers and skips them, so re-running is safe.
"""

import sys


AUI_MARKER = "import aui_compat"
AUI_BLOCK = "import aui_compat  # noqa: F401  -- silences wx 4.x AUI DrawSeparator float crash\n"

VIMODE_MARKER = "from vi_mode import ViMode"
VIMODE_ANCHOR = "self.editor.Bind(wx.EVT_CHAR, self.OnCharEvent)"
VIMODE_BLOCK = """\
        # Vi mode (F12 to toggle)
        try:
            from vi_mode import ViMode
            self.vi_mode = ViMode(
                self.editor,
                status_callback=lambda msg: self.statusbar.SetStatusText(msg, 0),
                ex_handler=self._handle_vi_ex,
            )
        except Exception as _vi_err:
            print('vi_mode disabled:', _vi_err)
"""

WATCH_MARKER = "self._watch_timer = wx.Timer(self)"
WATCH_ANCHOR = "self.timer.Start(2000, wx.TIMER_CONTINUOUS)"
WATCH_BLOCK = """\

        # Vi :watch -- file-watcher for "vim is editor, EasyABC is player" workflow
        self._watch_timer = wx.Timer(self)
        self._watch_mtime = None
        self._watch_enabled = False
        self.Bind(wx.EVT_TIMER, self._on_watch_tick, self._watch_timer)
"""

EXMETHOD_MARKER = "def _handle_vi_ex(self, cmd):"
EXMETHOD_ANCHOR = "    def OnSaveAs(self, evt):\n        self.save_as()\n"
EXMETHOD_BLOCK = '''
    def _handle_vi_ex(self, cmd):
        """Route vi ex commands to the host application."""
        cmd = cmd.strip()
        if cmd in ('w', 'w!'):
            self.OnSave(None)
        elif cmd in ('q', 'q!'):
            self.Close(force=(cmd == 'q!'))
        elif cmd in ('wq', 'x'):
            self.OnSave(None)
            self.Close()
        elif cmd == 'play':
            self.play()
        elif cmd == 'stop':
            self.stop_playing()
        elif cmd == 'watch':
            self._watch_start()
        elif cmd == 'nowatch':
            self._watch_stop()
        elif cmd in ('e', 'reload'):
            self._watch_reload()
        elif cmd.startswith('e '):
            path = cmd[2:].strip()
            if path:
                self.load(os.path.abspath(os.path.expanduser(path)))

    def _watch_start(self):
        if not self.current_file:
            print('vi :watch needs a file loaded; use :e <path> first')
            return
        try:
            self._watch_mtime = os.path.getmtime(self.current_file)
        except OSError:
            self._watch_mtime = None
        self._watch_enabled = True
        self._watch_timer.Start(500)
        self.editor.SetReadOnly(True)
        self.SetTitle('%s - %s [watching]' % (program_name, self.document_name or ''))

    def _watch_stop(self):
        self._watch_timer.Stop()
        self._watch_enabled = False
        self.editor.SetReadOnly(False)
        if self.document_name:
            self.SetTitle('%s - %s' % (program_name, self.document_name))

    def _watch_reload(self):
        if not self.current_file:
            return
        pos = self.editor.GetCurrentPos()
        was_readonly = self.editor.GetReadOnly()
        if was_readonly:
            self.editor.SetReadOnly(False)
        try:
            self.load(self.current_file, editor_pos=pos)
        finally:
            if was_readonly:
                self.editor.SetReadOnly(True)

    def _on_watch_tick(self, evt):
        if not self._watch_enabled or not self.current_file:
            return
        try:
            mtime = os.path.getmtime(self.current_file)
        except OSError:
            return
        if self._watch_mtime is None:
            self._watch_mtime = mtime
            return
        if mtime != self._watch_mtime:
            self._watch_mtime = mtime
            self._watch_reload()
'''


def _insert_after(src, anchor, block, marker):
    if marker in src:
        return src, False
    idx = src.find(anchor)
    if idx < 0:
        raise RuntimeError('anchor not found: %r' % anchor[:60])
    end = idx + len(anchor)
    return src[:end] + '\n' + block + src[end:], True


def patch(path):
    with open(path, encoding='utf-8') as fh:
        src = fh.read()

    changed = False

    # 1. aui_compat import — placed after the program_version line so it's
    # close to the top but doesn't break the header comment block.
    if AUI_MARKER not in src:
        anchor = "program_version = '"
        idx = src.find(anchor)
        if idx < 0:
            raise RuntimeError("anchor 'program_version' not found")
        line_end = src.find('\n', idx) + 1
        # Insert BEFORE program_version line
        line_start = src.rfind('\n', 0, idx) + 1
        src = src[:line_start] + AUI_BLOCK + '\n' + src[line_start:]
        changed = True
        print('  + aui_compat import')
    else:
        print('  = aui_compat import (already present)')

    # 2. ViMode instantiation
    src, did = _insert_after(src, VIMODE_ANCHOR, VIMODE_BLOCK, VIMODE_MARKER)
    if did:
        changed = True
        print('  + ViMode wire-in')
    else:
        print('  = ViMode wire-in (already present)')

    # 3. Watch timer setup
    src, did = _insert_after(src, WATCH_ANCHOR, WATCH_BLOCK, WATCH_MARKER)
    if did:
        changed = True
        print('  + _watch_timer setup')
    else:
        print('  = _watch_timer setup (already present)')

    # 4. _handle_vi_ex + watch helpers
    src, did = _insert_after(src, EXMETHOD_ANCHOR, EXMETHOD_BLOCK, EXMETHOD_MARKER)
    if did:
        changed = True
        print('  + _handle_vi_ex + watch helpers')
    else:
        print('  = _handle_vi_ex (already present)')

    if changed:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(src)
        print('Patched:', path)
    else:
        print('No changes needed:', path)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 patch.py <path-to-easy_abc.py>', file=sys.stderr)
        sys.exit(2)
    patch(sys.argv[1])

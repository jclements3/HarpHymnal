"""Embedded vi mode dispatcher for EasyABC's StyledTextCtrl editor.

ViMode owns the mode state machine and routes wx key events to motion,
operator, and search primitives provided by sibling modules. Vi behavior is
disabled by default; F12 toggles it.
"""

import string

import wx
import wx.stc as stc

from vi_motions import Motions
from vi_operators import Operators
from vi_search import Search


# Mode constants
NORMAL = 0
INSERT = 1
VISUAL = 2
V_LINE = 3
COMMAND = 4

_MODE_LABEL = {
    NORMAL: '-- NORMAL --',
    INSERT: '-- INSERT --',
    VISUAL: '-- VISUAL --',
    V_LINE: '-- V-LINE --',
}

# Linewise motion chars trigger linewise operator semantics for d/c/y.
_LINEWISE_MOTION_CHARS = {'j', 'k', 'G'}


class ViMode:
    """State machine + key dispatcher for vi-style editing."""

    def __init__(self, editor, status_callback=None, ex_handler=None):
        self.editor = editor
        self.status_callback = status_callback or (lambda msg: None)
        self.ex_handler = ex_handler or (lambda cmd: None)

        self.motions = Motions(editor)
        self.operators = Operators(editor)
        self.search = Search(editor)

        self.enabled = True
        self.mode = NORMAL

        # Pending state for multi-key sequences.
        self.count = ''
        self.pending_op = None
        self.pending_g = False
        self.pending_arg = None  # 'f', 'F', 't', 'T', 'r'
        self.visual_anchor = None
        self.cmdline = ''

        editor.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        editor.Bind(wx.EVT_CHAR, self.on_char)

        wx.CallAfter(self._enter_normal, reset_caret=False)

    # ------------------------------------------------------------------ enable

    def toggle(self):
        if self.enabled:
            self._disable()
        else:
            self._enable()

    def _enable(self):
        self.enabled = True
        self._enter_normal(reset_caret=False)

    def _disable(self):
        self.enabled = False
        self.mode = NORMAL
        self._reset_pending()
        self._set_caret_style(stc.STC_CARETSTYLE_LINE)
        self.status_callback('')

    def _set_caret_style(self, style):
        # Older Scintilla builds may lack one of these constants or the API.
        try:
            self.editor.SetCaretStyle(style)
        except Exception:
            pass

    # ------------------------------------------------------------------ status

    def _emit_status(self):
        if not self.enabled:
            self.status_callback('')
            return
        if self.mode == COMMAND:
            self.status_callback(self.cmdline)
            return
        label = _MODE_LABEL.get(self.mode, '')
        hint = self._pending_hint()
        if hint:
            self.status_callback('{}    [{}]'.format(label, hint))
        else:
            self.status_callback(label)

    def _pending_hint(self):
        parts = []
        if self.count:
            parts.append(self.count)
        if self.pending_op:
            parts.append(self.pending_op)
        if self.pending_g:
            parts.append('g')
        if self.pending_arg:
            parts.append(self.pending_arg)
        return ''.join(parts)

    # ------------------------------------------------------------------ helpers

    def _reset_pending(self):
        self.count = ''
        self.pending_op = None
        self.pending_g = False
        self.pending_arg = None

    def _take_count(self, default=1):
        n = int(self.count) if self.count else default
        return max(n, 1) if default >= 1 else n

    def _enter_normal(self, reset_caret=True):
        prev = self.mode
        self.mode = NORMAL
        self._reset_pending()
        self.cmdline = ''
        self.visual_anchor = None
        self.editor.SetEmptySelection(self.editor.GetCurrentPos())
        if reset_caret and prev == INSERT:
            # Vim convention: Esc from insert nudges caret left.
            pos = self.editor.GetCurrentPos()
            line = self.editor.LineFromPosition(pos)
            line_start = self.editor.PositionFromLine(line)
            new_pos = max(line_start, pos - 1)
            self.editor.GotoPos(new_pos)
        self._set_caret_style(stc.STC_CARETSTYLE_BLOCK)
        self._emit_status()

    def _enter_insert(self):
        self.mode = INSERT
        self._reset_pending()
        self._set_caret_style(stc.STC_CARETSTYLE_LINE)
        self._emit_status()

    def _enter_visual(self, linewise):
        self.mode = V_LINE if linewise else VISUAL
        self.visual_anchor = self.editor.GetCurrentPos()
        self._reset_pending()
        self._set_caret_style(stc.STC_CARETSTYLE_BLOCK)
        self._update_visual_selection()
        self._emit_status()

    def _enter_command(self, prefix):
        self.mode = COMMAND
        self.cmdline = prefix
        self._emit_status()

    def _update_visual_selection(self):
        if self.visual_anchor is None:
            return
        caret = self.editor.GetCurrentPos()
        if self.mode == VISUAL:
            lo, hi = sorted((self.visual_anchor, caret))
            # Inclusive selection: extend by one so the char under caret is selected.
            self.editor.SetSelection(lo, hi + 1)
        elif self.mode == V_LINE:
            a_line = self.editor.LineFromPosition(self.visual_anchor)
            c_line = self.editor.LineFromPosition(caret)
            lo_line, hi_line = sorted((a_line, c_line))
            start = self.editor.PositionFromLine(lo_line)
            end = self.editor.GetLineEndPosition(hi_line)
            # Include trailing newline so linewise yank/delete grabs the full line.
            doc_end = self.editor.GetLength()
            if end < doc_end:
                end += 1
            self.editor.SetSelection(start, end)

    # ------------------------------------------------------------------ events

    def on_key_down(self, evt):
        key = evt.GetKeyCode()

        if key == wx.WXK_F12:
            self.toggle()
            return

        if not self.enabled:
            evt.Skip()
            return

        ctrl = evt.ControlDown()

        # Ctrl-[ is a synonym for Esc in vim.
        if ctrl and key == ord('['):
            self._handle_escape()
            return

        if key == wx.WXK_ESCAPE:
            self._handle_escape()
            return

        if self.mode == INSERT:
            evt.Skip()
            return

        if self.mode == COMMAND:
            if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
                self._execute_cmdline()
                return
            if key == wx.WXK_BACK:
                if len(self.cmdline) > 1:
                    self.cmdline = self.cmdline[:-1]
                    self._emit_status()
                else:
                    self._enter_normal(reset_caret=False)
                return
            # Printable chars handled in on_char — must Skip() in EVT_KEY_DOWN
            # so wx fires EVT_CHAR. on_char will then consume without Skip().
            if 32 <= key <= 126 and not ctrl:
                evt.Skip()
                return
            evt.Skip()
            return

        # NORMAL / VISUAL / V_LINE
        if ctrl and key in (ord('R'), ord('r')):
            n = self._take_count()
            for _ in range(n):
                self.editor.Redo()
            self._reset_pending()
            self._emit_status()
            return

        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            n = self._take_count()
            target = self.motions.down(n)
            self.editor.GotoPos(target)
            target = self.motions.first_nonblank()
            self.editor.GotoPos(target)
            self._reset_pending()
            if self.mode in (VISUAL, V_LINE):
                self._update_visual_selection()
            self._emit_status()
            return

        if key == wx.WXK_BACK:
            n = self._take_count()
            target = self.motions.left(n)
            self._do_motion_or_op(target, linewise=False)
            return

        if key in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN):
            n = self._take_count()
            if key == wx.WXK_LEFT:
                target = self.motions.left(n)
            elif key == wx.WXK_RIGHT:
                target = self.motions.right(n)
            elif key == wx.WXK_UP:
                target = self.motions.up(n)
            else:
                target = self.motions.down(n)
            self._do_motion_or_op(target, linewise=(key in (wx.WXK_UP, wx.WXK_DOWN)))
            return

        # Printable (unmodified): Skip() so wx fires EVT_CHAR, where on_char
        # dispatches and consumes without Skip — that prevents editor insertion.
        # Ctrl/Alt-modified keys fall through to evt.Skip() so menu accelerators
        # (Ctrl-S etc.) still work.
        if 32 <= key <= 126 and not ctrl and not evt.AltDown():
            evt.Skip()
            return

        evt.Skip()
    def on_char(self, evt):
        if not self.enabled or self.mode == INSERT:
            evt.Skip()
            return

        try:
            code = evt.GetUnicodeKey() or evt.GetKeyCode()
            ch = chr(code) if code else ''
        except (ValueError, OverflowError):
            evt.Skip()
            return

        if not ch or not ch.isprintable():
            evt.Skip()
            return

        if self.mode == COMMAND:
            self.cmdline += ch
            self._emit_status()
            return

        if self.mode == NORMAL:
            self._dispatch_normal(ch)
            return

        if self.mode in (VISUAL, V_LINE):
            self._dispatch_visual(ch)
            return

    def _handle_escape(self):
        if self.mode == COMMAND:
            self._enter_normal(reset_caret=False)
            return
        if self.mode in (VISUAL, V_LINE):
            self.editor.SetEmptySelection(self.editor.GetCurrentPos())
        self._enter_normal()

    # ------------------------------------------------------------------ normal

    def _dispatch_normal(self, ch):
        # 1. pending_arg: f/F/t/T target char, or r replacement.
        if self.pending_arg in ('f', 'F', 't', 'T'):
            self._apply_find_char(ch)
            return
        if self.pending_arg == 'r':
            n = self._take_count()
            self.operators.replace_char(ch, n)
            self._reset_pending()
            self._emit_status()
            return

        # 2. gg sequence.
        if self.pending_g:
            self.pending_g = False
            if ch == 'g':
                n = int(self.count) if self.count else 1
                target = self.motions.doc_start(n)
                if self.pending_op:
                    self._apply_op_motion(target, linewise=True)
                else:
                    self.editor.GotoPos(target)
                    if self.mode in (VISUAL, V_LINE):
                        self._update_visual_selection()
                self._reset_pending()
                self._emit_status()
                return
            self._reset_pending()
            self._emit_status()
            return

        # 3. Digit count: bare 0 with no count is a motion.
        if ch.isdigit() and (ch != '0' or self.count):
            self.count += ch
            self._emit_status()
            return

        # 4. Linewise op shortcut: dd, cc, yy.
        if self.pending_op and ch == self.pending_op:
            self._apply_linewise_self_op()
            return

        # 5. Operator + motion.
        if self.pending_op:
            if ch == 'g':
                self.pending_g = True
                self._emit_status()
                return
            if ch in ('f', 'F', 't', 'T'):
                self.pending_arg = ch
                self._emit_status()
                return
            target = self._compute_motion(ch)
            if target is None:
                self._reset_pending()
                self._emit_status()
                return
            linewise = ch in _LINEWISE_MOTION_CHARS
            self._apply_op_motion(target, linewise=linewise)
            return

        # 6. Plain dispatch.
        self._dispatch_normal_action(ch)

    def _compute_motion(self, ch):
        n = self._take_count()
        if ch == 'h':
            return self.motions.left(n)
        if ch == 'l':
            return self.motions.right(n)
        if ch == 'j':
            return self.motions.down(n)
        if ch == 'k':
            return self.motions.up(n)
        if ch == 'w':
            return self.motions.word_forward(n)
        if ch == 'W':
            return self.motions.word_forward(n, big=True)
        if ch == 'b':
            return self.motions.word_backward(n)
        if ch == 'B':
            return self.motions.word_backward(n, big=True)
        if ch == 'e':
            return self.motions.word_end(n)
        if ch == 'E':
            return self.motions.word_end(n, big=True)
        if ch == '0':
            return self.motions.line_start()
        if ch == '^':
            return self.motions.first_nonblank()
        if ch == '$':
            return self.motions.line_end()
        if ch == 'G':
            return self.motions.doc_end(int(self.count) if self.count else 0)
        if ch == '%':
            return self.motions.match_brace()
        return None

    def _dispatch_normal_action(self, ch):
        n = max(int(self.count) if self.count else 1, 1)

        # Motions (non-pending case).
        target = self._compute_motion(ch)
        if target is not None:
            self.editor.GotoPos(target)
            self._reset_pending()
            self._emit_status()
            return

        if ch == 'g':
            self.pending_g = True
            self._emit_status()
            return

        if ch in ('f', 'F', 't', 'T'):
            self.pending_arg = ch
            self._emit_status()
            return

        # Insert entries.
        if ch == 'i':
            self._enter_insert(); return
        if ch == 'I':
            self.editor.GotoPos(self.motions.first_nonblank())
            self._enter_insert(); return
        if ch == 'a':
            pos = self.editor.GetCurrentPos()
            line = self.editor.LineFromPosition(pos)
            eol = self.editor.GetLineEndPosition(line)
            if pos < eol:
                self.editor.GotoPos(pos + 1)
            self._enter_insert(); return
        if ch == 'A':
            self.editor.GotoPos(self.motions.line_end(allow_past_eol=True))
            self._enter_insert(); return
        if ch == 'o':
            self.editor.GotoPos(self.motions.line_end(allow_past_eol=True))
            self.editor.AddText('\n')
            self._enter_insert(); return
        if ch == 'O':
            line = self.editor.LineFromPosition(self.editor.GetCurrentPos())
            line_start = self.editor.PositionFromLine(line)
            self.editor.GotoPos(line_start)
            self.editor.AddText('\n')
            self.editor.GotoPos(line_start)
            self._enter_insert(); return

        # Operators.
        if ch in ('d', 'c', 'y'):
            self.pending_op = ch
            self._emit_status()
            return

        # Quick edits.
        if ch == 'x':
            pos = self.editor.GetCurrentPos()
            end = self.motions.right(n, allow_past_eol=True)
            self.operators.delete(pos, end)
            self._reset_pending(); self._emit_status(); return
        if ch == 'X':
            pos = self.editor.GetCurrentPos()
            start = self.motions.left(n)
            self.operators.delete(start, pos)
            self._reset_pending(); self._emit_status(); return
        if ch == 'D':
            pos = self.editor.GetCurrentPos()
            end = self.motions.line_end(allow_past_eol=True)
            self.operators.delete(pos, end)
            self._reset_pending(); self._emit_status(); return
        if ch == 'C':
            pos = self.editor.GetCurrentPos()
            end = self.motions.line_end(allow_past_eol=True)
            self.operators.change(pos, end)
            self._enter_insert(); return
        if ch == 'Y':
            self._apply_linewise_yank(n)
            self._reset_pending(); self._emit_status(); return
        if ch == 's':
            pos = self.editor.GetCurrentPos()
            end = self.motions.right(n, allow_past_eol=True)
            self.operators.change(pos, end)
            self._enter_insert(); return
        if ch == 'S':
            self._apply_linewise_change(n)
            self._enter_insert(); return
        if ch == 'r':
            self.pending_arg = 'r'
            self._emit_status(); return
        if ch == '~':
            self.operators.toggle_case(n)
            self._reset_pending(); self._emit_status(); return

        # Paste.
        if ch == 'p':
            self.operators.paste_after(n)
            self._reset_pending(); self._emit_status(); return
        if ch == 'P':
            self.operators.paste_before(n)
            self._reset_pending(); self._emit_status(); return

        # Visual.
        if ch == 'v':
            self._enter_visual(linewise=False); return
        if ch == 'V':
            self._enter_visual(linewise=True); return

        # Undo.
        if ch == 'u':
            for _ in range(n):
                self.editor.Undo()
            self._reset_pending(); self._emit_status(); return

        # Search and ex.
        if ch == '/':
            self._enter_command('/'); return
        if ch == '?':
            self._enter_command('?'); return
        if ch == 'n':
            pos = self.search.repeat(reverse=False)
            if pos >= 0:
                self.editor.GotoPos(pos)
            self._reset_pending(); self._emit_status(); return
        if ch == 'N':
            pos = self.search.repeat(reverse=True)
            if pos >= 0:
                self.editor.GotoPos(pos)
            self._reset_pending(); self._emit_status(); return
        if ch == ':':
            self._enter_command(':'); return

        # Unhandled: drop pending state silently.
        self._reset_pending()
        self._emit_status()
    def _apply_find_char(self, ch):
        kind = self.pending_arg
        n = self._take_count()
        forward = kind in ('f', 't')
        before = kind in ('t', 'T')
        target = self.motions.find_char(ch, forward, before)
        if target < 0:
            self._reset_pending()
            self._emit_status()
            return

        if self.pending_op:
            # f/t are inclusive in operator-pending: dft deletes through t.
            cur = self.editor.GetCurrentPos()
            if forward:
                end = target + 1 if kind == 'f' else target
                self._apply_op_motion(end, linewise=False, override_start=cur)
            else:
                start = target if kind == 'F' else target + 1
                self._apply_op_motion(start, linewise=False, override_end=cur)
        else:
            for _ in range(n - 1):
                self.editor.GotoPos(target)
                target = self.motions.find_char(ch, forward, before)
                if target < 0:
                    break
            if target >= 0:
                self.editor.GotoPos(target)
        self._reset_pending()
        if self.mode in (VISUAL, V_LINE):
            self._update_visual_selection()
        self._emit_status()

    def _apply_op_motion(self, target, linewise, override_start=None, override_end=None):
        op = self.pending_op
        cur = self.editor.GetCurrentPos()
        if override_start is not None or override_end is not None:
            a = override_start if override_start is not None else cur
            b = override_end if override_end is not None else target
            start, end = sorted((a, b))
        else:
            start, end = sorted((cur, target))

        if linewise:
            start_line = self.editor.LineFromPosition(start)
            end_line = self.editor.LineFromPosition(end)
            start = self.editor.PositionFromLine(start_line)
            end = self.editor.GetLineEndPosition(end_line)
            doc_end = self.editor.GetLength()
            if end < doc_end:
                end += 1

        if op == 'd':
            self.operators.delete(start, end, linewise=linewise)
        elif op == 'y':
            self.operators.yank(start, end, linewise=linewise)
            # Yank shouldn't move caret; restore.
            self.editor.GotoPos(cur)
        elif op == 'c':
            self.operators.change(start, end, linewise=linewise)
            self._enter_insert()
            return

        self._reset_pending()
        self._emit_status()

    def _apply_linewise_self_op(self):
        op = self.pending_op
        n = self._take_count()
        if op == 'y':
            self._apply_linewise_yank(n)
        elif op == 'd':
            self._apply_linewise_delete(n)
        elif op == 'c':
            self._apply_linewise_change(n)
            self._enter_insert()
            return
        self._reset_pending()
        self._emit_status()

    def _line_range(self, n):
        cur = self.editor.GetCurrentPos()
        line = self.editor.LineFromPosition(cur)
        last_line = min(line + n - 1, self.editor.GetLineCount() - 1)
        start = self.editor.PositionFromLine(line)
        end = self.editor.GetLineEndPosition(last_line)
        doc_end = self.editor.GetLength()
        if end < doc_end:
            end += 1
        return start, end

    def _apply_linewise_yank(self, n):
        start, end = self._line_range(n)
        cur = self.editor.GetCurrentPos()
        self.operators.yank(start, end, linewise=True)
        self.editor.GotoPos(cur)

    def _apply_linewise_delete(self, n):
        start, end = self._line_range(n)
        self.operators.delete(start, end, linewise=True)

    def _apply_linewise_change(self, n):
        start, end = self._line_range(n)
        self.operators.change(start, end, linewise=True)

    def _do_motion_or_op(self, target, linewise):
        if self.pending_op:
            self._apply_op_motion(target, linewise=linewise)
            return
        self.editor.GotoPos(target)
        if self.mode in (VISUAL, V_LINE):
            self._update_visual_selection()
        self._reset_pending()
        self._emit_status()

    # ------------------------------------------------------------------ visual

    def _dispatch_visual(self, ch):
        if self.pending_arg in ('f', 'F', 't', 'T'):
            self._apply_find_char(ch)
            return

        if self.pending_g:
            self.pending_g = False
            if ch == 'g':
                n = int(self.count) if self.count else 1
                self.editor.GotoPos(self.motions.doc_start(n))
                self._update_visual_selection()
            self._reset_pending()
            self._emit_status()
            return

        if ch.isdigit() and (ch != '0' or self.count):
            self.count += ch
            self._emit_status()
            return

        # Mode switches.
        if ch == 'v':
            if self.mode == VISUAL:
                self._enter_normal(reset_caret=False)
            else:
                self.mode = VISUAL
                self._update_visual_selection()
                self._emit_status()
            return
        if ch == 'V':
            if self.mode == V_LINE:
                self._enter_normal(reset_caret=False)
            else:
                self.mode = V_LINE
                self._update_visual_selection()
                self._emit_status()
            return

        if ch == 'g':
            self.pending_g = True
            self._emit_status()
            return
        if ch in ('f', 'F', 't', 'T'):
            self.pending_arg = ch
            self._emit_status()
            return

        # Motions extend selection.
        target = self._compute_motion(ch)
        if target is not None:
            self.editor.GotoPos(target)
            self._update_visual_selection()
            self._reset_pending()
            self._emit_status()
            return

        # Operators on selection.
        linewise = (self.mode == V_LINE)
        sel_start, sel_end = self.editor.GetSelection()
        if ch in ('d', 'x'):
            self.operators.delete(sel_start, sel_end, linewise=linewise)
            self._enter_normal(reset_caret=False); return
        if ch == 'c':
            self.operators.change(sel_start, sel_end, linewise=linewise)
            self._enter_insert(); return
        if ch == 'y':
            self.operators.yank(sel_start, sel_end, linewise=linewise)
            self.editor.GotoPos(sel_start)
            self._enter_normal(reset_caret=False); return
        if ch == '~':
            self.editor.SetSelection(sel_start, sel_end)
            self.operators.toggle_case(1)
            self._enter_normal(reset_caret=False); return
        if ch == ':':
            self._enter_command(':'); return

        # Unknown: drop pending.
        self._reset_pending()
        self._emit_status()

    # ------------------------------------------------------------------ cmdline

    def _execute_cmdline(self):
        cmd = self.cmdline
        self._enter_normal(reset_caret=False)
        if not cmd:
            return
        prefix, rest = cmd[0], cmd[1:]

        if prefix in ('/', '?'):
            if rest:
                pos = self.search.search(rest, backward=(prefix == '?'))
                if pos >= 0:
                    self.editor.GotoPos(pos)
            return

        if prefix == ':':
            body = rest.strip()
            if not body:
                return
            if body in ('w', 'q', 'wq', 'w!', 'q!', 'x'):
                self.ex_handler(body)
                return
            if body.isdigit():
                line = max(0, int(body) - 1)
                self.editor.GotoPos(self.editor.PositionFromLine(line))
                return
            if body.startswith('s/') or body.startswith('%s/'):
                self.search.substitute(body)
                return
            self.ex_handler(body)
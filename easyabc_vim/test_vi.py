"""Self-contained test harness for vi_mode + vi_motions + vi_operators + vi_search.

Stubs out wx / wx.stc so vi_mode imports cleanly without a GUI, then drives
synthetic key events through the dispatcher and asserts buffer/cursor state.

Run with:  python3 test_vi.py
       or: python3 test_vi.py <pattern>     # run only matching tests
"""

import os
import sys
import types

# ---------------------------------------------------------------- wx mocks

class _MockEvent:
    def __init__(self, key=0, unicode_key=None, ctrl=False, alt=False, shift=False):
        self._key = key
        self._unicode = unicode_key if unicode_key is not None else key
        self._ctrl = ctrl
        self._alt = alt
        self._shift = shift
        self.skipped = False
    def GetKeyCode(self): return self._key
    def GetUnicodeKey(self): return self._unicode
    def ControlDown(self): return self._ctrl
    def AltDown(self): return self._alt
    def ShiftDown(self): return self._shift
    def Skip(self, skip=True): self.skipped = skip


_mock_wx = types.ModuleType('wx')
_mock_wx.EVT_KEY_DOWN = 'EVT_KEY_DOWN'
_mock_wx.EVT_CHAR = 'EVT_CHAR'
_mock_wx.WXK_F12 = 343
_mock_wx.WXK_ESCAPE = 27
_mock_wx.WXK_RETURN = 13
_mock_wx.WXK_NUMPAD_ENTER = 370
_mock_wx.WXK_BACK = 8
_mock_wx.WXK_LEFT = 314
_mock_wx.WXK_RIGHT = 316
_mock_wx.WXK_UP = 315
_mock_wx.WXK_DOWN = 317
_mock_wx.CallAfter = lambda fn, *a, **kw: fn(*a, **kw)

_mock_stc = types.ModuleType('wx.stc')
_mock_stc.STC_CARETSTYLE_BLOCK = 2
_mock_stc.STC_CARETSTYLE_LINE = 1
_mock_wx.stc = _mock_stc

sys.modules['wx'] = _mock_wx
sys.modules['wx.stc'] = _mock_stc


# ---------------------------------------------------------------- fake editor

class FakeEditor:
    """Minimal Scintilla shim backed by a Python str."""

    def __init__(self, text=""):
        self.text = text
        self.pos = 0
        self.anchor = 0
        self.target_start = 0
        self.target_end = 0
        self.read_only = False
        self.undo_stack = []
        self.redo_stack = []
        self.in_undo_action = 0
        self._handlers = {}

    # binding hooks (no-op; we drive ViMode methods directly)
    def Bind(self, evt_type, handler, source=None):
        self._handlers[evt_type] = handler

    def SetCaretStyle(self, style): pass
    def SetReadOnly(self, b): self.read_only = bool(b)
    def GetReadOnly(self): return self.read_only

    def BeginUndoAction(self): self.in_undo_action += 1
    def EndUndoAction(self):   self.in_undo_action = max(0, self.in_undo_action - 1)

    def _snap(self):
        self.undo_stack.append((self.text, self.pos, self.anchor))
        self.redo_stack.clear()

    def Undo(self):
        if self.undo_stack:
            self.redo_stack.append((self.text, self.pos, self.anchor))
            self.text, self.pos, self.anchor = self.undo_stack.pop()

    def Redo(self):
        if self.redo_stack:
            self.undo_stack.append((self.text, self.pos, self.anchor))
            self.text, self.pos, self.anchor = self.redo_stack.pop()

    # cursor / selection
    def GetCurrentPos(self): return self.pos
    def GotoPos(self, p):
        self.pos = max(0, min(len(self.text), p))
        self.anchor = self.pos
    def SetCurrentPos(self, p): self.pos = max(0, min(len(self.text), p))
    def SetEmptySelection(self, p): self.GotoPos(p)
    def SetSelection(self, anchor, caret):
        self.anchor = max(0, min(len(self.text), anchor))
        self.pos = max(0, min(len(self.text), caret))
    def GetSelectionStart(self): return min(self.anchor, self.pos)
    def GetSelectionEnd(self):   return max(self.anchor, self.pos)
    def GetSelectedText(self):
        return self.text[self.GetSelectionStart():self.GetSelectionEnd()]

    # text access
    def GetText(self): return self.text
    def SetText(self, t):
        self._snap()
        self.text = t
        self.pos = min(self.pos, len(t))
        self.anchor = min(self.anchor, len(t))
    def ClearAll(self):
        self._snap()
        self.text = ""
        self.pos = 0
        self.anchor = 0
    def GetTextLength(self): return len(self.text)
    def GetCharAt(self, p):
        if 0 <= p < len(self.text):
            return ord(self.text[p])
        return 0
    def GetTextRange(self, s, e):
        s = max(0, s); e = max(s, min(len(self.text), e))
        return self.text[s:e]

    # lines
    def LineFromPosition(self, p):
        p = max(0, min(len(self.text), p))
        return self.text[:p].count('\n')
    def PositionFromLine(self, line):
        if line <= 0: return 0
        idx = -1
        for _ in range(line):
            idx = self.text.find('\n', idx + 1)
            if idx < 0:
                return len(self.text)
        return idx + 1
    def GetLineEndPosition(self, line):
        start = self.PositionFromLine(line)
        nl = self.text.find('\n', start)
        return nl if nl >= 0 else len(self.text)
    def GetLineCount(self):
        return self.text.count('\n') + 1
    def GetLine(self, line):
        s = self.PositionFromLine(line)
        e = self.GetLineEndPosition(line)
        if e < len(self.text) and self.text[e] == '\n':
            e += 1
        return self.text[s:e]

    # editing
    def SetTargetStart(self, p): self.target_start = p
    def SetTargetEnd(self, p):   self.target_end = p
    def ReplaceTarget(self, t):
        self._snap()
        s, e = self.target_start, self.target_end
        s = max(0, s); e = max(s, min(len(self.text), e))
        self.text = self.text[:s] + t + self.text[e:]
        self.target_end = s + len(t)
    def InsertText(self, p, t):
        self._snap()
        p = max(0, min(len(self.text), p))
        self.text = self.text[:p] + t + self.text[p:]
    def DeleteRange(self, p, length):
        self._snap()
        p = max(0, min(len(self.text), p))
        self.text = self.text[:p] + self.text[p + length:]

    def BraceMatch(self, p):
        if not (0 <= p < len(self.text)): return -1
        ch = self.text[p]
        pairs = {'(':')', '[':']', '{':'}', ')':'(', ']':'[', '}':'{'}
        if ch not in pairs: return -1
        match = pairs[ch]
        forward = ch in '([{'
        depth = 1
        i = p + (1 if forward else -1)
        while 0 <= i < len(self.text):
            if self.text[i] == ch:    depth += 1
            elif self.text[i] == match: depth -= 1
            if depth == 0: return i
            i += 1 if forward else -1
        return -1

    def WordStartPosition(self, p, only_word_chars=True):
        while p > 0 and (self.text[p - 1].isalnum() or self.text[p - 1] == '_'):
            p -= 1
        return p
    def WordEndPosition(self, p, only_word_chars=True):
        while p < len(self.text) and (self.text[p].isalnum() or self.text[p] == '_'):
            p += 1
        return p


# ---------------------------------------------------------------- import ViMode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vi_mode import ViMode, NORMAL, INSERT, VISUAL, V_LINE, COMMAND  # noqa: E402


# ---------------------------------------------------------------- key driver

def _keycode_for(ch):
    """Approximate the wxPython EVT_KEY_DOWN keycode for a 1-char key."""
    if ch.isalpha():
        return ord(ch.upper())
    return ord(ch)


def send_key(vi, key, ctrl=False, alt=False, shift=False, raw=False):
    """Send a key through the full event chain.

    ``key`` may be a 1-char str ('h'), a longer mnemonic ('Esc', 'Enter',
    'BS', 'Up', 'F12'), or an int keycode if ``raw=True``.
    """
    mnemonics = {
        'Esc': _mock_wx.WXK_ESCAPE, 'Enter': _mock_wx.WXK_RETURN,
        'BS': _mock_wx.WXK_BACK, 'F12': _mock_wx.WXK_F12,
        'Left': _mock_wx.WXK_LEFT, 'Right': _mock_wx.WXK_RIGHT,
        'Up': _mock_wx.WXK_UP, 'Down': _mock_wx.WXK_DOWN,
    }
    if raw:
        kc = key; uc = key
    elif isinstance(key, str) and key in mnemonics:
        kc = mnemonics[key]; uc = 0
    elif isinstance(key, str) and len(key) == 1:
        kc = _keycode_for(key); uc = ord(key)
    else:
        raise ValueError('bad key: %r' % (key,))

    evt = _MockEvent(key=kc, unicode_key=uc, ctrl=ctrl, alt=alt, shift=shift)
    vi.on_key_down(evt)
    if evt.skipped and 32 <= uc <= 126:
        char_evt = _MockEvent(key=uc, unicode_key=uc, ctrl=ctrl, alt=alt, shift=shift)
        vi.on_char(char_evt)


def keys(vi, *seq):
    """Send a sequence: each item is either a 1-char str (chars), or a tuple
    ('mnemonic', kw...) e.g. ('Esc',), or ('r', {'ctrl': True}) for Ctrl-R."""
    for item in seq:
        if isinstance(item, tuple):
            k = item[0]
            kw = item[1] if len(item) > 1 else {}
            send_key(vi, k, **kw)
        elif len(item) == 1:
            send_key(vi, item)
        else:
            send_key(vi, item)


def make_vi(text="", autosent=True):
    ed = FakeEditor(text)
    status = []
    ex_calls = []
    vi = ViMode(ed,
                status_callback=lambda m: status.append(m),
                ex_handler=lambda c: ex_calls.append(c))
    return vi, ed, status, ex_calls


# ---------------------------------------------------------------- tests

TESTS = []
def test(fn):
    TESTS.append(fn)
    return fn


@test
def t_initial_state():
    vi, ed, status, _ = make_vi("hello")
    assert vi.enabled is True, "vi should be enabled by default"
    assert vi.mode == NORMAL, vi.mode
    assert any('NORMAL' in s for s in status), status

@test
def t_basic_hjkl():
    vi, ed, _, _ = make_vi("abcdef")
    keys(vi, 'l', 'l', 'l')
    assert ed.pos == 3, ed.pos
    keys(vi, 'h')
    assert ed.pos == 2, ed.pos

@test
def t_jk_lines():
    vi, ed, _, _ = make_vi("abc\ndef\nghi")
    keys(vi, 'l', 'j')              # col=1 line=1 -> pos=5
    assert ed.pos == 5, ed.pos
    keys(vi, 'k')
    assert ed.pos == 1, ed.pos

@test
def t_word_w():
    vi, ed, _, _ = make_vi("hello world foo")
    keys(vi, 'w')
    assert ed.pos == 6, ed.pos
    keys(vi, 'w')
    assert ed.pos == 12, ed.pos

@test
def t_word_b():
    vi, ed, _, _ = make_vi("hello world")
    ed.GotoPos(8)
    keys(vi, 'b')
    assert ed.pos == 6, ed.pos

@test
def t_line_dollar():
    vi, ed, _, _ = make_vi("hello world")
    keys(vi, '$')
    # NORMAL $: last char of line (not newline); buffer is single line, last char idx 10
    assert ed.pos == 10, ed.pos

@test
def t_line_zero():
    vi, ed, _, _ = make_vi("hello")
    keys(vi, '$', '0')
    assert ed.pos == 0, ed.pos

@test
def t_doc_gg_G():
    vi, ed, _, _ = make_vi("a\nb\nc\nd")
    keys(vi, 'G')
    assert ed.pos == 6, ed.pos      # last line 'd', pos at 'd'
    keys(vi, 'g', 'g')
    assert ed.pos == 0, ed.pos

@test
def t_count_motion():
    vi, ed, _, _ = make_vi("0123456789")
    keys(vi, '5', 'l')
    assert ed.pos == 5, ed.pos

@test
def t_insert_then_esc():
    vi, ed, _, _ = make_vi("abc")
    keys(vi, 'i')
    assert vi.mode == INSERT
    keys(vi, ('Esc',))
    assert vi.mode == NORMAL

@test
def t_append_a():
    vi, ed, _, _ = make_vi("ab")
    keys(vi, 'a')
    assert ed.pos == 1, ed.pos     # 'a' moves caret one right
    assert vi.mode == INSERT

@test
def t_open_o():
    vi, ed, _, _ = make_vi("abc\ndef")
    keys(vi, 'o')
    assert vi.mode == INSERT
    # caret should be on a new line below "abc"
    assert ed.text.startswith("abc\n"), ed.text
    assert ed.pos > 3, ed.pos

@test
def t_x_delete_char():
    vi, ed, _, _ = make_vi("hello")
    keys(vi, 'l', 'x')
    assert ed.text == "hllo", ed.text

@test
def t_dd_delete_line():
    vi, ed, _, _ = make_vi("a\nb\nc")
    keys(vi, 'd', 'd')
    assert ed.text == "b\nc", ed.text

@test
def t_dw_delete_word():
    vi, ed, _, _ = make_vi("hello world")
    keys(vi, 'd', 'w')
    assert ed.text == "world", ed.text

@test
def t_yy_p_paste_line():
    vi, ed, _, _ = make_vi("aaa\nbbb")
    keys(vi, 'y', 'y', 'p')
    assert ed.text == "aaa\naaa\nbbb", ed.text

@test
def t_x_then_p():
    vi, ed, _, _ = make_vi("abc")
    keys(vi, 'x', 'p')              # cut 'a', paste after 'b' -> "bac"
    assert ed.text == "bac", ed.text

@test
def t_visual_y():
    vi, ed, _, _ = make_vi("hello")
    keys(vi, 'v', 'l', 'l', 'y')
    assert vi.operators.register == "hel", repr(vi.operators.register)

@test
def t_visual_d():
    vi, ed, _, _ = make_vi("hello world")
    keys(vi, 'v', 'l', 'l', 'l', 'l', 'd')
    assert ed.text == " world", ed.text

@test
def t_undo_redo():
    vi, ed, _, _ = make_vi("hello")
    keys(vi, 'x')
    assert ed.text == "ello"
    keys(vi, 'u')
    assert ed.text == "hello", ed.text
    keys(vi, ('r', {'ctrl': True}))
    assert ed.text == "ello", ed.text

@test
def t_replace_r():
    vi, ed, _, _ = make_vi("cat")
    keys(vi, 'r', 'b')
    assert ed.text == "bat", ed.text

@test
def t_count_x():
    vi, ed, _, _ = make_vi("hello")
    keys(vi, '3', 'x')
    assert ed.text == "lo", ed.text

@test
def t_search_slash():
    vi, ed, _, _ = make_vi("foo bar baz bar")
    keys(vi, '/', 'b', 'a', 'r', ('Enter',))
    assert ed.pos == 4, ed.pos
    keys(vi, 'n')
    assert ed.pos == 12, ed.pos

@test
def t_substitute():
    vi, ed, _, _ = make_vi("apple banana apple")
    # :%s/apple/orange/g
    for c in ":%s/apple/orange/g":
        send_key(vi, c)
    send_key(vi, 'Enter')
    assert ed.text == "orange banana orange", ed.text

@test
def t_ex_w_routes_to_handler():
    vi, ed, _, ex = make_vi("foo")
    for c in ":w":
        send_key(vi, c)
    send_key(vi, 'Enter')
    assert ex == ['w'], ex

@test
def t_f12_disables():
    vi, ed, _, _ = make_vi("abc")
    assert vi.enabled
    send_key(vi, 'F12')
    assert not vi.enabled
    send_key(vi, 'F12')
    assert vi.enabled

@test
def t_change_word_cw():
    vi, ed, _, _ = make_vi("hello world")
    keys(vi, 'c', 'w')
    assert vi.mode == INSERT
    assert ed.text == " world", ed.text   # 'hello' deleted

@test
def t_count_dd():
    vi, ed, _, _ = make_vi("a\nb\nc\nd")
    keys(vi, '2', 'd', 'd')
    assert ed.text == "c\nd", ed.text


# ---------------------------------------------------------------- runner

def run(pattern=None):
    selected = [t for t in TESTS if pattern is None or pattern in t.__name__]
    fails, errors = 0, 0
    for t in selected:
        try:
            t()
            print('PASS', t.__name__)
        except AssertionError as e:
            fails += 1
            print('FAIL', t.__name__, '-', e)
        except Exception as e:
            errors += 1
            import traceback
            print('ERROR', t.__name__, '-', type(e).__name__, e)
            traceback.print_exc()
    total = len(selected)
    passed = total - fails - errors
    print('\n%d/%d passed (%d fail, %d error)' % (passed, total, fails, errors))
    return fails + errors


if __name__ == '__main__':
    pat = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(0 if run(pat) == 0 else 1)

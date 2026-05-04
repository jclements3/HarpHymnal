"""Vi motion library for wx.stc.StyledTextCtrl.

Each motion method returns a target caret position (int). Methods do not
move the caret themselves; the caller is expected to call editor.GotoPos().
"""

import string


_WORD_CHARS = set(string.ascii_letters + string.digits + "_")


def _char_class(ch):
    """Return 0 (whitespace), 1 (word: alnum/underscore), or 2 (punctuation).

    Empty string and newlines count as whitespace for word-motion purposes.
    """
    if ch == "" or ch.isspace():
        return 0
    if ch in _WORD_CHARS:
        return 1
    return 2


def _big_class(ch):
    """Big-word class: 0 whitespace, 1 non-whitespace."""
    if ch == "" or ch.isspace():
        return 0
    return 1


class Motions:
    """Vi-style motion primitives over a Scintilla editor."""

    def __init__(self, editor):
        self.editor = editor

    def _char(self, pos):
        if pos < 0 or pos >= self.editor.GetTextLength():
            return ""
        code = self.editor.GetCharAt(pos)
        if code <= 0:
            return ""
        try:
            return chr(code)
        except ValueError:
            return ""

    def _line_of(self, pos):
        return self.editor.LineFromPosition(pos)

    def _line_bounds(self, line):
        start = self.editor.PositionFromLine(line)
        end = self.editor.GetLineEndPosition(line)
        return start, end

    def _column(self, pos):
        return pos - self.editor.PositionFromLine(self._line_of(pos))

    def _goto_column(self, line, col):
        start, end = self._line_bounds(line)
        if end <= start:
            return start
        max_col = end - start - 1
        return start + min(col, max(0, max_col))

    def _first_nonblank_of_line(self, line):
        if line < 0:
            line = 0
        last = self.editor.GetLineCount() - 1
        if line > last:
            line = last
        start, end = self._line_bounds(line)
        p = start
        while p < end:
            c = self._char(p)
            if c == "" or not c.isspace():
                return p
            p += 1
        return start

    def left(self, n):
        """h. Move n chars left, clamped to start of current line."""
        pos = self.editor.GetCurrentPos()
        line_start = self.editor.PositionFromLine(self._line_of(pos))
        return max(line_start, pos - n)

    def right(self, n, allow_past_eol=False):
        """l. Move n chars right, clamped per NORMAL/INSERT rule."""
        pos = self.editor.GetCurrentPos()
        line = self._line_of(pos)
        start, end = self._line_bounds(line)
        if allow_past_eol:
            limit = end
        else:
            limit = start if end <= start else end - 1
        return min(limit, pos + n)

    def up(self, n):
        """k. Move up n lines, preserving column."""
        pos = self.editor.GetCurrentPos()
        line = self._line_of(pos)
        col = self._column(pos)
        target_line = max(0, line - n)
        return self._goto_column(target_line, col)

    def down(self, n):
        """j. Move down n lines, preserving column."""
        pos = self.editor.GetCurrentPos()
        line = self._line_of(pos)
        col = self._column(pos)
        last = self.editor.GetLineCount() - 1
        target_line = min(last, line + n)
        return self._goto_column(target_line, col)

    def word_forward(self, n, big=False):
        """w / W. Start of next word."""
        cls = _big_class if big else _char_class
        pos = self.editor.GetCurrentPos()
        end = self.editor.GetTextLength()
        for _ in range(n):
            if pos >= end:
                break
            cur = cls(self._char(pos))
            if cur != 0:
                while pos < end and cls(self._char(pos)) == cur:
                    pos += 1
            while pos < end and cls(self._char(pos)) == 0:
                pos += 1
        return min(pos, end)

    def word_backward(self, n, big=False):
        """b / B. Start of current word, or previous word if at start."""
        cls = _big_class if big else _char_class
        pos = self.editor.GetCurrentPos()
        for _ in range(n):
            if pos <= 0:
                break
            pos -= 1
            while pos > 0 and cls(self._char(pos)) == 0:
                pos -= 1
            cur = cls(self._char(pos))
            if cur == 0:
                break
            while pos > 0 and cls(self._char(pos - 1)) == cur:
                pos -= 1
        return max(0, pos)

    def word_end(self, n, big=False):
        """e / E. End of current word, or next word's end if already at end."""
        cls = _big_class if big else _char_class
        pos = self.editor.GetCurrentPos()
        end = self.editor.GetTextLength()
        if end <= 0:
            return 0
        for _ in range(n):
            if pos >= end - 1:
                pos = end - 1
                break
            pos += 1
            while pos < end and cls(self._char(pos)) == 0:
                pos += 1
            if pos >= end:
                pos = end - 1
                break
            cur = cls(self._char(pos))
            while pos + 1 < end and cls(self._char(pos + 1)) == cur:
                pos += 1
        return min(pos, end - 1)

    def line_start(self):
        """0 - column 0 of current line."""
        pos = self.editor.GetCurrentPos()
        return self.editor.PositionFromLine(self._line_of(pos))

    def first_nonblank(self):
        """^ - first non-whitespace char of current line."""
        pos = self.editor.GetCurrentPos()
        return self._first_nonblank_of_line(self._line_of(pos))

    def line_end(self, allow_past_eol=False):
        """$ - last char (NORMAL) or newline position (allow_past_eol)."""
        pos = self.editor.GetCurrentPos()
        line = self._line_of(pos)
        start, end = self._line_bounds(line)
        if allow_past_eol:
            return end
        if end <= start:
            return start
        return end - 1

    def doc_start(self, n=1):
        """gg - first non-blank of line n (1-based)."""
        return self._first_nonblank_of_line(max(1, n) - 1)

    def doc_end(self, n=0):
        """G - first non-blank of line n; n=0 means last line."""
        last = self.editor.GetLineCount() - 1
        if n <= 0:
            line = last
        else:
            line = min(last, n - 1)
        return self._first_nonblank_of_line(line)

    def match_brace(self):
        """% - matching brace; try one char right if not on a brace."""
        pos = self.editor.GetCurrentPos()
        match = self.editor.BraceMatch(pos)
        if match >= 0:
            return match
        line = self._line_of(pos)
        _, end = self._line_bounds(line)
        if pos + 1 < end:
            match = self.editor.BraceMatch(pos + 1)
            if match >= 0:
                return match
        return pos

    def find_char(self, ch, forward, before):
        """f / F / t / T. Search current line only."""
        if not ch:
            return self.editor.GetCurrentPos()
        pos = self.editor.GetCurrentPos()
        line = self._line_of(pos)
        start, end = self._line_bounds(line)
        if forward:
            p = pos + 1
            while p < end:
                if self._char(p) == ch:
                    return p - 1 if before else p
                p += 1
        else:
            p = pos - 1
            while p >= start:
                if self._char(p) == ch:
                    return p + 1 if before else p
                p -= 1
        return pos

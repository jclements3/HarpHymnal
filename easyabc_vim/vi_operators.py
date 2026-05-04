"""vi-mode operators for wx.stc.StyledTextCtrl (Scintilla).

Implements d/c/y/p/P/r/~ against a Scintilla editor. Pure Python, stdlib only.
The dispatcher composes these with motions; this module owns the unnamed
register and the linewise flag.
"""


class Operators:
    def __init__(self, editor):
        self.editor = editor
        self.register = ""
        self.register_linewise = False

    # ------------------------------------------------------------------ helpers

    def _clamp(self, pos):
        if pos < 0:
            return 0
        n = self.editor.GetTextLength()
        if pos > n:
            return n
        return pos

    def _normalize(self, start, end):
        if start > end:
            start, end = end, start
        return self._clamp(start), self._clamp(end)

    def _expand_linewise(self, start, end):
        """Expand a [start, end) range to whole lines.

        end is treated as exclusive; we look at the last *included* line via
        end - 1 so a range ending exactly at a line boundary doesn't swallow
        the next line. The trailing newline is included so paste-below works
        naturally.
        """
        ed = self.editor
        start, end = self._normalize(start, end)
        if end == start:
            last_line_pos = start
        else:
            last_line_pos = end - 1
        first_line = ed.LineFromPosition(start)
        last_line = ed.LineFromPosition(last_line_pos)
        new_start = ed.PositionFromLine(first_line)
        new_end = ed.GetLineEndPosition(last_line) + 1  # +1 for the newline
        new_end = self._clamp(new_end)
        return new_start, new_end

    def _first_nonblank(self, line):
        ed = self.editor
        if line < 0:
            line = 0
        if line >= ed.GetLineCount():
            line = ed.GetLineCount() - 1
        line_start = ed.PositionFromLine(line)
        line_end = ed.GetLineEndPosition(line)
        pos = line_start
        while pos < line_end:
            ch = ed.GetCharAt(pos)
            # space (0x20) or tab (0x09)
            if ch != 0x20 and ch != 0x09:
                return pos
            pos += 1
        return line_start

    def _replace(self, start, end, text):
        ed = self.editor
        ed.SetTargetStart(start)
        ed.SetTargetEnd(end)
        ed.ReplaceTarget(text)

    # ------------------------------------------------------------------ d / c / y

    def delete(self, start: int, end: int, linewise: bool = False) -> int:
        """`d`-motion. Delete [start, end); yank into register.

        If linewise, expand to whole lines (consuming the trailing newline)
        and place caret at first-nonblank of the resulting line.
        """
        ed = self.editor
        start, end = self._normalize(start, end)
        if linewise:
            start, end = self._expand_linewise(start, end)
        if start == end:
            self.register_linewise = linewise
            return self._clamp(start)
        self.register = ed.GetTextRange(start, end)
        self.register_linewise = linewise
        ed.BeginUndoAction()
        try:
            self._replace(start, end, "")
        finally:
            ed.EndUndoAction()
        if linewise:
            line = ed.LineFromPosition(start)
            if line >= ed.GetLineCount():
                line = ed.GetLineCount() - 1
            new_pos = self._first_nonblank(line)
        else:
            new_pos = start
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

    def change(self, start: int, end: int, linewise: bool = False) -> int:
        """`c`-motion. Like delete, but linewise leaves an empty line behind.

        Caller is responsible for entering insert mode.
        """
        ed = self.editor
        start, end = self._normalize(start, end)
        if linewise:
            start, end = self._expand_linewise(start, end)
        if start == end and not linewise:
            self.register_linewise = linewise
            return self._clamp(start)
        self.register = ed.GetTextRange(start, end)
        self.register_linewise = linewise
        ed.BeginUndoAction()
        try:
            self._replace(start, end, "")
            if linewise:
                ed.InsertText(start, "\n")
                new_pos = start
            else:
                new_pos = start
        finally:
            ed.EndUndoAction()
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

    def yank(self, start: int, end: int, linewise: bool = False) -> int:
        """`y`-motion. Copy range into register; do not modify buffer.

        Caret returns to min(start, end) per vim convention.
        """
        ed = self.editor
        orig_start, _ = self._normalize(start, end)
        if linewise:
            r_start, r_end = self._expand_linewise(start, end)
        else:
            r_start, r_end = self._normalize(start, end)
        self.register = ed.GetTextRange(r_start, r_end)
        self.register_linewise = linewise
        ed.GotoPos(self._clamp(orig_start))
        return ed.GetCurrentPos()

    # ------------------------------------------------------------------ p / P

    def paste_after(self, count: int = 1) -> int:
        """`p`. Insert register `count` times after caret (or below for linewise)."""
        ed = self.editor
        if not self.register or count < 1:
            return ed.GetCurrentPos()
        text = self.register * count
        pos = ed.GetCurrentPos()
        ed.BeginUndoAction()
        try:
            if self.register_linewise:
                line = ed.LineFromPosition(pos)
                line_end = ed.GetLineEndPosition(line)
                total = ed.GetTextLength()
                if line_end >= total:
                    # last line with no trailing newline: prepend a newline
                    payload = "\n" + (text[:-1] if text.endswith("\n") else text)
                    ed.InsertText(total, payload)
                    new_line = line + 1
                else:
                    ed.InsertText(line_end + 1, text)
                    new_line = line + 1
                if new_line >= ed.GetLineCount():
                    new_line = ed.GetLineCount() - 1
                new_pos = self._first_nonblank(new_line)
            else:
                line = ed.LineFromPosition(pos)
                line_end = ed.GetLineEndPosition(line)
                if pos >= ed.GetTextLength():
                    insert_at = pos
                elif pos >= line_end:
                    insert_at = pos
                else:
                    insert_at = pos + 1
                ed.InsertText(insert_at, text)
                new_pos = insert_at + len(text) - 1
        finally:
            ed.EndUndoAction()
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

    def paste_before(self, count: int = 1) -> int:
        """`P`. Insert register `count` times before caret (or above for linewise)."""
        ed = self.editor
        if not self.register or count < 1:
            return ed.GetCurrentPos()
        text = self.register * count
        pos = ed.GetCurrentPos()
        ed.BeginUndoAction()
        try:
            if self.register_linewise:
                line = ed.LineFromPosition(pos)
                insert_at = ed.PositionFromLine(line)
                ed.InsertText(insert_at, text)
                new_pos = self._first_nonblank(line)
            else:
                ed.InsertText(pos, text)
                new_pos = pos + len(text) - 1
        finally:
            ed.EndUndoAction()
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

    # ------------------------------------------------------------------ r / ~

    def replace_char(self, ch: str, n: int) -> int:
        """`r{ch}`. Replace n chars with `ch`, capped at end of line."""
        ed = self.editor
        if n < 1 or not ch:
            return ed.GetCurrentPos()
        pos = ed.GetCurrentPos()
        line = ed.LineFromPosition(pos)
        line_end = ed.GetLineEndPosition(line)
        remaining = line_end - pos
        if remaining <= 0:
            return pos
        n = min(n, remaining)
        replacement = ch * n
        ed.BeginUndoAction()
        try:
            self._replace(pos, pos + n, replacement)
        finally:
            ed.EndUndoAction()
        new_pos = pos + n - 1
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

    def toggle_case(self, n: int) -> int:
        """`~`. Toggle case of n chars; skip non-letters; don't cross newline."""
        ed = self.editor
        if n < 1:
            return ed.GetCurrentPos()
        pos = ed.GetCurrentPos()
        line = ed.LineFromPosition(pos)
        line_end = ed.GetLineEndPosition(line)
        remaining = line_end - pos
        if remaining <= 0:
            return pos
        n = min(n, remaining)
        original = ed.GetTextRange(pos, pos + n)
        toggled_chars = []
        for c in original:
            if c.isalpha():
                if c.islower():
                    toggled_chars.append(c.upper())
                else:
                    toggled_chars.append(c.lower())
            else:
                toggled_chars.append(c)
        toggled = "".join(toggled_chars)
        ed.BeginUndoAction()
        try:
            if toggled != original:
                self._replace(pos, pos + n, toggled)
        finally:
            ed.EndUndoAction()
        new_pos = pos + n
        if new_pos > line_end:
            new_pos = line_end
        ed.GotoPos(self._clamp(new_pos))
        return ed.GetCurrentPos()

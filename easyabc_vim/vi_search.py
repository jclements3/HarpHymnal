"""vi-style search and substitute for a wx.stc.StyledTextCtrl editor.

This module is intentionally free of any wx imports; it talks to the editor
solely through the Scintilla API surface listed below. The dispatcher module
owns caret movement and user feedback; this class only computes positions
and performs buffer mutations for `:s` / `:%s` commands.

Editor methods used:
    GetCurrentPos, GetText, SetText, GetTextLength,
    LineFromPosition, PositionFromLine, GetLineEndPosition,
    SetTargetStart, SetTargetEnd, ReplaceTarget,
    BeginUndoAction, EndUndoAction
"""


class Search:
    def __init__(self, editor):
        self.editor = editor
        self.last_term = ""
        self.last_backward = False

    # ------------------------------------------------------------------ search

    def search(self, term, backward, from_pos=None):
        """Plain-text, case-sensitive search with wrap-around.

        Returns the absolute buffer position of a match, or -1 if not found.
        Does not move the caret. Updates last_term / last_backward.
        """
        # Always remember the request, even on empty term, so that `n` after
        # a failed search still behaves predictably (returns -1).
        self.last_term = term
        self.last_backward = backward

        if not term:
            return -1

        text = self.editor.GetText()
        text_len = len(text)
        if text_len == 0:
            return -1

        caret = self.editor.GetCurrentPos()
        if from_pos is None:
            start = caret + 1 if not backward else caret - 1
        else:
            start = from_pos

        # Clamp to valid range so the slice arithmetic below is well-defined.
        if start < 0:
            start = 0
        if start > text_len:
            start = text_len

        if backward:
            # First pass: [0, start). rfind treats the end index exclusively.
            idx = text.rfind(term, 0, start)
            if idx != -1:
                return idx
            # Wrap: search the rest of the buffer [start, end).
            idx = text.rfind(term, start, text_len)
            return idx
        else:
            # First pass: [start, end).
            idx = text.find(term, start, text_len)
            if idx != -1:
                return idx
            # Wrap: [0, start). The pattern may straddle this boundary in
            # principle but for line-oriented vi search the simple split is
            # the conventional behavior.
            idx = text.find(term, 0, start)
            return idx

    # ------------------------------------------------------------------ repeat

    def repeat(self, reverse=False):
        """Re-run last search. `reverse` flips direction (vi `N`)."""
        if not self.last_term:
            return -1
        backward = self.last_backward
        if reverse:
            backward = not backward
        # Don't mutate last_backward when N is pressed: vi semantics keep the
        # original direction of the last `/` or `?` for subsequent `n`.
        saved_backward = self.last_backward
        pos = self.search(self.last_term, backward)
        self.last_backward = saved_backward
        return pos

    # -------------------------------------------------------------- substitute

    def substitute(self, cmd):
        """Execute `s/pat/rep/[g]` or `%s/pat/rep/[g]`.

        Returns the number of replacements performed, or -1 on parse error.
        """
        if not cmd:
            return -1

        whole_buffer = False
        rest = cmd
        if rest.startswith("%"):
            whole_buffer = True
            rest = rest[1:]

        if not rest.startswith("s/"):
            return -1
        rest = rest[2:]  # drop the leading 's/'

        # Split into at most three pieces: pattern, replacement, flags.
        # An empty replacement (e.g. 's/foo//') must be allowed.
        parts = rest.split("/")
        if len(parts) < 2:
            return -1
        pat = parts[0]
        rep = parts[1]
        flags = parts[2] if len(parts) >= 3 else ""
        # Any extra trailing slashes/segments are a parse error.
        if len(parts) > 3:
            return -1
        if not pat:
            return -1

        global_flag = "g" in flags
        # Reject unknown flags so typos surface instead of silently no-oping.
        for ch in flags:
            if ch != "g":
                return -1

        if whole_buffer:
            return self._sub_buffer(pat, rep, global_flag)
        return self._sub_line(pat, rep, global_flag)

    # ------------------------------------------------------------- sub helpers

    def _sub_buffer(self, pat, rep, global_flag):
        text = self.editor.GetText()
        lines = text.split("\n")
        total = 0
        new_lines = []
        for line in lines:
            if global_flag:
                count = line.count(pat)
                if count:
                    line = line.replace(pat, rep)
                    total += count
            else:
                idx = line.find(pat)
                if idx != -1:
                    line = line[:idx] + rep + line[idx + len(pat):]
                    total += 1
            new_lines.append(line)

        if total > 0:
            new_text = "\n".join(new_lines)
            self.editor.BeginUndoAction()
            try:
                self.editor.SetText(new_text)
            finally:
                self.editor.EndUndoAction()
        return total

    def _sub_line(self, pat, rep, global_flag):
        editor = self.editor
        line_no = editor.LineFromPosition(editor.GetCurrentPos())
        line_start = editor.PositionFromLine(line_no)
        line_end = editor.GetLineEndPosition(line_no)

        # Reach into the buffer for just this line's text.
        text = editor.GetText()
        line_text = text[line_start:line_end]

        if global_flag:
            count = line_text.count(pat)
            if count == 0:
                return 0
            new_line = line_text.replace(pat, rep)
        else:
            idx = line_text.find(pat)
            if idx == -1:
                return 0
            new_line = line_text[:idx] + rep + line_text[idx + len(pat):]
            count = 1

        editor.BeginUndoAction()
        try:
            editor.SetTargetStart(line_start)
            editor.SetTargetEnd(line_end)
            editor.ReplaceTarget(new_line)
        finally:
            editor.EndUndoAction()
        return count

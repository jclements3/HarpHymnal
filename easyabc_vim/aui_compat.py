"""Monkeypatch wx.lib.agw.aui.auibar.AuiDefaultToolBarArt.DrawSeparator
to use integer division. The shipped method does ``rect.x += rect.width/2``
which crashes the paint loop on Py3/wxPython 4.x because wx.Rect coords
must be int. Faithful re-implementation of the upstream method with `/`
swapped for `//`.
"""

try:
    import wx
    from wx.lib.agw.aui import auibar as _auibar
    from wx.lib.agw.aui.aui_utilities import StepColour as _StepColour

    def _draw_separator_int(self, dc, wnd, _rect):
        horizontal = True
        if self._agwFlags & _auibar.AUI_TB_VERTICAL:
            horizontal = False

        rect = wx.Rect(*_rect)

        if horizontal:
            rect.x += rect.width // 2
            rect.width = 1
            new_height = (rect.height * 3) // 4
            rect.y += (rect.height // 2) - (new_height // 2)
            rect.height = new_height
        else:
            rect.y += rect.height // 2
            rect.height = 1
            new_width = (rect.width * 3) // 4
            rect.x += (rect.width // 2) - (new_width // 2)
            rect.width = new_width

        start_colour = _StepColour(self._base_colour, 80)
        end_colour = _StepColour(self._base_colour, 80)
        direction = wx.SOUTH if horizontal else wx.EAST
        dc.GradientFillLinear(rect, start_colour, end_colour, direction)

    _auibar.AuiDefaultToolBarArt.DrawSeparator = _draw_separator_int
except Exception as _e:
    print('aui_compat: monkeypatch failed:', _e)

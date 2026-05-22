"""
Desktop Tool — Fully Custom Painted wxPython
Toàn bộ UI vẽ tay bằng wx.GraphicsContext

Author: lamngocchien
Repository: https://github.com/lamngocchien/beautiful-wxpython
Created: May 2026
"""
import wx
import wx.lib.scrolledpanel as scrolled

# ══════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════
class T:
    BG          = wx.Colour(13,  17,  23)
    SIDEBAR     = wx.Colour(22,  27,  34)
    CARD        = wx.Colour(30,  38,  48)
    CARD2       = wx.Colour(38,  48,  60)
    BORDER      = wx.Colour(48,  60,  76)
    ACCENT      = wx.Colour(88,  166, 255)   # blue
    ACCENT2     = wx.Colour(63,  207, 142)   # green
    ACCENT3     = wx.Colour(210, 153, 255)   # purple
    ACCENT4     = wx.Colour(255, 166,  77)   # orange
    TEXT        = wx.Colour(230, 237, 243)
    TEXT2       = wx.Colour(139, 148, 158)
    TEXT3       = wx.Colour(72,  82,  94)
    SUCCESS     = wx.Colour(63,  207, 142)
    ERROR       = wx.Colour(255, 100, 100)
    WARNING     = wx.Colour(255, 200,  80)
    HOVER       = wx.Colour(33,  41,  52)
    SEL         = wx.Colour(22,  43,  70)

    @staticmethod
    def font(size=10, bold=False):
        w = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, w)

    @staticmethod
    def gcfont(gc, size=10, bold=False, color=None):
        return gc.CreateFont(T.font(size, bold), color or T.TEXT)


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def rounded_rect(gc, x, y, w, h, r, fill=None, stroke=None, stroke_w=1):
    if fill:
        gc.SetBrush(wx.Brush(fill))
    else:
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
    if stroke:
        gc.SetPen(wx.Pen(stroke, stroke_w))
    else:
        gc.SetPen(wx.TRANSPARENT_PEN)
    gc.DrawRoundedRectangle(x, y, w, h, r)

def draw_text(gc, text, x, y, size=10, bold=False, color=None):
    gc.SetFont(T.gcfont(gc, size, bold, color or T.TEXT))
    gc.DrawText(text, x, y)

def text_center(gc, text, x, y, w, h, size=10, bold=False, color=None):
    gc.SetFont(T.gcfont(gc, size, bold, color or T.TEXT))
    tw, th = gc.GetTextExtent(text)
    gc.DrawText(text, x + (w - tw) / 2, y + (h - th) / 2)


# ══════════════════════════════════════════════
#  BASE PANEL (transparent-friendly)
# ══════════════════════════════════════════════
class BasePanel(wx.Panel):
    def __init__(self, parent, bg=None):
        super().__init__(parent, style=wx.NO_BORDER)
        self.bg = bg or T.BG
        self.SetBackgroundColour(self.bg)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._base_paint)
        self.Bind(wx.EVT_SIZE,  lambda e: (e.Skip(), self.Refresh()))

    def _base_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(self.bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        self.on_paint(gc, w, h)

    def on_paint(self, gc, w, h):
        pass


# ══════════════════════════════════════════════
#  NAV ITEM
# ══════════════════════════════════════════════
class NavItem(wx.Panel):
    def __init__(self, parent, label, icon_char, index, callback):
        super().__init__(parent, size=(-1, 44), style=wx.NO_BORDER)
        self.label    = label
        self.icon     = icon_char
        self.index    = index
        self.callback = callback
        self.selected = False
        self.hovered  = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_PAINT,        self._paint)
        self.Bind(wx.EVT_LEFT_DOWN,    self._click)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self._hover(True))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._hover(False))
        self.Bind(wx.EVT_SIZE,         lambda e: (e.Skip(), self.Refresh()))

    def _hover(self, v):
        self.hovered = v; self.Refresh()

    def _click(self, e):
        self.callback(self.index)

    def set_selected(self, v):
        self.selected = v; self.Refresh()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        # background
        if self.selected:
            bg = T.SEL
        elif self.hovered:
            bg = T.HOVER
        else:
            bg = T.SIDEBAR
        gc.SetBrush(wx.Brush(bg)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # accent bar
        if self.selected:
            gc.SetBrush(wx.Brush(T.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRoundedRectangle(0, 8, 3, h-16, 2)

        # icon
        ic = T.ACCENT if self.selected else T.TEXT2
        gc.SetFont(T.gcfont(gc, 13, False, ic))
        iw, ih = gc.GetTextExtent(self.icon)
        gc.DrawText(self.icon, 18, (h - ih) / 2)

        # label
        lc = T.TEXT if self.selected else T.TEXT2
        gc.SetFont(T.gcfont(gc, 10, self.selected, lc))
        _, lh = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, 44, (h - lh) / 2)


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
PAGES = [
    ("Dashboard", "⬛"),
    ("Files",     "📁"),
    ("Reports",   "📊"),
    ("Tools",     "🔧"),
    ("Settings",  "⚙"),
    ("About",     "ℹ"),
]

class Sidebar(BasePanel):
    def __init__(self, parent, on_nav):
        super().__init__(parent, T.SIDEBAR)
        self.on_nav   = on_nav
        self.items    = []
        self.SetMinSize((200, -1))

        outer = wx.BoxSizer(wx.VERTICAL)

        # logo zone (painted separately)
        self.logo_zone = wx.Panel(self, size=(-1, 64), style=wx.NO_BORDER)
        self.logo_zone.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.logo_zone.Bind(wx.EVT_PAINT, self._paint_logo)
        outer.Add(self.logo_zone, 0, wx.EXPAND)

        # divider
        div = wx.Panel(self, size=(-1, 1), style=wx.NO_BORDER)
        div.SetBackgroundColour(T.BORDER); outer.Add(div, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        outer.AddSpacer(6)

        # nav items
        for i, (label, icon) in enumerate(PAGES):
            item = NavItem(self, label, icon, i, self._on_item)
            self.items.append(item)
            outer.Add(item, 0, wx.EXPAND)

        outer.AddStretchSpacer()

        # divider
        div2 = wx.Panel(self, size=(-1, 1), style=wx.NO_BORDER)
        div2.SetBackgroundColour(T.BORDER); outer.Add(div2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        # user zone
        self.user_zone = wx.Panel(self, size=(-1, 58), style=wx.NO_BORDER)
        self.user_zone.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.user_zone.Bind(wx.EVT_PAINT, self._paint_user)
        outer.Add(self.user_zone, 0, wx.EXPAND)

        self.SetSizer(outer)
        self.select(0)

    def _paint_logo(self, event):
        dc = wx.AutoBufferedPaintDC(self.logo_zone)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.logo_zone.GetSize()
        gc.SetBrush(wx.Brush(T.SIDEBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # circle logo
        gc.SetBrush(wx.Brush(T.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawEllipse(16, 18, 28, 28)
        gc.SetFont(T.gcfont(gc, 11, True, T.BG))
        tw, th = gc.GetTextExtent("M")
        gc.DrawText("M", 16 + (28-tw)/2, 18 + (28-th)/2)

        # app name
        gc.SetFont(T.gcfont(gc, 12, True, T.TEXT))
        gc.DrawText("MyTool", 52, 22)
        gc.SetFont(T.gcfont(gc, 8, False, T.TEXT2))
        gc.DrawText("Desktop Suite", 52, 38)

    def _paint_user(self, event):
        dc = wx.AutoBufferedPaintDC(self.user_zone)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.user_zone.GetSize()
        gc.SetBrush(wx.Brush(T.SIDEBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # avatar circle
        gc.SetBrush(wx.Brush(T.ACCENT3)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawEllipse(14, 13, 32, 32)
        gc.SetFont(T.gcfont(gc, 11, True, T.BG))
        tw, th = gc.GetTextExtent("A")
        gc.DrawText("A", 14 + (32-tw)/2, 13 + (32-th)/2)

        gc.SetFont(T.gcfont(gc, 10, True, T.TEXT))
        gc.DrawText("Admin", 54, 16)
        # green dot + online
        gc.SetBrush(wx.Brush(T.SUCCESS)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawEllipse(54, 36, 8, 8)
        gc.SetFont(T.gcfont(gc, 8, False, T.TEXT2))
        gc.DrawText("Online", 66, 34)

    def _on_item(self, idx):
        self.select(idx)
        self.on_nav(PAGES[idx][0])

    def select(self, idx):
        for i, item in enumerate(self.items):
            item.set_selected(i == idx)


# ══════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════
class StatCard(BasePanel):
    def __init__(self, parent, label, value, accent, sublabel=""):
        super().__init__(parent, T.BG)
        self.label    = label
        self.value    = value
        self.accent   = accent
        self.sublabel = sublabel
        self.SetMinSize((170, 100))

    def on_paint(self, gc, w, h):
        # card bg
        rounded_rect(gc, 0, 0, w, h, 10, fill=T.CARD, stroke=T.BORDER)

        # top accent bar
        rounded_rect(gc, 0, 0, w, 4, 2, fill=self.accent)

        # value
        gc.SetFont(T.gcfont(gc, 24, True, self.accent))
        vw, vh = gc.GetTextExtent(self.value)
        gc.DrawText(self.value, (w - vw) / 2, 16)

        # label
        gc.SetFont(T.gcfont(gc, 9, False, T.TEXT2))
        lw, lh = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, (w - lw) / 2, h - lh - 12)

        if self.sublabel:
            gc.SetFont(T.gcfont(gc, 8, False, T.TEXT3))
            sw, sh = gc.GetTextExtent(self.sublabel)
            gc.DrawText(self.sublabel, (w - sw) / 2, h - lh - sh - 16)


# ══════════════════════════════════════════════
#  CUSTOM LIST (vẽ tay từng row)
# ══════════════════════════════════════════════
class CustomList(wx.ScrolledWindow):
    ROW_H = 38

    def __init__(self, parent, columns):
        super().__init__(parent, style=wx.NO_BORDER)
        self.columns = columns   # [(label, weight), ...]
        self.rows    = []
        self.hovered = -1
        self.selected= -1

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetScrollRate(0, self.ROW_H)
        self.EnableScrolling(False, True)

        self.Bind(wx.EVT_PAINT,        self._paint)
        self.Bind(wx.EVT_SIZE,         lambda e: (e.Skip(), self._update_scroll(), self.Refresh()))
        self.Bind(wx.EVT_MOTION,       self._motion)
        self.Bind(wx.EVT_LEFT_DOWN,    self._click)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hover(-1))

    def set_rows(self, rows, colors=None):
        # rows: list of tuples matching columns count
        # colors: optional list of wx.Colour per row
        self.rows   = rows
        self.colors = colors or [None]*len(rows)
        self._update_scroll()
        self.Refresh()

    def _update_scroll(self):
        w, _ = self.GetClientSize()
        total_h = self.ROW_H * (len(self.rows) + 1)  # +1 header
        self.SetVirtualSize(w, total_h)

    def _set_hover(self, idx):
        if self.hovered != idx:
            self.hovered = idx; self.Refresh()

    def _motion(self, e):
        _, sy = self.GetViewStart()
        sy *= self.ROW_H
        row = (e.GetY() + sy - self.ROW_H) // self.ROW_H
        self._set_hover(int(row) if 0 <= row < len(self.rows) else -1)

    def _click(self, e):
        _, sy = self.GetViewStart()
        sy *= self.ROW_H
        row = (e.GetY() + sy - self.ROW_H) // self.ROW_H
        if 0 <= row < len(self.rows):
            self.selected = int(row); self.Refresh()

    def _col_widths(self, total_w):
        total_w -= 24
        total_weight = sum(w for _, w in self.columns)
        return [int(total_w * w / total_weight) for _, w in self.columns]

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(T.CARD))
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        cw, ch = self.GetClientSize()
        _, sy = self.GetViewStart(); sy *= self.ROW_H

        widths = self._col_widths(cw)

        # header
        rounded_rect(gc, 0, -sy, cw, self.ROW_H, 0, fill=T.CARD2)
        x = 12
        for i, ((label, _), w) in enumerate(zip(self.columns, widths)):
            gc.SetFont(T.gcfont(gc, 9, True, T.TEXT2))
            gc.DrawText(label.upper(), x + 4, -sy + (self.ROW_H - 14) // 2)
            x += w

        # rows
        for ri, row in enumerate(self.rows):
            ry = self.ROW_H * (ri + 1) - sy
            if ry + self.ROW_H < 0 or ry > ch:
                continue

            if ri == self.selected:
                bg = T.SEL
            elif ri == self.hovered:
                bg = T.HOVER
            else:
                bg = T.CARD if ri % 2 == 0 else wx.Colour(32, 40, 51)
            gc.SetBrush(wx.Brush(bg)); gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(0, ry, cw, self.ROW_H)

            x = 12
            for ci, (cell, w) in enumerate(zip(row, widths)):
                text  = str(cell[0]) if isinstance(cell, tuple) else str(cell)
                color = cell[1]      if isinstance(cell, tuple) else (self.colors[ri] or T.TEXT)
                gc.SetFont(T.gcfont(gc, 9, False, color))
                _, th = gc.GetTextExtent(text)
                gc.DrawText(text, x + 4, ry + (self.ROW_H - th) / 2)
                x += w

            # row divider
            gc.SetPen(wx.Pen(T.BORDER, 1)); gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawLines([(0, ry + self.ROW_H - 1), (cw, ry + self.ROW_H - 1)])


# ══════════════════════════════════════════════
#  CUSTOM BUTTON
# ══════════════════════════════════════════════
class FlatButton(wx.Panel):
    def __init__(self, parent, label, accent=None, size=(-1, 32)):
        super().__init__(parent, size=size, style=wx.NO_BORDER)
        self.label   = label
        self.accent  = accent or T.ACCENT
        self.hovered = False
        self.pressed = False
        self._cb     = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_PAINT,        self._paint)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self._h(True))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._h(False))
        self.Bind(wx.EVT_LEFT_DOWN,    self._down)
        self.Bind(wx.EVT_LEFT_UP,      self._up)
        self.Bind(wx.EVT_SIZE,         lambda e: (e.Skip(), self.Refresh()))

    def Bind_click(self, cb): self._cb = cb

    def _h(self, v): self.hovered = v; self.Refresh()
    def _down(self, e): self.pressed = True; self.Refresh()
    def _up(self, e):
        self.pressed = False; self.Refresh()
        if self._cb: self._cb()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        if self.pressed:
            bg = wx.Colour(max(0,self.accent.Red()-30),
                           max(0,self.accent.Green()-30),
                           max(0,self.accent.Blue()-30))
        elif self.hovered:
            bg = wx.Colour(min(255,self.accent.Red()+20),
                           min(255,self.accent.Green()+20),
                           min(255,self.accent.Blue()+20))
        else:
            bg = self.accent

        rounded_rect(gc, 0, 0, w, h, 6, fill=bg)
        gc.SetFont(T.gcfont(gc, 10, True, T.BG))
        tw, th = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, (w-tw)/2, (h-th)/2)


class GhostButton(FlatButton):
    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        bg = T.HOVER if self.hovered else T.CARD
        rounded_rect(gc, 0, 0, w, h, 6, fill=bg, stroke=T.BORDER)
        gc.SetFont(T.gcfont(gc, 10, False, T.TEXT))
        tw, th = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, (w-tw)/2, (h-th)/2)


# ══════════════════════════════════════════════
#  SECTION HEADER
# ══════════════════════════════════════════════
class SectionHeader(BasePanel):
    def __init__(self, parent, title, subtitle=""):
        super().__init__(parent, T.BG)
        self.title    = title
        self.subtitle = subtitle
        self.SetMinSize((-1, 70))

    def on_paint(self, gc, w, h):
        gc.SetFont(T.gcfont(gc, 18, True, T.TEXT))
        gc.DrawText(self.title, 0, 8)
        if self.subtitle:
            gc.SetFont(T.gcfont(gc, 10, False, T.TEXT2))
            gc.DrawText(self.subtitle, 2, 36)
        # accent underline
        gc.SetBrush(wx.Brush(T.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, h-3, 40, 3, 2)


# ══════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════
class DashboardPage(BasePanel):
    def __init__(self, parent):
        super().__init__(parent, T.BG)
        s = wx.BoxSizer(wx.VERTICAL)

        s.Add(SectionHeader(self, "Dashboard", "Welcome back, Admin"), 0, wx.EXPAND | wx.ALL, 20)

        # stat cards
        cards = wx.BoxSizer(wx.HORIZONTAL)
        data  = [
            ("Total Files", "1,284", T.ACCENT,  "+12% this week"),
            ("Processed",   "  843", T.SUCCESS, "67% of total"),
            ("Errors",      "    5", T.ERROR,   "2 critical"),
            ("Pending",     "  436", T.WARNING, "33% of total"),
        ]
        for label, val, color, sub in data:
            c = StatCard(self, label, val, color, sub)
            cards.Add(c, 1, wx.ALL, 6)
        s.Add(cards, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        s.AddSpacer(10)

        # section label
        lbl = wx.StaticText(self, label="Recent Activity")
        lbl.SetFont(T.font(11, True)); lbl.SetForegroundColour(T.TEXT)
        lbl.SetBackgroundColour(T.BG)
        s.Add(lbl, 0, wx.LEFT | wx.BOTTOM, 20)

        # custom list
        self.lst = CustomList(self, [
            ("Time",   2), ("Action", 5), ("Status", 2)
        ])
        rows = [
            [("10:42 AM", T.TEXT2), ("Processed report.pdf",   T.TEXT), ("✓  Done",    T.SUCCESS)],
            [("10:38 AM", T.TEXT2), ("Imported data.csv",      T.TEXT), ("✓  Done",    T.SUCCESS)],
            [("10:30 AM", T.TEXT2), ("Sync with server",       T.TEXT), ("✗  Failed",  T.ERROR)],
            [("10:15 AM", T.TEXT2), ("Generated summary.docx", T.TEXT), ("✓  Done",    T.SUCCESS)],
            [("09:55 AM", T.TEXT2), ("Backup completed",       T.TEXT), ("✓  Done",    T.SUCCESS)],
            [("09:40 AM", T.TEXT2), ("Deleted temp files",     T.TEXT), ("✓  Done",    T.SUCCESS)],
            [("09:20 AM", T.TEXT2), ("Config reload",          T.TEXT), ("⚠  Warning", T.WARNING)],
        ]
        self.lst.set_rows(rows)
        s.Add(self.lst, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(s)


class FilesPage(BasePanel):
    def __init__(self, parent):
        super().__init__(parent, T.BG)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(SectionHeader(self, "Files", "Manage your project files"), 0, wx.EXPAND | wx.ALL, 20)

        # toolbar buttons
        tb = wx.BoxSizer(wx.HORIZONTAL)
        for lbl, acc in [("+ New File", T.ACCENT), ("↑ Upload", T.ACCENT2)]:
            btn = FlatButton(self, lbl, acc, size=(110, 32))
            tb.Add(btn, 0, wx.RIGHT, 8)
        for lbl in ["Rename", "Delete"]:
            btn = GhostButton(self, lbl, size=(80, 32))
            tb.Add(btn, 0, wx.RIGHT, 8)
        s.Add(tb, 0, wx.LEFT | wx.BOTTOM, 20)

        self.lst = CustomList(self, [
            ("Name", 4), ("Type", 2), ("Size", 2), ("Modified", 3)
        ])
        rows = [
            [("report.pdf",    T.ACCENT),  ("PDF",    T.TEXT2), ("2.4 MB", T.TEXT2), ("Today 10:42",  T.TEXT2)],
            [("data.csv",      T.ACCENT2), ("CSV",    T.TEXT2), ("840 KB", T.TEXT2), ("Today 10:38",  T.TEXT2)],
            [("summary.docx",  T.ACCENT),  ("DOCX",   T.TEXT2), ("1.1 MB", T.TEXT2), ("Today 10:15",  T.TEXT2)],
            [("process.py",    T.ACCENT3), ("Python", T.TEXT2), ("12 KB",  T.TEXT2), ("Yesterday",    T.TEXT2)],
            [("output.json",   T.WARNING), ("JSON",   T.TEXT2), ("320 KB", T.TEXT2), ("Yesterday",    T.TEXT2)],
            [("run.bat",       T.TEXT2),   ("BAT",    T.TEXT2), ("2 KB",   T.TEXT2), ("3 days ago",   T.TEXT2)],
        ]
        self.lst.set_rows(rows)
        s.Add(self.lst, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(s)


class SettingsPage(BasePanel):
    def __init__(self, parent):
        super().__init__(parent, T.BG)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(SectionHeader(self, "Settings", "Configure your preferences"), 0, wx.EXPAND | wx.ALL, 20)

        card = BasePanel(self, T.CARD)
        cs   = wx.BoxSizer(wx.VERTICAL)

        def row(label, ctrl):
            r = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(card, label=label, size=(130,-1))
            lbl.SetFont(T.font(10)); lbl.SetForegroundColour(T.TEXT2)
            lbl.SetBackgroundColour(T.CARD)
            r.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            ctrl.SetBackgroundColour(T.CARD2)
            ctrl.SetForegroundColour(T.TEXT)
            ctrl.SetFont(T.font(10))
            r.Add(ctrl, 1)
            return r

        fields = [
            ("Output folder",  wx.TextCtrl(card, value="C:/output", style=wx.BORDER_SIMPLE)),
            ("Max threads",    wx.SpinCtrl(card, value="4", min=1, max=32, style=wx.BORDER_SIMPLE)),
            ("Log level",      wx.Choice(card, choices=["Debug","Info","Warning","Error"])),
            ("Auto backup",    wx.CheckBox(card)),
            ("Language",       wx.Choice(card, choices=["English","Tiếng Việt","中文"])),
        ]
        for lbl, ctrl in fields:
            cs.Add(row(lbl, ctrl), 0, wx.EXPAND | wx.ALL, 10)

        cs.Add(wx.Panel(card, size=(-1, 8), style=wx.NO_BORDER), 0)

        btn = FlatButton(card, "Save Settings", T.ACCENT, size=(140, 34))
        btn.Bind_click(lambda: wx.MessageBox("Settings saved!", "OK", wx.OK | wx.ICON_INFORMATION))
        cs.Add(btn, 0, wx.LEFT | wx.BOTTOM, 16)

        card.SetSizer(cs)
        s.Add(card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(s)


class GenericPage(BasePanel):
    def __init__(self, parent, name):
        super().__init__(parent, T.BG)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(SectionHeader(self, name), 0, wx.EXPAND | wx.ALL, 20)
        hint = wx.StaticText(self, label=f"Content for '{name}' goes here.")
        hint.SetFont(T.font(10)); hint.SetForegroundColour(T.TEXT2)
        hint.SetBackgroundColour(T.BG)
        s.Add(hint, 0, wx.LEFT, 20)
        self.SetSizer(s)


# ══════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════
class TopBar(BasePanel):
    def __init__(self, parent, title="Dashboard"):
        super().__init__(parent, T.SIDEBAR)
        self.page_title = title
        self.SetMinSize((-1, 48))

    def set_title(self, t):
        self.page_title = t; self.Refresh()

    def on_paint(self, gc, w, h):
        # left border
        gc.SetBrush(wx.Brush(T.BORDER)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, 1, h)
        # bottom border
        gc.DrawRectangle(0, h-1, w, 1)
        # title
        gc.SetFont(T.gcfont(gc, 11, True, T.TEXT))
        _, th = gc.GetTextExtent(self.page_title)
        gc.DrawText(self.page_title, 20, (h - th) / 2)


# ══════════════════════════════════════════════
#  CONTENT AREA
# ══════════════════════════════════════════════
class ContentArea(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(T.BG)

        self.topbar = TopBar(self)
        self.stack  = wx.BoxSizer(wx.VERTICAL)

        self.pages = {
            "Dashboard": DashboardPage(self),
            "Files":     FilesPage(self),
            "Reports":   GenericPage(self, "Reports"),
            "Tools":     GenericPage(self, "Tools"),
            "Settings":  SettingsPage(self),
            "About":     GenericPage(self, "About"),
        }
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        for p in self.pages.values():
            page_sizer.Add(p, 1, wx.EXPAND)
            p.Hide()

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.topbar, 0, wx.EXPAND)
        outer.Add(page_sizer, 1, wx.EXPAND)

        self.page_sizer = page_sizer
        self.current = None
        self.SetSizer(outer)
        self.show("Dashboard")

    def show(self, name):
        if self.current: self.current.Hide()
        p = self.pages.get(name)
        if p: p.Show(); self.current = p
        self.topbar.set_title(name)
        self.Layout()


# ══════════════════════════════════════════════
#  MAIN FRAME
# ══════════════════════════════════════════════
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="MyTool", size=(1100, 700),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((820, 540))
        self.SetBackgroundColour(T.BG)

        self.content = ContentArea(self)
        self.sidebar = Sidebar(self, self.content.show)

        main = wx.BoxSizer(wx.HORIZONTAL)
        main.Add(self.sidebar, 0, wx.EXPAND)
        main.Add(self.content, 1, wx.EXPAND)
        self.SetSizer(main)

        self.Centre()
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame()
    app.MainLoop()

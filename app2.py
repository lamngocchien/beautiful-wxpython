"""
Desktop Tool - Dark Mode Modern
wxPython với giao diện tối, accent xanh cyan

Author: lamngocchien
Repository: https://github.com/lamngocchien/beautiful-wxpython
Created: May 2026
"""

import wx
import wx.lib.scrolledpanel as scrolled

# ─────────────────────────────────────────────
#  THEME / COLOR PALETTE
# ─────────────────────────────────────────────
class Theme:
    BG_DARK       = wx.Colour(18,  18,  27)   # nền tổng thể
    BG_SIDEBAR    = wx.Colour(24,  24,  36)   # sidebar
    BG_CARD       = wx.Colour(30,  30,  46)   # card / panel
    BG_HOVER      = wx.Colour(40,  40,  60)   # hover state
    BG_SELECTED   = wx.Colour(0,   122, 204)  # selected item (xanh dương)
    ACCENT        = wx.Colour(0,   200, 180)  # cyan accent
    ACCENT2       = wx.Colour(99,  102, 241)  # indigo accent
    TEXT_PRIMARY  = wx.Colour(220, 220, 235)
    TEXT_SECONDARY= wx.Colour(130, 130, 160)
    TEXT_MUTED    = wx.Colour(80,  80,  110)
    BORDER        = wx.Colour(45,  45,  65)
    SUCCESS       = wx.Colour(34,  197, 94)
    ERROR         = wx.Colour(239, 68,  68)
    WARNING       = wx.Colour(251, 191, 36)

    @staticmethod
    def font(size=10, bold=False, italic=False):
        weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        style  = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, style, weight)


# ─────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────

class DarkPanel(wx.Panel):
    """Panel với màu nền dark"""
    def __init__(self, parent, bg=None):
        super().__init__(parent)
        self.SetBackgroundColour(bg or Theme.BG_CARD)


class SectionTitle(wx.StaticText):
    def __init__(self, parent, label):
        super().__init__(parent, label=label)
        self.SetFont(Theme.font(16, bold=True))
        self.SetForegroundColour(Theme.TEXT_PRIMARY)
        self.SetBackgroundColour(parent.GetBackgroundColour())


class SubLabel(wx.StaticText):
    def __init__(self, parent, label):
        super().__init__(parent, label=label)
        self.SetFont(Theme.font(9))
        self.SetForegroundColour(Theme.TEXT_SECONDARY)
        self.SetBackgroundColour(parent.GetBackgroundColour())


class Divider(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(-1, 1))
        self.SetBackgroundColour(Theme.BORDER)


class StatCard(wx.Panel):
    """Card hiển thị số liệu với custom draw"""
    def __init__(self, parent, label, value, color=None):
        super().__init__(parent, size=(160, 90))
        self.label = label
        self.value = value
        self.color = color or Theme.ACCENT
        self.SetBackgroundColour(Theme.BG_CARD)
        self.SetDoubleBuffered(True)  # Thêm double buffering
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE,  lambda e: self.Refresh())

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        # Thêm anti-aliasing
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)

        # Nền card bo góc
        gc.SetBrush(wx.Brush(Theme.BG_CARD))
        gc.SetPen(wx.Pen(self.color, 1))
        gc.DrawRoundedRectangle(1, 1, w-2, h-2, 10)

        # Thanh accent trên cùng
        gc.SetBrush(wx.Brush(self.color))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(1, 1, w-2, 4, 3)

        # Thêm hiệu ứng đổ bóng
        shadow = wx.Colour(self.color.Red()//2, self.color.Green()//2, self.color.Blue()//2, 100)
        gc.SetBrush(wx.Brush(shadow))
        gc.DrawRoundedRectangle(1, 5, w-2, 4, 3)

        # Value text
        gc.SetFont(gc.CreateFont(Theme.font(22, bold=True), self.color))
        tw, th = gc.GetTextExtent(self.value)
        gc.DrawText(self.value, (w - tw) / 2, 18)

        # Thêm hiệu ứng đổ bóng cho text
        shadow_color = wx.Colour(0, 0, 0, 100)
        gc.SetFont(gc.CreateFont(Theme.font(22, bold=True), shadow_color))
        gc.DrawText(self.value, (w - tw) / 2 + 1, 19)

        # Label text
        gc.SetFont(gc.CreateFont(Theme.font(8), Theme.TEXT_SECONDARY))
        lw, lh = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, (w - lw) / 2, h - lh - 10)

        # Thêm hiệu ứng đổ bóng cho label
        shadow_color = wx.Colour(0, 0, 0, 100)
        gc.SetFont(gc.CreateFont(Theme.font(8), shadow_color))
        gc.DrawText(self.label, (w - lw) / 2 + 1, h - lh - 9)


class NavItem(wx.Panel):
    """Sidebar nav item với hover effect"""
    def __init__(self, parent, label, icon_art, index):
        super().__init__(parent, size=(-1, 42))
        self.label    = label
        self.icon_art = icon_art
        self.index    = index
        self.selected = False
        self.hovered  = False

        self.SetBackgroundColour(Theme.BG_SIDEBAR)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetDoubleBuffered(True)  # Thêm double buffering

        self.Bind(wx.EVT_PAINT,        self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN,    self.OnClick)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)

    def SetSelected(self, sel):
        self.selected = sel
        self.Refresh()

    def OnEnter(self, e):
        self.hovered = True;  self.Refresh()
    def OnLeave(self, e):
        self.hovered = False; self.Refresh()

    def OnClick(self, e):
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetInt(self.index)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        # Thêm anti-aliasing
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)

        # Nền
        if self.selected:
            bg = Theme.BG_HOVER
        elif self.hovered:
            bg = wx.Colour(35, 35, 52)
        else:
            bg = Theme.BG_SIDEBAR
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # Thêm hiệu ứng đổ bóng
        if self.selected or self.hovered:
            shadow = wx.Colour(0, 0, 0, 50)
            gc.SetBrush(wx.Brush(shadow))
            gc.DrawRoundedRectangle(2, 2, w-4, h-4, 4)

        # Thanh accent bên trái nếu selected
        if self.selected:
            gc.SetBrush(wx.Brush(Theme.ACCENT))
            gc.DrawRoundedRectangle(0, 6, 4, h-12, 2)

            # Thêm hiệu ứng đổ bóng cho thanh accent
            shadow = wx.Colour(0, 0, 0, 100)
            gc.SetBrush(wx.Brush(shadow))
            gc.DrawRoundedRectangle(5, 6, 4, h-12, 2)

        # Icon
        bmp = wx.ArtProvider.GetBitmap(self.icon_art, wx.ART_MENU, (16, 16))
        if bmp.IsOk():
            # Tint icon sáng hơn
            img = bmp.ConvertToImage()
            img = img.AdjustChannels(2.0, 2.0, 2.0)
            bmp = img.ConvertToBitmap()

            # Thêm hiệu ứng đổ bóng cho icon
            shadow = wx.Colour(0, 0, 0, 100)
            gc.SetBrush(wx.Brush(shadow))
            gc.DrawRoundedRectangle(15, (h-16)/2 + 1, 16, 16, 2)

            gc.DrawBitmap(bmp, 14, (h-16)/2, 16, 16)

        # Label
        color = Theme.TEXT_PRIMARY if self.selected else Theme.TEXT_SECONDARY
        gc.SetFont(gc.CreateFont(
            Theme.font(10, bold=self.selected), color))
        _, th = gc.GetTextExtent(self.label)
        gc.DrawText(self.label, 38, (h - th) / 2)

        # Thêm hiệu ứng đổ bóng cho label
        shadow_color = wx.Colour(0, 0, 0, 100)
        gc.SetFont(gc.CreateFont(
            Theme.font(10, bold=self.selected), shadow_color))
        gc.DrawText(self.label, 39, (h - th) / 2 + 1)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
MENU = [
    ("Dashboard", wx.ART_HELP_BOOK),
    ("Files",     wx.ART_FOLDER),
    ("Reports",   wx.ART_REPORT_VIEW),
    ("Tools",     wx.ART_EXECUTABLE_FILE),
    ("Settings",  wx.ART_FIND_AND_REPLACE),
    ("About",     wx.ART_INFORMATION),
]

class Sidebar(wx.Panel):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, size=(210, -1))
        self.SetBackgroundColour(Theme.BG_SIDEBAR)
        self.on_navigate = on_navigate
        self.nav_items   = []

        sizer = wx.BoxSizer(wx.VERTICAL)

        # ── Logo / App name ──
        logo_panel = DarkPanel(self, Theme.BG_SIDEBAR)
        logo_sizer = wx.BoxSizer(wx.HORIZONTAL)

        dot = wx.Panel(logo_panel, size=(10, 10))
        dot.SetBackgroundColour(Theme.ACCENT)

        app_name = wx.StaticText(logo_panel, label="MyTool")
        app_name.SetFont(Theme.font(14, bold=True))
        app_name.SetForegroundColour(Theme.TEXT_PRIMARY)
        app_name.SetBackgroundColour(Theme.BG_SIDEBAR)

        logo_sizer.Add(dot,      0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 14)
        logo_sizer.Add(app_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        logo_panel.SetSizer(logo_sizer)

        sizer.Add(logo_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 16)
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer(8)

        # ── Nav items ──
        cat_label = wx.StaticText(self, label="NAVIGATION")
        cat_label.SetFont(Theme.font(7, bold=True))
        cat_label.SetForegroundColour(Theme.TEXT_MUTED)
        cat_label.SetBackgroundColour(Theme.BG_SIDEBAR)
        sizer.Add(cat_label, 0, wx.LEFT | wx.BOTTOM, 12)

        for i, (label, art) in enumerate(MENU):
            item = NavItem(self, label, art, i)
            self.nav_items.append(item)
            sizer.Add(item, 0, wx.EXPAND)
            self.Bind(wx.EVT_BUTTON, self.OnNavClick, item)

        sizer.AddStretchSpacer()
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # ── User area ──
        user_panel = DarkPanel(self, Theme.BG_SIDEBAR)
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        avatar = wx.Panel(user_panel, size=(32, 32))
        avatar.SetBackgroundColour(Theme.ACCENT2)

        uname = wx.StaticText(user_panel, label="Admin User")
        uname.SetFont(Theme.font(9, bold=True))
        uname.SetForegroundColour(Theme.TEXT_PRIMARY)
        uname.SetBackgroundColour(Theme.BG_SIDEBAR)

        ustatus = wx.StaticText(user_panel, label="● Online")
        ustatus.SetFont(Theme.font(8))
        ustatus.SetForegroundColour(Theme.SUCCESS)
        ustatus.SetBackgroundColour(Theme.BG_SIDEBAR)

        uinfo = wx.BoxSizer(wx.VERTICAL)
        uinfo.Add(uname)
        uinfo.Add(ustatus)

        user_sizer.Add(avatar,  0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        user_sizer.Add(uinfo,   0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        user_panel.SetSizer(user_sizer)
        sizer.Add(user_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        self.SetSizer(sizer)
        self.select(0)

    def select(self, idx):
        for i, item in enumerate(self.nav_items):
            item.SetSelected(i == idx)

    def OnNavClick(self, event):
        idx = event.GetInt()
        self.select(idx)
        self.on_navigate(MENU[idx][0])


# ─────────────────────────────────────────────
#  CONTENT PAGES
# ─────────────────────────────────────────────

class DashboardPage(DarkPanel):
    def __init__(self, parent):
        super().__init__(parent, Theme.BG_DARK)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        title = SectionTitle(self, "Dashboard")
        title.SetBackgroundColour(Theme.BG_DARK)
        sub   = SubLabel(self, "Welcome back, Admin")
        sub.SetBackgroundColour(Theme.BG_DARK)
        h2 = wx.BoxSizer(wx.VERTICAL)
        h2.Add(title); h2.Add(sub, 0, wx.TOP, 2)
        hdr.Add(h2, 1)
        sizer.Add(hdr, 0, wx.ALL, 20)
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Stat cards
        cards_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stats = [
            ("Total Files",  "1,284", Theme.ACCENT),
            ("Processed",    "  843", Theme.SUCCESS),
            ("Errors",       "    5", Theme.ERROR),
            ("Pending",      "  436", Theme.WARNING),
        ]
        for label, val, color in stats:
            card = StatCard(self, label, val, color)
            cards_sizer.Add(card, 1, wx.ALL, 6)
        sizer.Add(cards_sizer, 0, wx.EXPAND | wx.ALL, 14)

        # Recent activity
        act_label = wx.StaticText(self, label="Recent Activity")
        act_label.SetFont(Theme.font(11, bold=True))
        act_label.SetForegroundColour(Theme.TEXT_PRIMARY)
        act_label.SetBackgroundColour(Theme.BG_DARK)
        sizer.Add(act_label, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 16)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_HRULES)
        self.list.SetBackgroundColour(Theme.BG_CARD)
        self.list.SetForegroundColour(Theme.TEXT_PRIMARY)
        self.list.SetFont(Theme.font(9))

        for col, w in [("Time", 110), ("Action", 260), ("Status", 100)]:
            self.list.InsertColumn(self.list.GetColumnCount(), col, width=w)

        rows = [
            ("10:42 AM", "Processed report.pdf",  "✓ Done",    Theme.SUCCESS),
            ("10:38 AM", "Imported data.csv",      "✓ Done",    Theme.SUCCESS),
            ("10:30 AM", "Sync with server",       "✗ Failed",  Theme.ERROR),
            ("10:15 AM", "Generated summary.docx", "✓ Done",    Theme.SUCCESS),
            ("09:55 AM", "Backup completed",       "✓ Done",    Theme.SUCCESS),
        ]
        for i, (t, a, s, c) in enumerate(rows):
            self.list.InsertItem(i, t)
            self.list.SetItem(i, 1, a)
            self.list.SetItem(i, 2, s)
            self.list.SetItemTextColour(i, Theme.TEXT_PRIMARY)

        sizer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(sizer)


class FilesPage(DarkPanel):
    def __init__(self, parent):
        super().__init__(parent, Theme.BG_DARK)
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = SectionTitle(self, "Files")
        title.SetBackgroundColour(Theme.BG_DARK)
        sizer.Add(title, 0, wx.ALL, 20)
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Toolbar
        tb = wx.BoxSizer(wx.HORIZONTAL)
        for lbl, art in [("New", wx.ART_NEW), ("Open", wx.ART_FILE_OPEN), ("Delete", wx.ART_DELETE)]:
            bmp = wx.ArtProvider.GetBitmap(art, wx.ART_BUTTON, (16, 16))
            btn = wx.BitmapButton(self, bitmap=bmp, style=wx.BORDER_NONE)
            btn.SetBackgroundColour(Theme.BG_CARD)
            btn.SetToolTip(lbl)
            tb.Add(btn, 0, wx.RIGHT, 4)

        search = wx.SearchCtrl(self, size=(220, 28))
        search.SetBackgroundColour(Theme.BG_CARD)
        search.SetForegroundColour(Theme.TEXT_PRIMARY)
        tb.Add(search, 0, wx.LEFT, 12)
        sizer.Add(tb, 0, wx.ALL, 14)

        # Tree
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.BORDER_NONE)
        self.tree.SetBackgroundColour(Theme.BG_CARD)
        self.tree.SetForegroundColour(Theme.TEXT_PRIMARY)
        self.tree.SetFont(Theme.font(10))

        il = wx.ImageList(16, 16)
        fi = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, (16,16)))
        ff = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))
        self.tree.SetImageList(il); self._il = il

        root = self.tree.AddRoot("Project", fi)
        for folder, files in [
            ("Documents", ["report.pdf","notes.txt","summary.docx"]),
            ("Data",      ["input.csv","output.json"]),
            ("Scripts",   ["process.py","utils.py","run.bat"]),
        ]:
            node = self.tree.AppendItem(root, folder, fi)
            for f in files:
                self.tree.AppendItem(node, f, ff)
        self.tree.ExpandAll()
        sizer.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(sizer)


class SettingsPage(DarkPanel):
    def __init__(self, parent):
        super().__init__(parent, Theme.BG_DARK)
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = SectionTitle(self, "Settings")
        title.SetBackgroundColour(Theme.BG_DARK)
        sizer.Add(title, 0, wx.ALL, 20)
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Form card
        card = DarkPanel(self, Theme.BG_CARD)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(cols=2, vgap=12, hgap=16)
        grid.AddGrowableCol(1)

        def dark_label(text):
            lbl = wx.StaticText(card, label=text)
            lbl.SetFont(Theme.font(10))
            lbl.SetForegroundColour(Theme.TEXT_SECONDARY)
            lbl.SetBackgroundColour(Theme.BG_CARD)
            return lbl

        def dark_text(val=""):
            t = wx.TextCtrl(card, value=val, style=wx.BORDER_SIMPLE)
            t.SetBackgroundColour(Theme.BG_DARK)
            t.SetForegroundColour(Theme.TEXT_PRIMARY)
            t.SetFont(Theme.font(10))
            return t

        fields = [
            ("Output folder",  dark_text("C:/output")),
            ("Max threads",    wx.SpinCtrl(card, value="4", min=1, max=32)),
            ("Log level",      wx.Choice(card, choices=["Debug","Info","Warning","Error"])),
            ("Auto save",      wx.CheckBox(card)),
        ]
        for lbl_txt, ctrl in fields:
            grid.Add(dark_label(lbl_txt), 0, wx.ALIGN_CENTER_VERTICAL)
            if isinstance(ctrl, (wx.SpinCtrl, wx.Choice, wx.CheckBox)):
                ctrl.SetBackgroundColour(Theme.BG_DARK)
                ctrl.SetForegroundColour(Theme.TEXT_PRIMARY)
            grid.Add(ctrl, 1, wx.EXPAND)

        card_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 16)

        # Save button
        save_btn = wx.Button(card, label="  Save Settings  ", style=wx.BORDER_NONE)
        save_btn.SetBackgroundColour(Theme.ACCENT)
        save_btn.SetForegroundColour(wx.Colour(10, 10, 20))
        save_btn.SetFont(Theme.font(10, bold=True))
        save_btn.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox("Saved!", "OK", wx.OK))
        card_sizer.Add(save_btn, 0, wx.LEFT | wx.BOTTOM, 16)

        card.SetSizer(card_sizer)
        sizer.Add(card, 0, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(sizer)


class GenericPage(DarkPanel):
    def __init__(self, parent, name):
        super().__init__(parent, Theme.BG_DARK)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = SectionTitle(self, name)
        title.SetBackgroundColour(Theme.BG_DARK)
        sizer.Add(title, 0, wx.ALL, 20)
        sizer.Add(Divider(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        hint = SubLabel(self, f"Content for '{name}' goes here.")
        hint.SetBackgroundColour(Theme.BG_DARK)
        sizer.Add(hint, 0, wx.ALL, 20)
        self.SetSizer(sizer)


# ─────────────────────────────────────────────
#  CONTENT AREA
# ─────────────────────────────────────────────
class ContentArea(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(Theme.BG_DARK)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.pages = {
            "Dashboard": DashboardPage(self),
            "Files":     FilesPage(self),
            "Reports":   GenericPage(self, "Reports"),
            "Tools":     GenericPage(self, "Tools"),
            "Settings":  SettingsPage(self),
            "About":     GenericPage(self, "About"),
        }
        for p in self.pages.values():
            self.sizer.Add(p, 1, wx.EXPAND)
            p.Hide()

        self.current = None
        self.show("Dashboard")
        self.SetSizer(self.sizer)

    def show(self, name):
        if self.current:
            self.current.Hide()
        p = self.pages.get(name)
        if p:
            p.Show()
            self.current = p
        self.Layout()


# ─────────────────────────────────────────────
#  MAIN FRAME
# ─────────────────────────────────────────────
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="MyTool", size=(1060, 680),
                         style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((800, 520))
        self.SetBackgroundColour(Theme.BG_DARK)

        # Status bar
        sb = self.CreateStatusBar(2)
        sb.SetBackgroundColour(Theme.BG_SIDEBAR)
        sb.SetForegroundColour(Theme.TEXT_SECONDARY)
        sb.SetStatusWidths([-1, 160])
        sb.SetStatusText("Ready", 0)
        sb.SetStatusText("v2.0  Dark Mode", 1)

        # Menu
        mb = wx.MenuBar()
        fm = wx.Menu()
        fm.Append(wx.ID_NEW,  "&New\tCtrl+N")
        fm.Append(wx.ID_OPEN, "&Open\tCtrl+O")
        fm.AppendSeparator()
        fm.Append(wx.ID_EXIT, "Exit\tAlt+F4")
        mb.Append(fm, "&File")
        hm = wx.Menu()
        hm.Append(wx.ID_ABOUT, "&About")
        mb.Append(hm, "&Help")
        self.SetMenuBar(mb)
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), id=wx.ID_EXIT)

        # Layout: sidebar | content
        main = wx.BoxSizer(wx.HORIZONTAL)
        self.content_area = ContentArea(self)
        self.sidebar      = Sidebar(self, self.on_navigate)

        main.Add(self.sidebar,      0, wx.EXPAND)
        main.Add(self.content_area, 1, wx.EXPAND)
        self.SetSizer(main)

        self.Centre()
        self.Show()

    def on_navigate(self, name):
        self.content_area.show(name)
        self.SetStatusText(f"  {name}", 0)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
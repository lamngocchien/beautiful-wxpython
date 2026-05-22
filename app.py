"""
Desktop Tool - wxPython Native OS Demo
Sidebar Navigation + Content Area

Author: lamngocchien
Repository: https://github.com/lamngocchien/beautiful-wxpython
"""

import wx
import wx.lib.agw.flatnotebook as FNB

# ─────────────────────────────────────────────
#  Custom Event để sidebar giao tiếp với content
# ─────────────────────────────────────────────
myEVT_NAVIGATE = wx.NewEventType()
EVT_NAVIGATE = wx.PyEventBinder(myEVT_NAVIGATE, 1)

class NavigateEvent(wx.PyCommandEvent):
    def __init__(self, label=""):
        super().__init__(myEVT_NAVIGATE)
        self.label = label

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
class SidebarPanel(wx.Panel):
    MENU_ITEMS = [
        ("Dashboard",  wx.ART_HELP_BOOK),
        ("Files",      wx.ART_FOLDER),
        ("Reports",    wx.ART_REPORT_VIEW),
        ("Tools",      wx.ART_EXECUTABLE_FILE),
        ("Settings",   wx.ART_FIND_AND_REPLACE),
        ("About",      wx.ART_INFORMATION),
    ]

    def __init__(self, parent):
        super().__init__(parent)

        # Dark mode support
        self.dark_mode = False

        # Màu nền lấy từ hệ thống (native)
        sys_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK)
        self.SetBackgroundColour(sys_bg)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # ── Tiêu đề app ──
        self.title_panel = wx.Panel(self)
        self.title_panel.SetBackgroundColour(sys_bg)
        title_sizer = wx.BoxSizer(wx.VERTICAL)

        app_label = wx.StaticText(self.title_panel, label="MY TOOL")
        app_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        app_font.SetPointSize(app_font.GetPointSize() + 1)
        app_font.SetWeight(wx.FONTWEIGHT_BOLD)
        app_label.SetFont(app_font)

        title_sizer.Add(app_label, 0, wx.ALL, 10)
        title_sizer.Add(wx.StaticLine(self.title_panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        self.title_panel.SetSizer(title_sizer)

        sizer.Add(self.title_panel, 0, wx.EXPAND)

        # ── Navigation list ──
        self.nav_list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.BORDER_NONE
        )
        self.nav_list.InsertColumn(0, "", width=180)

        # Thêm icon từ ArtProvider (native)
        img_list = wx.ImageList(16, 16)
        self.icon_map = {}
        for i, (label, art_id) in enumerate(self.MENU_ITEMS):
            bmp = wx.ArtProvider.GetBitmap(art_id, wx.ART_MENU, (16, 16))
            idx = img_list.Add(bmp)
            self.icon_map[i] = idx

        self.nav_list.SetImageList(img_list, wx.IMAGE_LIST_SMALL)
        self._img_list = img_list  # giữ reference

        for i, (label, art_id) in enumerate(self.MENU_ITEMS):
            self.nav_list.InsertItem(i, f"  {label}", self.icon_map[i])

        self.nav_list.Select(0)
        self.nav_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)

        sizer.Add(self.nav_list, 1, wx.EXPAND | wx.TOP, 4)

        # ── Trạng thái ở cuối sidebar ──
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        self.status = wx.StaticText(self, label="● Connected")
        status_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        status_font.SetPointSize(status_font.GetPointSize() - 1)
        self.status.SetFont(status_font)
        self.status.SetForegroundColour(wx.Colour(0, 150, 80))
        sizer.Add(self.status, 0, wx.ALL, 8)

        self.SetSizer(sizer)

        # Add dark mode toggle button
        self.add_dark_mode_toggle()

    def add_dark_mode_toggle(self):
        """Add toggle button for dark mode"""
        toggle_panel = wx.Panel(self)
        toggle_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dark_mode_btn = wx.BitmapButton(
            toggle_panel,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_BUTTON, (16, 16))
        )
        self.dark_mode_btn.SetToolTip("Toggle Dark Mode")
        self.dark_mode_btn.Bind(wx.EVT_BUTTON, self.on_dark_mode_toggle)

        toggle_sizer.Add(self.dark_mode_btn, 0, wx.ALL, 4)
        toggle_panel.SetSizer(toggle_sizer)

        # Add to main sizer before status
        self.GetSizer().Insert(self.GetSizer().GetItemCount() - 1, toggle_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        self.Layout()

    def on_dark_mode_toggle(self, event=None):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.toggle_dark_mode()
        self.update_dark_mode_icon()

        # Propagate to main frame
        frame = self.GetParent().GetParent()
        if hasattr(frame, 'toggle_dark_mode'):
            frame.toggle_dark_mode()

    def update_dark_mode_icon(self):
        """Update the dark mode toggle button icon"""
        if self.dark_mode:
            bmp = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_BUTTON, (16, 16))
        else:
            bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_BUTTON, (16, 16))
        self.dark_mode_btn.SetBitmap(bmp)

    def toggle_dark_mode(self):
        """Apply dark or light mode colors"""
        if self.dark_mode:
            # Dark mode colors
            bg_color = wx.Colour(45, 45, 45)
            fg_color = wx.Colour(240, 240, 240)
            title_bg = wx.Colour(30, 30, 30)
            status_color = wx.Colour(0, 200, 100)
            list_bg = wx.Colour(55, 55, 55)
            list_fg = wx.Colour(220, 220, 220)
        else:
            # Light mode colors (system defaults)
            bg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK)
            fg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            title_bg = bg_color
            status_color = wx.Colour(0, 150, 80)
            list_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            list_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        # Apply colors
        self.SetBackgroundColour(bg_color)
        self.title_panel.SetBackgroundColour(title_bg)
        self.status.SetForegroundColour(status_color)
        self.status.SetLabel("● Connected" if not self.dark_mode else "● Dark Mode")

        # Update list control colors
        self.nav_list.SetBackgroundColour(list_bg)
        self.nav_list.SetTextColour(list_fg)

        # Refresh all panels
        self.Refresh()
        self.Update()

    def OnSelect(self, event):
        idx = event.GetIndex()
        label = self.MENU_ITEMS[idx][0]
        evt = NavigateEvent(label=label)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent().GetParent(), evt)  # bubble lên Frame

# ─────────────────────────────────────────────
#  CONTENT PANELS
# ─────────────────────────────────────────────
class DashboardPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Dashboard")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 6)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        sizer.Add(self.title, 0, wx.ALL, 16)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        # Stat cards dùng StaticBox (native)
        cards_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stats = [
            ("Total Files", "1,284"),
            ("Processed",   "  843"),
            ("Errors",      "    5"),
            ("Pending",     "  436"),
        ]
        for label, value in stats:
            box = wx.StaticBox(self, label=label)
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            val_text = wx.StaticText(self, label=value)
            val_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            val_font.SetPointSize(val_font.GetPointSize() + 10)
            val_font.SetWeight(wx.FONTWEIGHT_BOLD)
            val_text.SetFont(val_font)
            box_sizer.Add(val_text, 0, wx.ALL | wx.ALIGN_CENTER, 12)
            cards_sizer.Add(box_sizer, 1, wx.ALL, 8)

        sizer.Add(cards_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Recent activity list
        activity_box = wx.StaticBox(self, label="Recent Activity")
        activity_sizer = wx.StaticBoxSizer(activity_box, wx.VERTICAL)

        self.activity_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.activity_list.InsertColumn(0, "Time",   width=120)
        self.activity_list.InsertColumn(1, "Action", width=200)
        self.activity_list.InsertColumn(2, "Status", width=100)

        rows = [
            ("10:42 AM", "Processed report.pdf",   "Done"),
            ("10:38 AM", "Imported data.csv",       "Done"),
            ("10:30 AM", "Sync with server",        "Failed"),
            ("10:15 AM", "Generated summary.docx",  "Done"),
            ("09:55 AM", "Backup completed",        "Done"),
        ]
        for i, (t, a, s) in enumerate(rows):
            self.activity_list.InsertItem(i, t)
            self.activity_list.SetItem(i, 1, a)
            self.activity_list.SetItem(i, 2, s)

        activity_sizer.Add(self.activity_list, 1, wx.EXPAND | wx.ALL, 4)
        sizer.Add(activity_sizer, 1, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(sizer)

    def toggle_dark_mode(self, dark_mode):
        """Apply dark mode colors"""
        if dark_mode:
            # Dark mode colors
            bg_color = wx.Colour(45, 45, 45)
            fg_color = wx.Colour(240, 240, 240)
            card_bg = wx.Colour(55, 55, 55)
            list_bg = wx.Colour(55, 55, 55)
            list_fg = wx.Colour(220, 220, 220)
        else:
            # Light mode colors
            bg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            fg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            card_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            list_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            list_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        self.SetBackgroundColour(bg_color)
        self.title.SetForegroundColour(fg_color)

        if self.activity_list:
            self.activity_list.SetBackgroundColour(list_bg)
            self.activity_list.SetTextColour(list_fg)

        # Update all static boxes (cards)
        for child in self.GetChildren():
            if isinstance(child, wx.StaticBox):
                child.SetForegroundColour(fg_color)
                child_sizer = child.GetContainingSizer()
                if child_sizer:
                    for item in child_sizer.GetChildren():
                        if item.GetWindow():
                            item.GetWindow().SetBackgroundColour(card_bg)
                            item.GetWindow().SetForegroundColour(fg_color)

        self.Refresh()

class FilesPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Toolbar actions
        self.title = wx.StaticText(self, label="Files")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 6)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        sizer.Add(self.title, 0, wx.ALL, 16)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        # Action buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label, art in [("New", wx.ART_NEW), ("Open", wx.ART_FILE_OPEN), ("Delete", wx.ART_DELETE)]:
            bmp = wx.ArtProvider.GetBitmap(art, wx.ART_BUTTON, (16, 16))
            btn = wx.BitmapButton(self, bitmap=bmp)
            btn.SetToolTip(label)
            btn_sizer.Add(btn, 0, wx.RIGHT, 4)
        btn_sizer.Add(wx.SearchCtrl(self, size=(200, -1)), 0, wx.LEFT, 8)
        sizer.Add(btn_sizer, 0, wx.ALL, 8)

        # File tree
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.BORDER_SUNKEN)
        img_list = wx.ImageList(16, 16)
        folder_idx = img_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)))
        file_idx   = img_list.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))
        self.tree.SetImageList(img_list)
        self._img_list = img_list

        root = self.tree.AddRoot("Project", folder_idx)
        for folder, files in [
            ("Documents", ["report.pdf", "notes.txt", "summary.docx"]),
            ("Data",      ["input.csv",  "output.json"]),
            ("Scripts",   ["process.py", "utils.py", "run.bat"]),
        ]:
            node = self.tree.AppendItem(root, folder, folder_idx)
            for f in files:
                self.tree.AppendItem(node, f, file_idx)
        self.tree.ExpandAll()

        sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(sizer)

    def toggle_dark_mode(self, dark_mode):
        """Apply dark mode colors"""
        if dark_mode:
            # Dark mode colors
            bg_color = wx.Colour(45, 45, 45)
            fg_color = wx.Colour(240, 240, 240)
            tree_bg = wx.Colour(55, 55, 55)
            tree_fg = wx.Colour(220, 220, 220)
        else:
            # Light mode colors
            bg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            fg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            tree_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            tree_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        self.SetBackgroundColour(bg_color)
        self.title.SetForegroundColour(fg_color)

        if self.tree:
            self.tree.SetBackgroundColour(tree_bg)
            self.tree.SetForegroundColour(tree_fg)

        self.Refresh()

class SettingsPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Settings")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 6)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        sizer.Add(self.title, 0, wx.ALL, 16)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        # Form fields dùng FlexGridSizer (căn chỉnh đẹp native)
        form_box = wx.StaticBox(self, label="General")
        form_sizer = wx.StaticBoxSizer(form_box, wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=12)
        grid.AddGrowableCol(1)

        fields = [
            ("Output folder:",   wx.TextCtrl(self, value="C:/output")),
            ("Max threads:",     wx.SpinCtrl(self, value="4", min=1, max=32)),
            ("Log level:",       wx.Choice(self, choices=["Debug", "Info", "Warning", "Error"])),
            ("Auto save:",       wx.CheckBox(self)),
            ("Language:",        wx.Choice(self, choices=["English", "Tiếng Việt", "中文"])),
        ]
        for label, ctrl in fields:
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(ctrl, 1, wx.EXPAND)

        form_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 8)
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Save button
        save_btn = wx.Button(self, label="Save Settings")
        sizer.Add(save_btn, 0, wx.LEFT, 16)
        save_btn.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox("Settings saved!", "OK", wx.OK | wx.ICON_INFORMATION))

        self.SetSizer(sizer)

    def toggle_dark_mode(self, dark_mode):
        """Apply dark mode colors"""
        if dark_mode:
            # Dark mode colors
            bg_color = wx.Colour(45, 45, 45)
            fg_color = wx.Colour(240, 240, 240)
            field_bg = wx.Colour(55, 55, 55)
            field_fg = wx.Colour(220, 220, 220)
        else:
            # Light mode colors
            bg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            fg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            field_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            field_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        self.SetBackgroundColour(bg_color)
        self.title.SetForegroundColour(fg_color)

        # Update all controls
        for child in self.GetChildren():
            if isinstance(child, (wx.TextCtrl, wx.SpinCtrl, wx.Choice, wx.CheckBox)):
                child.SetBackgroundColour(field_bg)
                child.SetForegroundColour(field_fg)
            elif isinstance(child, wx.StaticText):
                child.SetForegroundColour(fg_color)
            elif isinstance(child, wx.StaticBox):
                child.SetForegroundColour(fg_color)
                for item in child.GetContainingSizer().GetChildren():
                    if item.GetWindow():
                        item.GetWindow().SetBackgroundColour(field_bg)
                        item.GetWindow().SetForegroundColour(field_fg)

        self.Refresh()

class GenericPanel(wx.Panel):
    """Panel mặc định cho các mục chưa làm"""
    def __init__(self, parent, name="Page"):
        super().__init__(parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label=name)
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 6)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        sizer.Add(self.title, 0, wx.ALL, 16)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        self.hint = wx.StaticText(self, label=f"Content for '{name}' goes here.")
        self.hint.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        sizer.Add(self.hint, 0, wx.ALL, 16)

        self.SetSizer(sizer)

    def toggle_dark_mode(self, dark_mode):
        """Apply dark mode colors"""
        if dark_mode:
            # Dark mode colors
            bg_color = wx.Colour(45, 45, 45)
            fg_color = wx.Colour(240, 240, 240)
            hint_color = wx.Colour(150, 150, 150)
        else:
            # Light mode colors
            bg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            fg_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            hint_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        self.SetBackgroundColour(bg_color)
        self.title.SetForegroundColour(fg_color)
        self.hint.SetForegroundColour(hint_color)
        self.Refresh()

# ─────────────────────────────────────────────
#  CONTENT AREA (quản lý các panel)
# ─────────────────────────────────────────────
class ContentArea(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent  # Store parent reference for dark mode

        # Tạo sẵn tất cả panels, ẩn/hiện khi navigate
        self.panels = {
            "Dashboard": DashboardPanel(self),
            "Files":     FilesPanel(self),
            "Reports":   GenericPanel(self, "Reports"),
            "Tools":     GenericPanel(self, "Tools"),
            "Settings":  SettingsPanel(self),
            "About":     GenericPanel(self, "About"),
        }

        # Apply dark mode if sidebar is in dark mode
        self.toggle_dark_mode(False)

        for panel in self.panels.values():
            self.sizer.Add(panel, 1, wx.EXPAND)
            panel.Hide()

        self.current = None
        self.show_page("Dashboard")
        self.SetSizer(self.sizer)

    def show_page(self, name):
        if self.current:
            self.current.Hide()
        panel = self.panels.get(name)
        if panel:
            panel.Show()
            self.current = panel
        self.Layout()

    def toggle_dark_mode(self, dark_mode):
        """Propagate dark mode to all panels"""
        for panel in self.panels.values():
            if hasattr(panel, 'toggle_dark_mode'):
                panel.toggle_dark_mode(dark_mode)

# ─────────────────────────────────────────────
#  MAIN FRAME
# ─────────────────────────────────────────────
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="Desktop Tool",
            size=(960, 640),
            style=wx.DEFAULT_FRAME_STYLE
        )
        self.SetMinSize((700, 450))

        # Dark mode state
        self.dark_mode = False

        # Icon native
        self.SetIcon(wx.ArtProvider.GetIcon(wx.ART_EXECUTABLE_FILE))

        # Status bar
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-1, 180])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("v1.0.0", 1)

        # Menu bar
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW,  "&New\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menu_bar.Append(file_menu, "&File")

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, lambda e: self.Close(), id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        # Splitter: sidebar | content
        splitter = wx.SplitterWindow(self, style=wx.SP_THIN_SASH | wx.SP_LIVE_UPDATE)

        self.sidebar = SidebarPanel(splitter)
        self.content = ContentArea(splitter)

        splitter.SplitVertically(self.sidebar, self.content, sashPosition=200)
        splitter.SetMinimumPaneSize(160)

        # Lắng nghe navigate event
        self.Bind(EVT_NAVIGATE, self.OnNavigate)

        # Propagate dark mode to content area
        self.content.toggle_dark_mode(self.dark_mode)

        self.Centre()
        self.Show()

    def toggle_dark_mode(self):
        """Toggle dark mode for the entire application"""
        self.dark_mode = not self.dark_mode
        self.sidebar.toggle_dark_mode()
        self.content.toggle_dark_mode(self.dark_mode)

    def OnNavigate(self, event):
        label = event.label
        self.content.show_page(label)
        self.status_bar.SetStatusText(f"Viewing: {label}", 0)

        # Update status bar colors for dark mode
        if self.dark_mode:
            self.status_bar.SetBackgroundColour(wx.Colour(45, 45, 45))
            self.status_bar.SetForegroundColour(wx.Colour(240, 240, 240))
        else:
            self.status_bar.SetBackgroundColour(wx.NullColour)
            self.status_bar.SetForegroundColour(wx.NullColour)

    def OnAbout(self, event):
        wx.MessageBox(
            "Desktop Tool v1.0.0\nBuilt with wxPython",
            "About",
            wx.OK | wx.ICON_INFORMATION
        )

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
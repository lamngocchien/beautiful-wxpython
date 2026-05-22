"""
SSH Connection Manager — wxPython fully custom painted
Pixel-faithful recreation of the HTML design
"""
import wx
import datetime
import time
import random
import re
import wx.stc as stc
import ctypes
import platform

# ══════════════════════════════════════════════════════
#  WINDOWS DARK MODE HELPERS
# ══════════════════════════════════════════════════════
def apply_dark_scrollbars(window):
    if platform.system() == 'Windows':
        try:
            hwnd = window.GetHandle()
            ctypes.windll.uxtheme.SetWindowTheme(hwnd, "DarkMode_Explorer", None)
        except Exception: pass

def apply_dark_titlebar(frame):
    if platform.system() == 'Windows':
        try:
            hwnd = frame.GetHandle()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except Exception: pass


# ══════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════
class C:
    APP_BG      = wx.Colour(26,  26,  31)
    TITLEBAR    = wx.Colour(20,  20,  24)
    MENUBAR     = wx.Colour(30,  30,  38)
    SIDEBAR     = wx.Colour(30,  30,  38)
    EDITOR_BG   = wx.Colour(22,  22,  30)
    CODE_BG     = wx.Colour(22,  22,  30)
    INFO_BG     = wx.Colour(28,  28,  36)
    STATUSBAR   = wx.Colour(17,  17,  24)
    TAB_BG      = wx.Colour(26,  26,  34)
    CARD        = wx.Colour(37,  37,  48)
    HOVER       = wx.Colour(46,  46,  62)
    SEL         = wx.Colour(35,  35,  54)
    BORDER      = wx.Colour(42,  42,  53)
    BORDER2     = wx.Colour(58,  58,  80)
    SHADOW      = wx.Colour(15,  15,  20)

    ACCENT      = wx.Colour(139, 156, 255)
    GREEN       = wx.Colour(61,  220, 132)
    AMBER       = wx.Colour(244, 166,  35)
    RED         = wx.Colour(255, 107, 107)
    GRAY_DOT    = wx.Colour(85,  85,  104)

    TEXT        = wx.Colour(200, 200, 208)
    TEXT2       = wx.Colour(136, 136, 160)
    TEXT3       = wx.Colour(90,  90,  120)
    TEXT4       = wx.Colour(60,  60,  90)

    # syntax
    SYN_KW      = wx.Colour(199, 146, 234)
    SYN_STR     = wx.Colour(195, 232, 141)
    SYN_IP      = wx.Colour(130, 170, 255)
    SYN_PARAM   = wx.Colour(255, 203, 107)
    SYN_VAL     = wx.Colour(247, 140, 108)
    SYN_COMMENT = wx.Colour(78,  78,  110)
    SYN_OP      = wx.Colour(137, 221, 255)
    SYN_NUM     = wx.Colour(247, 140, 108)

    @staticmethod
    def font(size=10, bold=False, mono=False):
        fam = wx.FONTFAMILY_TELETYPE if mono else wx.FONTFAMILY_DEFAULT
        w   = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        return wx.Font(size, fam, wx.FONTSTYLE_NORMAL, w)

    @staticmethod
    def italic_font(size=10):
        return wx.Font(size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)


# ══════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════
CONNECTIONS = {
    'prod-web':   dict(ip='192.18.2.18',  port='22',   proto='/ssh',   auth='password', user='admin',    status='Active',  sc='green'),
    'prod-db':    dict(ip='192.18.2.20',  port='22',   proto='/ssh',   auth='key',      user='deploy',   status='Idle',    sc='green'),
    'prod-cache': dict(ip='192.18.2.21',  port='6379', proto='/tcp',   auth='password', user='root',     status='Idle',    sc='amber'),
    'stg-app':    dict(ip='10.0.1.10',    port='22',   proto='/ssh',   auth='password', user='ubuntu',   status='Offline', sc='gray'),
    'stg-db':     dict(ip='10.0.1.11',    port='5432', proto='/pgsql', auth='password', user='postgres', status='Offline', sc='gray'),
    'stg-ci':     dict(ip='10.0.1.15',    port='22',   proto='/ssh',   auth='key',      user='ci-bot',   status='Idle',    sc='green'),
    'dev-vm':     dict(ip='127.0.0.1',    port='2222', proto='/ssh',   auth='key',      user='vagrant',  status='Idle',    sc='green'),
    'dev-wsl':    dict(ip='172.20.0.1',   port='22',   proto='/ssh',   auth='password', user='wsl',      status='Idle',    sc='amber'),
    'aws-ec2':    dict(ip='54.210.8.41',  port='22',   proto='/ssh',   auth='key',      user='ec2-user', status='Idle',    sc='gray'),
    'aws-rds':    dict(ip='54.210.9.12',  port='3306', proto='/mysql', auth='password', user='admin',    status='Error',   sc='red'),
}

GROUPS = [
    ('Production', True,  [('web-server-01','prod-web','ssh'), ('db-primary','prod-db','ssh'), ('redis-cache','prod-cache','tcp')]),
    ('Staging',    True,  [('app-staging','stg-app','ssh'), ('pg-staging','stg-db','db'), ('ci-runner','stg-ci','ssh')]),
    ('Dev / Local',False, [('vagrant-vm','dev-vm','ssh'), ('wsl2-ubuntu','dev-wsl','ssh')]),
    ('Cloud — AWS',False, [('ec2-bastion','aws-ec2','ssh'), ('rds-mysql','aws-rds','db')]),
]

DOT_COLORS = {'green': C.GREEN, 'amber': C.AMBER, 'gray': C.GRAY_DOT, 'red': C.RED}


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def rr(gc, x, y, w, h, r, fill=None, stroke=None, sw=1):
    gc.SetBrush(wx.Brush(fill) if fill else wx.TRANSPARENT_BRUSH)
    gc.SetPen(wx.Pen(stroke, sw) if stroke else wx.TRANSPARENT_PEN)
    gc.DrawRoundedRectangle(x, y, w, h, r)

def text_wh(gc, s):
    w, h = gc.GetTextExtent(s)
    return float(w), float(h)

def hline(gc, x, y, w, color):
    gc.SetPen(wx.Pen(color, 1)); gc.SetBrush(wx.TRANSPARENT_BRUSH)
    gc.DrawLines([(x, y), (x+w, y)])

def vline(gc, x, y, h, color):
    gc.SetPen(wx.Pen(color, 1)); gc.SetBrush(wx.TRANSPARENT_BRUSH)
    gc.DrawLines([(x, y), (x, y+h)])


# ══════════════════════════════════════════════════════
#  CUSTOM DARK POPUP MENU
# ══════════════════════════════════════════════════════
class DarkMenu(wx.PopupTransientWindow):
    """A fully custom-drawn popup menu for perfect Dark Mode integration"""
    PADDING = 4
    MIN_WIDTH = 180

    def __init__(self, parent, items):
        super().__init__(parent)
        self.hovered = -1
        self.font = C.font(9)

        # Normalize items so separators do not consume an entire row.
        self.items = [item for item in items if item != "-"]
        self.separator_after = set()
        row = 0
        for i, item in enumerate(items):
            if item == "-":
                if row > 0:
                    self.separator_after.add(row - 1)
                continue
            row += 1

        # Measure items using a memory DC so style sizing is consistent.
        bmp = wx.Bitmap(1, 1)
        dc = wx.MemoryDC(bmp)
        gc = wx.GraphicsContext.Create(dc)
        gc.SetFont(gc.CreateFont(self.font, C.TEXT))

        text_heights = []
        max_text_w = 0
        for item in self.items:
            tw, th = text_wh(gc, item)
            text_heights.append(th)
            max_text_w = max(max_text_w, tw)

        text_h = max(text_heights) if text_heights else 0
        self.item_h = max(30, int(text_h + 12))
        self.w = max(self.MIN_WIDTH, int(max_text_w + 32))

        self.SetClientSize((self.w, len(self.items) * self.item_h + self.PADDING * 2))
        self.SetBackgroundColour(C.APP_BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_MOTION, self._motion)
        self.Bind(wx.EVT_LEFT_DOWN, self._click)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hover(-1))

    def _set_hover(self, idx):
        if self.hovered != idx:
            self.hovered = idx
            self.Refresh()

    def _motion(self, e):
        y = e.GetY() - self.PADDING
        if y < 0 or y >= len(self.items) * self.item_h:
            self._set_hover(-1)
            return

        idx = int(y // self.item_h)
        self._set_hover(idx)

    def _click(self, e):
        if self.hovered != -1 and self.items[self.hovered] != "-":
            print(f"Action: {self.items[self.hovered]}") # Handle menu click here
            self.Dismiss()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        # Menu background - brighter than app background
        gc.SetBrush(wx.Brush(C.CARD))
        gc.SetPen(wx.Pen(C.BORDER, 1))
        gc.DrawRectangle(0, 0, w, h)

        for i, item in enumerate(self.items):
            ry = self.PADDING + i * self.item_h

            # Hover highlight - subtle but visible
            if i == self.hovered:
                gc.SetBrush(wx.Brush(C.HOVER))
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.DrawRectangle(2, ry + 2, w - 4, self.item_h - 4)

            # Text - left aligned with good padding
            gc.SetFont(gc.CreateFont(self.font, C.TEXT))
            tw, th = text_wh(gc, item)
            gc.DrawText(item, 12, ry + (self.item_h - th) / 2)

            # Separator line if the next logical item was separated by '-'
            if i in self.separator_after:
                ysep = ry + self.item_h - 1
                gc.SetPen(wx.Pen(C.BORDER, 1))
                gc.StrokeLine(8, ysep, w - 8, ysep)

# ══════════════════════════════════════════════════════
#  MENU BAR
# ══════════════════════════════════════════════════════

class MenuBarPanel(wx.Panel):

    H = 30
    ITEMS = ["New", "Settings", "Help"]

    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.hovered = -1
        self.Bind(wx.EVT_PAINT,        self._paint)
        self.Bind(wx.EVT_MOTION,       self._motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hover(-1))
        # 1. Thêm sự kiện lắng nghe click chuột trái
        self.Bind(wx.EVT_LEFT_DOWN,    self._click)
        self.Bind(wx.EVT_SIZE,         lambda e: (e.Skip(), self.Refresh()))

    def _item_rects(self):
        rects = []
        x = 8
        dc = wx.ClientDC(self)
        gc = wx.GraphicsContext.Create(dc)
        gc.SetFont(gc.CreateFont(C.font(10), C.TEXT2))
        for label in self.ITEMS:
            tw, _ = text_wh(gc, label)
            rects.append((x, tw + 24))
            x += tw + 24 + 2
        return rects

    def _set_hover(self, idx):
        if self.hovered != idx:
            self.hovered = idx; self.Refresh()

    def _motion(self, e):
        for i, (rx, rw) in enumerate(self._item_rects()):
            if rx <= e.GetX() < rx + rw:
                self._set_hover(i); return
        self._set_hover(-1)

    # 2. Xử lý khi người dùng click
    def _click(self, e):
        for i, (rx, rw) in enumerate(self._item_rects()):
            # Kiểm tra xem chuột có đang click vào vùng của menu nào không
            if rx <= e.GetX() < rx + rw:
                self._show_menu(i, rx, self.H)
                return

    # 3. Tạo và hiển thị Menu sổ xuống
    def _show_menu(self, idx, x, y):
        if idx == 0:    # New
            items = ["New Connection", "-", "New Group"]
        elif idx == 1:  # Settings
            items = ["Preferences...", "Theme settings"]
        elif idx == 2:  # Help
            items = ["Documentation", "-", "About SSH Manager"]

        menu = DarkMenu(self, items)
        # Convert panel-local coordinates to screen coordinates so the popup
        # appears directly below the clicked menu item.
        screen_pos = self.ClientToScreen((int(x), int(y)))
        menu.Move(screen_pos)
        menu.Popup()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(C.MENUBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, h-1, w, C.BORDER)

        for i, (label, (rx, rw)) in enumerate(zip(self.ITEMS, self._item_rects())):
            if i == self.hovered:
                rr(gc, rx, 3, rw, h-6, 4, fill=C.HOVER)
            col = C.TEXT if i == self.hovered else C.TEXT2
            gc.SetFont(gc.CreateFont(C.font(10), col))
            tw, th = text_wh(gc, label)
            gc.DrawText(label, rx + (rw - tw)/2, (h - th)/2)

# ══════════════════════════════════════════════════════
#  NEW: TOOLBAR PANEL (+ AND x)
# ══════════════════════════════════════════════════════

class ToolBarPanel(wx.Panel):
    H = 40
    BUTTONS = ["Connect", "Disconnect", "Refresh", "Add"]

    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.hovered = -1
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_MOTION, self._motion)
        self.Bind(wx.EVT_LEFT_DOWN, self._click)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hover(-1))

    def _get_rects(self):
        # Tọa độ các ô vuông 32x32
        rects = []
        for i in range(len(self.BUTTONS)):
            rects.append((10 + i * 40, 32))
        return rects

    def _set_hover(self, idx):
        if self.hovered != idx: self.hovered = idx; self.Refresh()

    def _motion(self, e):
        for i, (rx, rw) in enumerate(self._get_rects()):
            if rx <= e.GetX() < rx + rw:
                self._set_hover(i); return
        self._set_hover(-1)

    def _click(self, e):
        for i, (rx, rw) in enumerate(self._get_rects()):
            if rx <= e.GetX() < rx + rw:
                print(f"Action: {self.BUTTONS[i]}")
                return

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        # 1. Background
        gc.SetBrush(wx.Brush(C.MENUBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, h-1, w, C.BORDER)

        for i, (name, (rx, rw)) in enumerate(zip(self.BUTTONS, self._get_rects())):
            # 2. Border & Hover
            stroke_col = C.ACCENT if i == self.hovered else C.BORDER2
            fill_col = C.HOVER if i == self.hovered else wx.Colour(0, 0, 0, 0)

            # Vẽ hình vuông chứa icon
            rr(gc, rx, 4, rw, 32, 5, fill=fill_col, stroke=stroke_col, sw=2)

            # 3. Vẽ Icon với màu sắc rõ ràng
            cx, cy = rx + rw/2, h/2

            if name == "Connect":
                # Mũi tên kết nối
                gc.SetPen(wx.Pen(C.ACCENT if i == self.hovered else C.TEXT, 4))
                gc.StrokeLine(cx-10, cy, cx+10, cy)
                gc.StrokeLine(cx+4, cy-8, cx+10, cy)
                gc.StrokeLine(cx+4, cy+8, cx+10, cy)
            elif name == "Disconnect":
                # Dấu X đỏ
                gc.SetPen(wx.Pen(C.RED, 4))
                gc.StrokeLine(cx-8, cy-8, cx+8, cy+8)
                gc.StrokeLine(cx+8, cy-8, cx-8, cy+8)
            elif name == "Refresh":
                # Mũi tên vòng tròn
                gc.SetPen(wx.Pen(C.ACCENT if i == self.hovered else C.TEXT, 4))
                gc.DrawEllipse(cx-10, cy-10, 20, 20)
                # Thêm mũi tên chỉ hướng
                gc.StrokeLine(cx+6, cy-6, cx+10, cy)
                gc.StrokeLine(cx+6, cy-6, cx+10, cy-10)
            elif name == "Add":
                # Dấu cộng
                gc.SetPen(wx.Pen(C.ACCENT if i == self.hovered else C.TEXT, 4))
                gc.StrokeLine(cx, cy-10, cx, cy+10)
                gc.StrokeLine(cx-10, cy, cx+10, cy)

# ══════════════════════════════════════════════════════
#  TITLE BAR
# ══════════════════════════════════════════════════════
class TitleBar(wx.Panel):
    H = 32
    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_SIZE,  lambda e: (e.Skip(), self.Refresh()))
        self.Bind(wx.EVT_LEFT_DOWN, self._drag_start)
        self.Bind(wx.EVT_LEFT_UP,   self._drag_end)
        self.Bind(wx.EVT_MOTION,    self._drag_move)
        self._drag = False; self._drag_pos = None

    def _drag_start(self, e):
        self._drag = True; self._drag_pos = e.GetPosition(); self.CaptureMouse()
    def _drag_end(self, e):
        self._drag = False; 
        if self.HasCapture(): self.ReleaseMouse()
    def _drag_move(self, e):
        if self._drag and e.Dragging() and e.LeftIsDown():
            frame = wx.GetTopLevelParent(self)
            pos   = frame.GetPosition()
            dp    = e.GetPosition() - self._drag_pos
            frame.Move(pos.x + dp.x, pos.y + dp.y)

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(C.TITLEBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, h-1, w, C.BORDER)

        for i, col in enumerate([wx.Colour(255,95,87), wx.Colour(255,189,46), wx.Colour(40,200,64)]):
            cx = 12 + i * 20
            gc.SetBrush(wx.Brush(col)); gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawEllipse(cx, (h-12)//2, 12, 12)

        gc.SetFont(gc.CreateFont(C.font(9), C.TEXT3))
        title = "SSH Connection Manager — v2.4.1"
        tw, th = text_wh(gc, title)
        gc.DrawText(title, (w - tw) / 2, (h - th) / 2)


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
class SidebarPanel(wx.ScrolledWindow):
    W         = 220
    ROW_H     = 32
    GROUP_H   = 30
    INDENT    = 28

    def __init__(self, parent, on_select):
        super().__init__(parent, size=(self.W, -1), style=wx.NO_BORDER)
        apply_dark_scrollbars(self)
        
        self.on_select  = on_select
        self.hovered    = None
        self.selected   = ('conn', 0, 0)
        self.expanded   = [True, True, False, False]

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetScrollRate(0, 1)
        self.EnableScrolling(False, True)

        self.Bind(wx.EVT_PAINT,        self._paint)
        self.Bind(wx.EVT_SIZE,         lambda e: (e.Skip(), self._recalc(), self.Refresh()))
        self.Bind(wx.EVT_MOTION,       self._motion)
        self.Bind(wx.EVT_LEFT_DOWN,    self._click)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hov(None))
        self._recalc()

    def _recalc(self):
        total = 8
        self._layout = []
        for gi, (gname, _, conns) in enumerate(GROUPS):
            self._layout.append(('group', gi, total))
            total += self.GROUP_H
            if self.expanded[gi]:
                for ci, conn in enumerate(conns):
                    self._layout.append(('conn', gi, ci, total))
                    total += self.ROW_H
        total += 8
        w, _ = self.GetClientSize()
        self.SetVirtualSize(w, total)

    def _set_hov(self, h):
        if self.hovered != h: self.hovered = h; self.Refresh()

    def _motion(self, e):
        _, sy = self.GetViewStart()
        y = e.GetY() + sy
        for item in self._layout:
            if item[0] == 'group':
                _, gi, iy = item
                if iy <= y < iy + self.GROUP_H:
                    self._set_hov(('group', gi)); return
            else:
                _, gi, ci, iy = item
                if iy <= y < iy + self.ROW_H:
                    self._set_hov(('conn', gi, ci)); return
        self._set_hov(None)

    def _click(self, e):
        _, sy = self.GetViewStart()
        y = e.GetY() + sy
        for item in self._layout:
            if item[0] == 'group':
                _, gi, iy = item
                if iy <= y < iy + self.GROUP_H:
                    self.expanded[gi] = not self.expanded[gi]
                    self._recalc(); self.Refresh(); return
            else:
                _, gi, ci, iy = item
                if iy <= y < iy + self.ROW_H:
                    self.selected = ('conn', gi, ci)
                    self.Refresh()
                    conn_id = GROUPS[gi][2][ci][1]
                    name    = GROUPS[gi][2][ci][0]
                    self.on_select(conn_id, name)
                    return

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        cw, ch = self.GetClientSize()
        _, sy = self.GetViewStart()

        gc.SetBrush(wx.Brush(C.SIDEBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, cw, ch)

        for item in self._layout:
            if item[0] == 'group':
                _, gi, iy = item
                ry = iy - sy
                if ry + self.GROUP_H < 0 or ry > ch: continue
                gname, expanded_default, _ = GROUPS[gi]

                if self.hovered == ('group', gi):
                    gc.SetBrush(wx.Brush(C.HOVER)); gc.SetPen(wx.TRANSPARENT_PEN)
                    gc.DrawRectangle(0, ry, cw, self.GROUP_H)

                chevron = "▾" if self.expanded[gi] else "▸"
                gc.SetFont(gc.CreateFont(C.font(8), C.TEXT3))
                cw2, ch2 = text_wh(gc, chevron)
                gc.DrawText(chevron, 10, ry + (self.GROUP_H - ch2)/2)

                gc.SetFont(gc.CreateFont(C.font(8, bold=True), C.TEXT3))
                lw, lh = text_wh(gc, gname.upper())
                gc.DrawText(gname.upper(), 22, ry + (self.GROUP_H - lh)/2)

            else:
                _, gi, ci, iy = item
                ry = iy - sy
                if ry + self.ROW_H < 0 or ry > ch: continue
                name, conn_id, tag = GROUPS[gi][2][ci]
                is_sel = self.selected == ('conn', gi, ci)
                is_hov = self.hovered  == ('conn', gi, ci)
                conn   = CONNECTIONS.get(conn_id, {})
                dot_col = DOT_COLORS.get(conn.get('sc','gray'), C.GRAY_DOT)

                if is_sel:
                    gc.SetBrush(wx.Brush(C.SEL)); gc.SetPen(wx.TRANSPARENT_PEN)
                    gc.DrawRectangle(0, ry, cw, self.ROW_H)
                    gc.SetBrush(wx.Brush(C.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
                    gc.DrawRectangle(0, ry, 2, self.ROW_H)
                elif is_hov:
                    gc.SetBrush(wx.Brush(C.HOVER)); gc.SetPen(wx.TRANSPARENT_PEN)
                    gc.DrawRectangle(0, ry, cw, self.ROW_H)

                gc.SetBrush(wx.Brush(dot_col)); gc.SetPen(wx.TRANSPARENT_PEN)
                gc.DrawEllipse(self.INDENT, ry + (self.ROW_H-6)//2, 6, 6)

                name_col = C.ACCENT if is_sel else (C.TEXT if is_hov else C.TEXT2)
                gc.SetFont(gc.CreateFont(C.font(10), name_col))
                _, nh = text_wh(gc, name)
                gc.DrawText(name, self.INDENT + 12, ry + (self.ROW_H - nh)/2)

                gc.SetFont(gc.CreateFont(C.font(8), C.TEXT3))
                tw, th = text_wh(gc, tag)
                pill_x = cw - tw - 16
                rr(gc, pill_x - 4, ry + (self.ROW_H-th-4)//2, tw+8, th+4, 3, fill=wx.Colour(46,46,66))
                gc.SetFont(gc.CreateFont(C.font(8), C.TEXT3))
                gc.DrawText(tag, pill_x, ry + (self.ROW_H-th)//2)

        vline(gc, cw-1, 0, ch, C.BORDER)


# ══════════════════════════════════════════════════════
#  CODE / EDITOR AREA
# ══════════════════════════════════════════════════════
class CodeArea(stc.StyledTextCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        apply_dark_scrollbars(self)
        self.conn_id = 'prod-web'
        self.name    = 'web-server-01'

        # Theme settings
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, C.CODE_BG)
        self.StyleSetForeground(stc.STC_STYLE_DEFAULT, C.TEXT)
        self.StyleClearAll()  # Đảm bảo tất cả styles kế thừa màu nền tối
        self.SetSelBackground(True, C.SEL)
        self.SetCaretForeground(C.ACCENT)

        # Highlight current line
        self.SetCaretLineVisible(True)
        self.SetCaretLineBackground(wx.Colour(31, 31, 46))
        
        # Margins (Line Numbers)
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 40)
        self.StyleSetBackground(stc.STC_STYLE_LINENUMBER, wx.Colour(20, 20, 28))
        self.StyleSetForeground(stc.STC_STYLE_LINENUMBER, C.TEXT4)

        # Syntax Highlighting Styles
        self.StyleSetForeground(1, C.SYN_COMMENT)
        self.StyleSetForeground(2, C.SYN_STR)
        self.StyleSetForeground(3, C.SYN_KW)
        self.StyleSetBold(3, True)
        self.StyleSetForeground(4, C.SYN_PARAM)
        self.StyleSetForeground(5, C.SYN_OP)
        self.StyleSetForeground(6, C.SYN_IP)
        self.StyleSetForeground(7, C.SYN_NUM)

        # Font
        font = C.font(10, mono=True)
        for i in range(32):
            self.StyleSetFont(i, font)

        # Autocomplete settings
        self.AutoCompSetIgnoreCase(True)
        self.AutoCompSetSeparator(ord(' '))
        self.completion_list = sorted([
            "connect", "run", "password", "key", "localhost",
            "/ssh", "/tcp", "/pgsql", "/mysql", "/auth", "/user", "/passwd",
            "/timeout", "/keepalive", "/L", "/background", "/log", "/identity"
        ])

        self.Bind(stc.EVT_STC_CHANGE, self.on_change)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_char_added)

    def apply_styling(self):
        text = self.GetText()
        if not text: return
        
        # Reset styling
        self.StartStyling(0)
        self.SetStyling(len(text.encode('utf-8')), 0)

        # Unified regex (1:comment, 2:string, 3:keyword, 4:param, 5:op, 6:ip, 7:num)
        regex = r'(#.*)|(\'[^\']*\'|"[^"]*")|\b(connect|run)\b|(/[a-zA-Z0-9]+)|([:=])|(\d{1,3}(?:\.\d{1,3}){3})|(\b\d+\b)'
        
        for match in re.finditer(regex, text):
            group_idx = match.lastindex
            if group_idx:
                start = len(text[:match.start(group_idx)].encode('utf-8'))
                end = len(text[:match.end(group_idx)].encode('utf-8'))
                self.StartStyling(start)
                self.SetStyling(end - start, group_idx)

    def set_conn(self, conn_id, name):
        self.conn_id = conn_id
        self.name = name
        c = CONNECTIONS.get(self.conn_id, CONNECTIONS['prod-web'])
        
        text = (f"# SSH Connection Manager — config script\n\n"
                f"# Target: {self.name} (Production)\n"
                f"# Protocol: {c['proto'].replace('/','').upper()} / Auth: {c['auth'].capitalize()}\n\n"
                f"connect '{c['ip']}:{c['port']}' {c['proto']} /2 /auth={c['auth']} /user={c['user']} /passwd=****\n\n"
                f"# Optional parameters\n"
                f"/timeout=30  /keepalive=60\n\n"
                f"# Tunnel / port-forward\n"
                f"/L=8080:localhost:80\n\n"
                f"# Identity / key override (optional)\n"
                f"# /identity=\"C:\\Users\\admin\\.ssh\\id_rsa\"\n\n"
                f"run /background /log=\"session.log\"")
        
        self.SetText(text)
        self.apply_styling()

    def on_char_added(self, event):
        pos = self.GetCurrentPos()
        # Lấy vị trí bắt đầu của từ hiện tại (bao gồm cả dấu / nếu có)
        start_pos = self.WordStartPosition(pos, True)
        if start_pos > 0 and self.GetCharAt(start_pos - 1) == ord('/'):
            start_pos -= 1
            
        word = self.GetTextRange(start_pos, pos)
        if len(word) >= 2 or (len(word) == 1 and word == '/'):
            if not self.AutoCompActive():
                self.AutoCompShow(len(word), " ".join(self.completion_list))

    def on_change(self, event):
        self.apply_styling()
        text = self.GetText()
        c = CONNECTIONS.get(self.conn_id)
        if not c: return

        # Parse text to update CONNECTIONS dict
        # 1. IP and Port
        ip_match = re.search(r"connect\s+'([^:]+):(\d+)'", text)
        if ip_match:
            c['ip'], c['port'] = ip_match.group(1), ip_match.group(2)
            
        # 2. Protocol (after IP:PORT)
        proto_match = re.search(r"connect\s+'[^']+'\s+(/[a-z]+)", text)
        if proto_match:
            c['proto'] = proto_match.group(1)
            
        # 3. User
        user_match = re.search(r"/user=([^\s/]+)", text)
        if user_match:
            c['user'] = user_match.group(1)
            
        # 4. Auth
        auth_match = re.search(r"/auth=([^\s/]+)", text)
        if auth_match:
            c['auth'] = auth_match.group(1)

        # Update UI components that depend on CONNECTIONS
        editor = self.GetParent()
        if hasattr(editor, 'info'):
            editor.info.Refresh()
            
        frame = self.GetTopLevelParent()
        if hasattr(frame, 'statusbar_'):
            frame.statusbar_.Refresh()
        
        if hasattr(frame, 'sidebar'):
            frame.sidebar.Refresh()


# ══════════════════════════════════════════════════════
#  TAB BAR
# ══════════════════════════════════════════════════════
class TabBar(wx.Panel):
    H = 34
    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.tab_label = "web-server-01"
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_SIZE,  lambda e: (e.Skip(), self.Refresh()))

    def set_label(self, lbl):
        self.tab_label = lbl; self.Refresh()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(C.TAB_BG)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, h-1, w, C.BORDER)

        x = 8
        gc.SetFont(gc.CreateFont(C.font(10), C.ACCENT))
        tw, th = text_wh(gc, self.tab_label)
        TAB_W = tw + 36

        gc.SetBrush(wx.Brush(C.GREEN)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawEllipse(x + 8, (h-5)//2, 5, 5)
        gc.SetFont(gc.CreateFont(C.font(10), C.ACCENT))
        gc.DrawText(self.tab_label, x + 20, (h - th)/2)
        gc.SetBrush(wx.Brush(C.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(x, h-2, TAB_W, 2)
        gc.SetFont(gc.CreateFont(C.font(11), C.TEXT3))
        gc.DrawText("+", x + TAB_W + 10, (h - th)/2)


# ══════════════════════════════════════════════════════
#  INFO PANEL
# ══════════════════════════════════════════════════════
class InfoPanel(wx.Panel):
    H = 52
    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.conn_id = 'prod-web'
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_SIZE,  lambda e: (e.Skip(), self.Refresh()))

    def set_conn(self, conn_id):
        self.conn_id = conn_id; self.Refresh()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(C.INFO_BG)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, 0, w, C.BORDER)

        c    = CONNECTIONS.get(self.conn_id, CONNECTIONS['prod-web'])
        auth_col   = C.GREEN if c['auth'] == 'key' else C.AMBER
        status_col = {'Active': C.GREEN, 'Idle': C.GREEN, 'Offline': C.GRAY_DOT,
                      'Error': C.RED}.get(c['status'], C.TEXT2)

        fields = [
            ("HOST",     f"{c['ip']}:{c['port']}", C.ACCENT),
            ("PROTOCOL", c['proto'].replace('/','').upper() + " v2", C.ACCENT),
            ("AUTH",     c['auth'].capitalize(), auth_col),
            ("USER",     c['user'], C.ACCENT),
            ("STATUS",   "● " + c['status'], status_col),
        ]

        x = 20
        for label, value, vcol in fields:
            gc.SetFont(gc.CreateFont(C.font(8, bold=True), C.TEXT4))
            gc.DrawText(label, x, 10)
            gc.SetFont(gc.CreateFont(C.font(10, mono=True), vcol))
            vw, vh = text_wh(gc, value)
            gc.DrawText(value, x, 26)
            x += max(vw + 30, 90)


# ══════════════════════════════════════════════════════
#  STATUS BAR
# ══════════════════════════════════════════════════════
class StatusBar(wx.Panel):
    H = 22
    def __init__(self, parent):
        super().__init__(parent, size=(-1, self.H))
        self.conn_name = "web-server-01"
        self.mem_val   = 42.0
        self.connected = 3
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_SIZE,  lambda e: (e.Skip(), self.Refresh()))
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._tick, self._timer)
        self._timer.Start(3000)

    def _tick(self, e):
        self.mem_val = max(28, min(85, self.mem_val + random.uniform(-2, 2)))
        self.Refresh()

    def set_conn(self, name):
        self.conn_name = name; self.Refresh()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()
        gc.SetBrush(wx.Brush(C.STATUSBAR)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        hline(gc, 0, 0, w, C.BORDER)

        f9 = C.font(9)
        def sb_text(txt, col, x):
            gc.SetFont(gc.CreateFont(f9, col))
            tw, th = text_wh(gc, txt)
            gc.DrawText(txt, x, (h - th)/2)
            return x + tw

        x = 0
        label = " SSH Manager  "
        gc.SetFont(gc.CreateFont(f9, C.ACCENT))
        lw, _ = text_wh(gc, label)
        gc.SetBrush(wx.Brush(wx.Colour(30,32,58))); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, lw, h)
        sb_text(label, C.ACCENT, 0)
        x = lw
        vline(gc, x, 0, h, C.BORDER2); x += 1

        seg = f"  ⦁ {self.connected} connected  "
        x2  = sb_text(seg, C.TEXT2, x)
        vline(gc, x2, 0, h, C.BORDER2)

        mem_str = f"  CPU  {int(self.mem_val)} MB  "
        gc.SetFont(gc.CreateFont(f9, C.TEXT2))
        mw, mh = text_wh(gc, mem_str)
        gc.DrawText("  CPU  ", x2 + 1, (h - mh)/2)
        tw2, _ = text_wh(gc, "  CPU  ")
        bar_x = x2 + 1 + tw2
        gc.SetBrush(wx.Brush(wx.Colour(42,42,58))); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(bar_x, (h-4)//2, 50, 4, 2)
        fw = int(50 * self.mem_val / 100)
        gc.SetBrush(wx.Brush(C.ACCENT)); gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(bar_x, (h-4)//2, fw, 4, 2)
        mb_str = f"  {int(self.mem_val)} MB  "
        mb_w, _ = text_wh(gc, mb_str)
        mb_x = bar_x + 54
        gc.DrawText(mb_str, mb_x, (h - mh)/2)
        vline(gc, mb_x + mb_w, 0, h, C.BORDER2)

        now = datetime.datetime.now().strftime("%H:%M")
        time_str = f"  {now}  "
        tw_t, th_t = text_wh(gc, time_str)
        gc.DrawText(time_str, w - tw_t, (h - th_t)/2)
        vline(gc, w - tw_t - 1, 0, h, C.BORDER2)

        notify = f" Connected to {self.conn_name}  "
        gc.SetFont(gc.CreateFont(f9, C.AMBER))
        tw_n, th_n = text_wh(gc, notify)
        gc.DrawText(notify, w - tw_t - tw_n - 2, (h - th_n)/2)
        vline(gc, w - tw_t - tw_n - 2, 0, h, C.BORDER2)


# ══════════════════════════════════════════════════════
#  EDITOR AREA (tabbar + code + info)
# ══════════════════════════════════════════════════════
class EditorArea(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(C.EDITOR_BG)

        self.tab_bar  = TabBar(self)
        self.code     = CodeArea(self)
        self.info     = InfoPanel(self)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.tab_bar, 0, wx.EXPAND)
        s.Add(self.code,    1, wx.EXPAND)
        s.Add(self.info,    0, wx.EXPAND)
        self.SetSizer(s)

    def set_conn(self, conn_id, name):
        self.tab_bar.set_label(name)
        self.code.set_conn(conn_id, name)
        self.info.set_conn(conn_id)


# ══════════════════════════════════════════════════════
#  MAIN FRAME
# ══════════════════════════════════════════════════════
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="SSH Connection Manager",
                         size=(900, 600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((720, 480))
        self.SetBackgroundColour(C.APP_BG)

        outer = wx.BoxSizer(wx.VERTICAL)

        self.titlebar = TitleBar(self)
        self.menubar_ = MenuBarPanel(self)
        self.toolbar_ = ToolBarPanel(self)  # THÊM TOOLBAR VÀO ĐÂY


        self.sidebar  = SidebarPanel(self, self._on_select)
        self.editor   = EditorArea(self)

        main_row = wx.BoxSizer(wx.HORIZONTAL)
        main_row.Add(self.sidebar, 0, wx.EXPAND)
        main_row.Add(self.editor,  1, wx.EXPAND)

        self.statusbar_ = StatusBar(self)

        # Trong sizer:
        outer.Add(self.titlebar,   0, wx.EXPAND)
        outer.Add(self.menubar_,   0, wx.EXPAND)
        outer.Add(self.toolbar_,   0, wx.EXPAND) # CHÈN TOOLBAR SAU MENUBAR
        outer.Add(main_row,        1, wx.EXPAND)
        outer.Add(self.statusbar_, 0, wx.EXPAND)

        self.SetSizer(outer)
        self._on_select('prod-web', 'web-server-01')
        self.Centre()
        
        apply_dark_titlebar(self)
        self.Show()

    def _on_select(self, conn_id, name):
        self.editor.set_conn(conn_id, name)
        self.statusbar_.set_conn(name)


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame()
    app.MainLoop()
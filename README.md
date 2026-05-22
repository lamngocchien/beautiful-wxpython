# SSH Connection Manager

![SSH Connection Manager Screenshot](Screenshot%202026-05-23%20044430.png)

A collection of beautiful wxPython applications with fully custom-painted UI, demonstrating modern dark-themed interfaces with smooth animations and pixel-perfect design.

## Features

- **SSH Connection Manager**: A fully custom-painted SSH client interface with:
  - Dark theme with accent colors
  - Connection grouping and status indicators
  - Custom code editor with syntax highlighting
  - Interactive toolbar and menu system
  - Windows dark mode integration

- **Desktop Tool**: A modern desktop application with:
  - Native OS integration
  - Dark/light mode toggle
  - Sidebar navigation
  - Custom-painted components

## Applications Included

1. **SSH Connection Manager** (`ssh_manager.py`, `app3.py`, `app4.py`, `app5.py`)
   - A sophisticated SSH client UI with connection management
   - Features custom-drawn components including:
     - Sidebar with expandable groups
     - Code editor with syntax highlighting
     - Status bar with real-time updates
     - Custom popup menus

2. **Desktop Tool** (`app.py`, `desktop_tool_painted.py`, `app2.py`)
   - A modern desktop application framework
   - Includes both native and custom-painted versions
   - Features:
     - Dark/light mode switching
     - Sidebar navigation
     - Dashboard with statistics
     - File management interface
     - Settings panel

## Technical Highlights

- **Fully Custom-Painted UI**: All components are drawn using `wx.GraphicsContext` for pixel-perfect control
- **Dark Mode Support**: Complete dark theme implementation with proper contrast ratios
- **Windows Integration**: Native dark mode support for title bars and scrollbars
- **Modern UI Patterns**: Includes hover effects, smooth animations, and responsive layouts
- **Code Editor**: Custom syntax-highlighted editor for connection scripts
- **Component Library**: Reusable custom components like:
  - Dark-themed menus and toolbars
  - Custom list controls
  - Stat cards with accent colors
  - Flat and ghost buttons

## Requirements

- Python 3.6+
- wxPython 4.1+

## Installation

```bash
pip install -r requirements.txt
```

## Running the Applications

Each application can be run directly:

```bash
python ssh_manager.py
python app.py
python desktop_tool_painted.py
```

## Author

**Lam Ngoc Chien** and A.I
- GitHub: [https://github.com/lamngocchien/beautiful-wxpython](https://github.com/lamngocchien/beautiful-wxpython)
- Created: May 2026

## License

This project is open source and available under the [MIT License](LICENSE).
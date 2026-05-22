# SSH Connection Manager (UI Demo)

Pixel-faithful UI template recreation of SSH Connection Manager with fully custom-painted wxPython interface. This is a visual demonstration only - no actual SSH functionality is implemented.

![SSH Connection Manager Screenshot](Screenshot%202026-05-23%20044430.png)

## Features (UI Demonstration)

- **Dark Mode UI**: Fully custom-drawn interface with dark theme
- **Visual Connection Management**:
  - Grouped connection display (Production, Staging, Dev, Cloud)
  - Status indicators (Active, Idle, Offline, Error)
  - Config script editor with syntax highlighting (visual only)
- **Custom UI Components**:
  - Draggable title bar with window controls
  - Collapsible sidebar with connection groups
  - Toolbar with Connect/Disconnect/Refresh/Add buttons (non-functional)
  - Status bar with simulated system metrics
- **Windows Integration**:
  - Dark mode scrollbars
  - Immersive dark title bar
  - Configurable sash position
- **Config Editor (Visual Only)**:
  - Syntax highlighting for SSH command format
  - Auto-completion for parameters (demonstration)

## System Requirements

- Windows 10/11 (with dark mode support)
- Python 3.8+
- wxPython 4.2+

## Installation

```bash
git clone [repository-url]
cd beautiful-wxpython-main
pip install -r requirements.txt
python app5.py
```

## Usage (UI Demonstration)

1. **Navigation**:
   - Click menu items to see visual feedback
   - Expand/collapse connection groups in sidebar
   - Select connections to view template config

2. **Visual Interaction**:
   - Toolbar buttons provide visual feedback only
   - Code editor displays template SSH configuration
   - Info panel shows simulated connection status

3. **Keyboard Shortcuts**:
   - `Ctrl+B`: Toggle sidebar visibility (functional)

## Configuration Template

The code editor displays a template SSH configuration (not functional):
```bash
connect '192.168.2.18:22' /ssh /2 /auth=password /user=admin /passwd=****
/timeout=30 /keepalive=60
/L=8080:localhost:80
```

## Version

2.4.1

## License

[MIT License](LICENSE)
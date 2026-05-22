# SSH Connection Manager

Pixel-faithful recreation of SSH Connection Manager with fully custom-painted wxPython interface.

![SSH Connection Manager Screenshot](https://i.imgur.com/ssh_manager_screenshot.png)

## Features

- **Dark Mode UI**: Fully custom-drawn interface with dark theme
- **Multi-protocol Support**: SSH, TCP, PostgreSQL, MySQL connections
- **Connection Management**:
  - Group connections (Production, Staging, Dev, Cloud)
  - Status indicators (Active, Idle, Offline, Error)
  - Config script editor with syntax highlighting
- **Custom Components**:
  - Draggable title bar with window controls
  - Collapsible sidebar with connection groups
  - Toolbar with Connect/Disconnect/Refresh/Add buttons
  - Status bar with system metrics
- **Windows Integration**:
  - Dark mode scrollbars
  - Immersive dark title bar
  - Configurable sash position
- **Config Editor**:
  - Syntax highlighting for SSH commands
  - Auto-completion for parameters
  - Real-time connection status updates

## System Requirements

- Windows 10/11 (with dark mode support)
- Python 3.8+
- wxPython 4.2+

## Installation

```bash
git clone [repository-url]
cd ssh-connection-manager
pip install -r requirements.txt
python app5.py
```

## Usage

1. **Navigation**:
   - Click menu items (New, Settings, Help)
   - Expand/collapse connection groups in sidebar
   - Select connections to view/edit config

2. **Connection Management**:
   - Use toolbar buttons to Connect/Disconnect/Refresh
   - Edit connection parameters in the code editor
   - View connection status in the info panel

3. **Keyboard Shortcuts**:
   - `Ctrl+B`: Toggle sidebar visibility

## Configuration

Edit the connection parameters in the code editor:
```bash
connect '192.168.2.18:22' /ssh /2 /auth=password /user=admin /passwd=****
/timeout=30 /keepalive=60
/L=8080:localhost:80
```

## Version

2.4.1

## License

[MIT License](LICENSE)
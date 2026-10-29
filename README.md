# AutoClicker

A desktop autoclicker for Windows 10/11 built with PySide6. The interface starts in English; Spanish is available in the language selector.

## Installation
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Global hotkeys
- F6: start or resume
- F7: pause
- F8: stop
- Ctrl+Alt+F9: emergency stop
- F10: capture coordinates with a countdown

Hotkeys can be edited in the application. The red emergency-stop button is an alternative; the global shortcut works even when the window is not focused. Test the shortcuts with a short run before using the app in a real task.

## Features
- Left, right, or middle mouse button.
- One speed setting: clicks per second (CPS), from 0.1 to 100.
- Speed can be changed while stopped or paused; it is locked while clicks are actively running and takes effect when resumed.
- Limited or unlimited click count.
- Initial delay and fixed/current cursor position.
- Coordinate capture countdown.
- Light and dark themes; English and Spanish interface.
- Preferences saved locally.
- Reset statistics without changing settings or hotkeys.
- Restore default settings.
- Code comments and docstrings describe the role of the main modules and important methods.

## Qt DPI notice
`SetProcessDpiAwarenessContext() failed: Access denied` can appear if Windows has already set the process DPI context and Qt cannot change it later. If the app opens, this does not necessarily mean it has failed. This project does not suppress the notice or force a DPI policy without knowing the system context.

## Current limitations
- Multiple profiles, system tray support, and macros are reserved for future iterations.
- Windows scheduling affects interval accuracy; this is not hard real-time software.
- Some elevated applications may block interaction from a process without equivalent privileges. Run as administrator only if necessary.
- Use automation only where it is permitted.

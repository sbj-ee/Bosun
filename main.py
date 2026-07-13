"""Entry point: launches the Bosun tray app."""

import os
import sys

from bosun.tray_app import BosunTrayApp

# Qt's native Wayland backend has incomplete QSystemTrayIcon support (tray
# context menus can fail to appear on compositors like GNOME or COSMIC).
# Routing through XWayland instead makes the tray menu reliable. This app's
# whole interface is the tray menu, so it always wins over the ambient
# QT_QPA_PLATFORM (which may list "wayland" first, e.g. "wayland;xcb").
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"


def main() -> int:
    app = BosunTrayApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())

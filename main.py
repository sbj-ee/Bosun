"""Entry point: launches the Bosun tray app."""

from bosun.tray_app import BosunTrayApp


def main() -> int:
    app = BosunTrayApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())

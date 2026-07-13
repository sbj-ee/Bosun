"""System tray application: strikes ship's bells or a plain hourly whistle."""

import sys
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .player import ring_bells, ring_whistle
from .watch import bell_count, last_half_hour_mark, watch_name

_ICON_PATH = Path(__file__).resolve().parent / "resources" / "uss_wisconsin_bb64_crest.png"


class ChimeMode(Enum):
    SHIPS_BELLS = auto()   # full 1-8 bell pattern, every half hour
    HOURLY_WHISTLE = auto()  # single whistle blast, on the hour only


def _build_icon() -> QIcon:
    return QIcon(str(_ICON_PATH))


class BosunTrayApp:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.enabled = True
        self.mode = ChimeMode.SHIPS_BELLS
        self.use_real_audio = False

        self.tray = QSystemTrayIcon(_build_icon())
        self.tray.setToolTip("Bosun")

        menu = self.menu = QMenu()

        self.enabled_action = QAction("Chiming Enabled", checkable=True, checked=True)
        self.enabled_action.toggled.connect(self._on_toggle_enabled)
        menu.addAction(self.enabled_action)

        menu.addSeparator()

        mode_group = QActionGroup(menu)
        mode_group.setExclusive(True)

        self.bells_action = QAction("Ship's Bells (half-hourly)", checkable=True, checked=True)
        self.bells_action.triggered.connect(lambda: self._on_select_mode(ChimeMode.SHIPS_BELLS))
        mode_group.addAction(self.bells_action)
        menu.addAction(self.bells_action)

        self.whistle_action = QAction("Hourly Whistle Only", checkable=True)
        self.whistle_action.triggered.connect(lambda: self._on_select_mode(ChimeMode.HOURLY_WHISTLE))
        mode_group.addAction(self.whistle_action)
        menu.addAction(self.whistle_action)

        menu.addSeparator()

        audio_group = QActionGroup(menu)
        audio_group.setExclusive(True)

        self.synth_audio_action = QAction("Synthesized Audio", checkable=True, checked=True)
        self.synth_audio_action.triggered.connect(lambda: self._on_select_audio_source(False))
        audio_group.addAction(self.synth_audio_action)
        menu.addAction(self.synth_audio_action)

        self.real_audio_action = QAction("Real Recordings (Navy Band / Ship's Bell)", checkable=True)
        self.real_audio_action.triggered.connect(lambda: self._on_select_audio_source(True))
        audio_group.addAction(self.real_audio_action)
        menu.addAction(self.real_audio_action)

        menu.addSeparator()

        self.test_action = QAction("Ring Now (test)")
        self.test_action.triggered.connect(self._ring_test)
        menu.addAction(self.test_action)

        menu.addSeparator()

        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.app.quit)
        menu.addAction(self.quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._on_tick)
        self._schedule_next()

    def _on_toggle_enabled(self, checked: bool) -> None:
        self.enabled = checked

    def _on_select_mode(self, mode: ChimeMode) -> None:
        self.mode = mode
        self._schedule_next()

    def _on_select_audio_source(self, use_real: bool) -> None:
        self.use_real_audio = use_real

    def _ring_test(self) -> None:
        self._strike(last_half_hour_mark(datetime.now()))

    def _strike(self, mark: datetime) -> None:
        if self.mode == ChimeMode.SHIPS_BELLS:
            count = bell_count(mark)
            ring_bells(count, use_real=self.use_real_audio)
            self.tray.setToolTip(f"Bosun — {watch_name(mark)}, {count} bell(s)")
        else:
            ring_whistle(use_real=self.use_real_audio)
            self.tray.setToolTip(f"Bosun — {mark.strftime('%H:%M')} whistle")

    def _schedule_next(self) -> None:
        now = datetime.now()
        if self.mode == ChimeMode.SHIPS_BELLS:
            next_tick = now.replace(minute=30, second=0, microsecond=0) if now.minute < 30 else (
                now + timedelta(hours=1)
            ).replace(minute=0, second=0, microsecond=0)
        else:
            next_tick = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        ms = int((next_tick - now).total_seconds() * 1000)
        self.timer.start(max(ms, 0))

    def _on_tick(self) -> None:
        if self.enabled:
            self._strike(datetime.now())
        self._schedule_next()

    def run(self) -> int:
        return self.app.exec()

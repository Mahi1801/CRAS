import time
import psutil
from datetime import datetime
from pynput import mouse, keyboard
from threading import Lock


class ActivityTracker:
    def __init__(self, idle_threshold=60):
        self.idle_threshold = idle_threshold
        self.last_activity_time = time.time()
        self.lock = Lock()

        self.mouse_listener = None
        self.keyboard_listener = None

        # Activity counters (reset every snapshot)
        self.click_count = 0
        self.key_count = 0

        self._start_listeners()

    # -------------------- Event handlers --------------------
    def _on_click(self, x, y, button, pressed):
        if pressed:  # only count press, not release
            with self.lock:
                self.last_activity_time = time.time()
                self.click_count += 1

    def _on_press(self, key):
        with self.lock:
            self.last_activity_time = time.time()
            self.key_count += 1

    def _on_activity(self, *args):
        """Mouse move or scroll"""
        with self.lock:
            self.last_activity_time = time.time()

    def _start_listeners(self):
        self.mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_click,
            on_scroll=self._on_activity
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()

    # -------------------- Window detection --------------------
    def get_active_window(self):
        """Get currently focused application (Windows)"""
        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)

            return {
                "app": process.name(),
                "title": win32gui.GetWindowText(hwnd)
            }
        except Exception:
            return {
                "app": "Unknown",
                "title": "Could not detect window"
            }

    def is_idle(self) -> bool:
        with self.lock:
            idle_seconds = time.time() - self.last_activity_time
            return idle_seconds > self.idle_threshold

    # -------------------- Main snapshot --------------------
    def take_snapshot(self) -> dict:
        window = self.get_active_window()
        idle = self.is_idle()

        with self.lock:
            clicks = self.click_count
            keys = self.key_count
            # Reset counters for next interval
            self.click_count = 0
            self.key_count = 0

        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "app": window["app"],
            "title": window["title"],
            "status": "Idle" if idle else "Active",
            "clicks": clicks,
            "keys": keys
        }
        return snapshot

    def stop(self):
        """Cleanly stop listeners"""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
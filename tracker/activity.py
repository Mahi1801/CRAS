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

        # Start listening to mouse and keyboard
        self._start_listeners()

    def _on_activity(self, *args):
        """Called whenever mouse or keyboard is used"""
        with self.lock:
            self.last_activity_time = time.time()

    def _start_listeners(self):
        self.mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_activity,
            on_scroll=self._on_activity
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_activity
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def get_active_window(self):
        """Get the currently active application name (Windows focused)"""
        try:
            # Works best on Windows
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name()
            window_title = win32gui.GetWindowText(hwnd)

            return {
                "app": app_name,
                "title": window_title
            }
        except Exception:
            # Fallback if win32 is not available
            return {
                "app": "Unknown",
                "title": "Could not detect window"
            }

    def is_idle(self):
        """Check if user has been idle longer than threshold"""
        with self.lock:
            idle_time = time.time() - self.last_activity_time
            return idle_time > self.idle_threshold

    def take_snapshot(self):
        """Take one complete activity snapshot"""
        window = self.get_active_window()
        idle = self.is_idle()

        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "app": window["app"],
            "title": window["title"],
            "status": "Idle" if idle else "Active"
        }
        return snapshot

    def stop(self):
        """Stop the listeners cleanly"""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
from threading import Lock
from pynput import keyboard

class PauseManager:
    def __init__(self, hotkey="ctrl+alt+p", enabled=True):
        self.enabled = enabled
        self.paused = False
        self.lock = Lock()
        self.hotkey = hotkey
        self.listener = None

        if self.enabled:
            self._start_hotkey_listener()

    def _start_hotkey_listener(self):
        # Map string to pynput format
        mapping = {
            "ctrl+alt+p": {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('p')}
        }
        # For simplicity we use a fixed hotkey first. You can expand later.
        def on_activate():
            self.toggle()

        self.listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+p': on_activate
        })
        self.listener.start()

    def toggle(self):
        with self.lock:
            self.paused = not self.paused
            state = "PAUSED ⏸️" if self.paused else "RESUMED ▶️"
            print(f"\n>>> Tracking {state}\n")

    def is_paused(self) -> bool:
        with self.lock:
            return self.paused

    def stop(self):
        if self.listener:
            self.listener.stop()
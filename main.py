import time
import yaml
from datetime import datetime

from tracker.activity import ActivityTracker
from tracker.document import DocumentGenerator
from tracker.cloud import CloudSync
from tracker.pause import PauseManager
from tracker.browser_receiver import start_browser_server, browser_state


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=" * 55)
    print("  CRAS – Continuous Work Activity Tracker")
    print("=" * 55)
    print("Press Ctrl+C to stop")
    print("Press Ctrl+Alt+P to Pause / Resume\n")

    config = load_config()

    interval = config.get("snapshot_interval_seconds", 10)
    idle_threshold = config.get("idle_threshold_seconds", 60)
    log_folder = config.get("log_folder", "logs")

    # Cloud interval
    cloud_cfg = config.get("cloud", {})
    sync_every = cloud_cfg.get("sync_interval_minutes", 15) * 60

    # ---------- Initialize components ----------
    tracker = ActivityTracker(idle_threshold=idle_threshold)

    doc_gen = DocumentGenerator(
        log_folder=log_folder,
        snapshot_interval=interval
    )

    cloud = CloudSync(config)

    pause_manager = PauseManager(
        enabled=config.get("enable_pause", True)
    )

    # Start local server for browser extension
    start_browser_server(port=8765)
    print("Browser receiver listening on http://127.0.0.1:8765")

    # Load today's existing history so we never lose data
    snapshots = doc_gen.load_existing_snapshots()
    print(f"Loaded {len(snapshots)} existing snapshots from today.\n")

    last_sync_time = time.time()

    try:
        while True:
            # ----- Pause check -----
            if pause_manager.is_paused():
                time.sleep(interval)
                continue

            # ----- Take snapshot -----
            snapshot = tracker.take_snapshot()

            # Merge browser data if available
            browser = browser_state.get()
            if browser and snapshot["app"].lower() in [
                "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"
            ]:
                active = browser.get("active")
                if active:
                    snapshot["browser_title"] = active.get("title", "")
                    snapshot["browser_url"] = active.get("url", "")
                snapshot["open_tabs"] = len(browser.get("tabs", []))

            # 1. Append to disk immediately (never lose history)
            doc_gen.append_snapshot(snapshot)

            # 2. Keep in memory for summary
            snapshots.append(snapshot)

            # 3. Rebuild Markdown
            doc_gen.rebuild_markdown(snapshots)

            # Live status
            icon = "🟢" if snapshot["status"] == "Active" else "⚪"
            extra = ""
            if "browser_url" in snapshot:
                extra = f" | {snapshot['browser_url'][:40]}"
            print(f"{icon} {snapshot['timestamp']} | {snapshot['app'][:25]:<25} | "
                  f"C:{snapshot.get('clicks', 0)} K:{snapshot.get('keys', 0)}{extra}")

            # ----- Periodic cloud sync -----
            if time.time() - last_sync_time >= sync_every:
                result = cloud.sync()
                print(f"☁️  {result}")
                last_sync_time = time.time()

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nStopping CRAS...")
        print(cloud.sync())
        tracker.stop()
        pause_manager.stop()
        print("Stopped cleanly. All data saved.")


if __name__ == "__main__":
    main()
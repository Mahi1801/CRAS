import time
import yaml
from datetime import datetime
from tracker.activity import ActivityTracker
from tracker.document import DocumentGenerator
from tracker.cloud import CloudSync

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    print("Activity Tracker started...")
    print("Press Ctrl+C to stop.\n")

    config = load_config()
    interval = config.get("snapshot_interval_seconds", 10)
    idle_threshold = config.get("idle_threshold_seconds", 60)
    sync_every = config.get("cloud_sync_interval_minutes", 15) * 60   # convert to seconds

    tracker = ActivityTracker(idle_threshold=idle_threshold)
    doc_gen = DocumentGenerator(log_folder=config.get("log_folder", "logs"))
    cloud = CloudSync()

    snapshots = []
    last_sync_time = time.time()

    try:
        while True:
            snapshot = tracker.take_snapshot()
            snapshots.append(snapshot)

            if len(snapshots) > 120:
                snapshots = snapshots[-120:]

            doc_gen.write_full_document(snapshots)

            # Live print
            icon = "🟢" if snapshot["status"] == "Active" else "⚪"
            print(f"{icon} {snapshot['timestamp']} | {snapshot['app'][:30]:<30} | {snapshot['status']}")

            # Periodic cloud sync
            if time.time() - last_sync_time > sync_every:
                result = cloud.sync()
                print(f"☁️  {result}")
                last_sync_time = time.time()

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping...")
        # Final sync before exit
        print(cloud.sync())
        tracker.stop()
        print("Stopped cleanly.")

if __name__ == "__main__":
    main()
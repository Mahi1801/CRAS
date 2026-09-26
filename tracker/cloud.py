import os
import subprocess
import time
from datetime import datetime

class CloudSync:
    def __init__(self, config: dict = None):
        config = config or {}
        cloud_cfg = config.get("cloud", {})

        self.enabled = cloud_cfg.get("enabled", True)
        self.local_log_folder = config.get("log_folder", "logs")
        self.rclone_path = cloud_cfg.get("rclone_path", "rclone")
        self.remote_name = cloud_cfg.get("remote", "gdrive")
        self.remote_folder = cloud_cfg.get("remote_folder", "ActivityLogs")
        self.retry_count = cloud_cfg.get("retry_count", 3)

    def sync(self):
        if not self.enabled:
            return "Cloud sync is disabled in config"

        if not os.path.exists(self.local_log_folder):
            return "No logs folder found"

        cmd = [
            self.rclone_path, "copy",
            self.local_log_folder,
            f"{self.remote_name}:{self.remote_folder}",
            "--update",
            "--retries", str(self.retry_count)
        ]

        for attempt in range(1, self.retry_count + 1):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    return f"Successfully uploaded to Google Drive at {datetime.now().strftime('%H:%M:%S')}"
                else:
                    error_msg = result.stderr[:300] if result.stderr else "Unknown error"
                    if attempt < self.retry_count:
                        time.sleep(2)
                        continue
                    return f"Upload failed after {self.retry_count} tries: {error_msg}"
            except Exception as e:
                if attempt < self.retry_count:
                    time.sleep(2)
                    continue
                return f"Error during upload: {str(e)}"

        return "Upload failed"
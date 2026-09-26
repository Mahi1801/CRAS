import os
import subprocess
from datetime import datetime

class CloudSync:
    def __init__(self, local_log_folder="logs", remote_name="gdrive", remote_folder="ActivityLogs"):
        self.local_log_folder = local_log_folder
        self.remote_name = remote_name
        self.remote_folder = remote_folder
        
        # Full path to rclone.exe (from your system)
        self.rclone_path = r"C:\Users\Asus\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.75.1-windows-amd64\rclone.exe"

    def sync(self):
        """Upload all log files to Google Drive using rclone"""
        if not os.path.exists(self.local_log_folder):
            return "No logs folder found"

        try:
            cmd = [
                self.rclone_path, "copy",
                self.local_log_folder,
                f"{self.remote_name}:{self.remote_folder}",
                "--update"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return f"Successfully uploaded to Google Drive at {datetime.now().strftime('%H:%M:%S')}"
            else:
                return f"Upload issue: {result.stderr[:300] if result.stderr else 'Unknown error'}"
        except Exception as e:
            return f"Error during upload: {str(e)}"
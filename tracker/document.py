from datetime import datetime
from collections import defaultdict
import os
import json

class DocumentGenerator:
    def __init__(self, log_folder="logs", snapshot_interval=10):
        self.log_folder = log_folder
        self.snapshot_interval = snapshot_interval
        os.makedirs(log_folder, exist_ok=True)

    def get_today_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    def get_markdown_path(self):
        return os.path.join(self.log_folder, f"activity_{self.get_today_date()}.md")

    def get_raw_path(self):
        """Raw JSONL file – one snapshot per line (survives restarts)"""
        return os.path.join(self.log_folder, f"activity_{self.get_today_date()}.jsonl")

    def load_existing_snapshots(self) -> list:
        """Load all snapshots from today's JSONL file"""
        path = self.get_raw_path()
        snapshots = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            snapshots.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return snapshots

    def append_snapshot(self, snapshot: dict):
        """Append one snapshot to the raw JSONL file (never loses history)"""
        path = self.get_raw_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    def generate_summary(self, snapshots: list) -> str:
        if not snapshots:
            return "No activity recorded yet."

        app_time = defaultdict(int)
        title_examples = defaultdict(list)
        active_count = 0
        idle_count = 0

        for s in snapshots:
            app = s.get("app", "Unknown")
            app_time[app] += 1
            title = s.get("title", "")
            if title and title not in title_examples[app]:
                title_examples[app].append(title[:60])
            if s.get("status") == "Active":
                active_count += 1
            else:
                idle_count += 1

        total = len(snapshots)
        minutes_approx = total * self.snapshot_interval / 60

        lines = [
            f"### Rolling Summary",
            f"- Total snapshots: **{total}** (~{minutes_approx:.1f} minutes of tracking)",
            f"- Active time: **{active_count}** snapshots",
            f"- Idle time: **{idle_count}** snapshots",
            "",
            "#### Time distribution by application:"
        ]

        for app, count in sorted(app_time.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            example = title_examples[app][0] if title_examples[app] else ""
            lines.append(f"- **{app}** — {count} snapshots ({pct:.1f}%)")
            if example:
                lines.append(f"  - Example: _{example}_")

        return "\n".join(lines)

    def rebuild_markdown(self, snapshots: list):
        """Rebuild the full Markdown file from all snapshots"""
        filename = self.get_markdown_path()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Work Activity Log – {self.get_today_date()}\n\n")
            f.write(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*\n\n")

            f.write("## Rolling Summary\n\n")
            f.write(self.generate_summary(snapshots))
            f.write("\n\n---\n\n")

            f.write("## Detailed Timeline\n\n")
            for s in snapshots:
                ts = s.get("timestamp", "")
                status = s.get("status", "")
                app = s.get("app", "")
                title = s.get("title", "")
                f.write(f"- **{ts}** | {status} | `{app}` → {title}\n")
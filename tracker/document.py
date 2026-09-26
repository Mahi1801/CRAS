from datetime import datetime
from collections import defaultdict
import os

class DocumentGenerator:
    def __init__(self, log_folder="logs"):
        self.log_folder = log_folder
        os.makedirs(log_folder, exist_ok=True)

    def get_today_filename(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_folder, f"activity_{today}.md")

    def generate_summary(self, snapshots: list) -> str:
        if not snapshots:
            return "No activity recorded yet."

        app_time = defaultdict(int)
        title_examples = defaultdict(list)
        active_count = 0
        idle_count = 0

        for s in snapshots:
            app = s["app"]
            app_time[app] += 1
            if s["title"] and s["title"] not in title_examples[app]:
                title_examples[app].append(s["title"][:60])
            if s["status"] == "Active":
                active_count += 1
            else:
                idle_count += 1

        total = len(snapshots)
        minutes_approx = total * 10 / 60   # assuming 10 sec interval

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

    def write_full_document(self, snapshots: list):
        filename = self.get_today_filename()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Work Activity Log – {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*\n\n")

            f.write("## Rolling Summary\n\n")
            f.write(self.generate_summary(snapshots))
            f.write("\n\n---\n\n")

            f.write("## Detailed Timeline\n\n")
            for s in snapshots:
                f.write(f"- **{s['timestamp']}** | {s['status']} | `{s['app']}` → {s['title']}\n")
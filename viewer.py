import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Activity Tracker", page_icon="📊", layout="wide")

st.title("📊 Work Activity Tracker")
st.markdown("Live view of your daily activity log")

log_folder = "logs"

# List available log files
if not os.path.exists(log_folder):
    st.warning("No logs folder found yet.")
    st.stop()

log_files = sorted([f for f in os.listdir(log_folder) if f.endswith(".md")], reverse=True)

if not log_files:
    st.info("No activity logs found yet. Run `python main.py` first.")
    st.stop()

selected_file = st.selectbox("Select log file", log_files)

file_path = os.path.join(log_folder, selected_file)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

st.markdown(content)

st.download_button(
    label="⬇️ Download this log",
    data=content,
    file_name=selected_file,
    mime="text/markdown"
)
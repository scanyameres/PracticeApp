import json, sys, os
from datetime import datetime

data = json.load(sys.stdin)
log_dir = os.path.join(data.get("cwd", "."), ".claude", "prompt-log")
os.makedirs(log_dir, exist_ok=True)

with open(os.path.join(log_dir, "prompts.md"), "a", encoding="utf-8") as f:
    f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M}  (session {data.get('session_id','')[:8]})\n\n")
    f.write(data.get("prompt", "") + "\n\n")

sys.exit(0)
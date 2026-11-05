"""Claude Code hook (UserPromptSubmit): append every prompt to .claude/prompt-log/prompts.md.

Configured in .claude/settings.json. Claude Code sends the prompt as JSON on stdin.
The log location is based on where this script lives (<project>/.claude/hooks/), not on the
current working directory, so prompts always land in the project's own log, even when
Claude Code works from a subfolder (that used to create a second log inside src/).
"""

import json
import sys
from datetime import datetime
from pathlib import Path

data = json.load(sys.stdin)
log_dir = Path(__file__).resolve().parents[1] / "prompt-log"  # <project>/.claude/prompt-log
log_dir.mkdir(parents=True, exist_ok=True)

with open(log_dir / "prompts.md", "a", encoding="utf-8") as f:
    f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M}  (session {data.get('session_id', '')[:8]})\n\n")
    f.write(data.get("prompt", "") + "\n\n")

sys.exit(0)

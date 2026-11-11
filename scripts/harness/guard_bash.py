#!/usr/bin/env python3
"""PreToolUse guard for the Bash tool.

Reads the hook payload on stdin and denies (or asks about) commands that are
destructive or that touch secrets. Prints a JSON decision for Claude Code.
Patterns are deliberately conservative: a false "ask" costs one prompt,
a false "allow" can delete work.
"""

import json
import re
import sys

DENY = [
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME|\.\.?|\*)(\s|$)", "rm -r on root/home/cwd"),
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b)", "force push"),
    (r"\bgit\s+push\b.*--delete\b.*\b(main|master)\b", "deleting main/master"),
    (r"\bgit\s+branch\s+-D\s+(main|master)\b", "deleting main/master"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard (use a WIP commit instead)"),
    (r"\bgit\s+checkout\s+--\s+\.", "discarding all working-tree changes"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean -f"),
    (
        r"\bgit\s+stash\b(?!\s+(list|show|apply|drop|push\s+-u\s+-m))",
        "bare git stash is shared across worktrees; use `git stash push -u -m <tag>`",
    ),
    (r"\bsudo\b", "sudo"),
    (r"\bchmod\s+(-R\s+)?777\b", "chmod 777"),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba)?sh\b", "piping a download into a shell"),
    (r"\bmkfs\b|\bdd\s+if=", "disk-level write"),
    (r">\s*\.env(\.[a-zA-Z0-9_-]+)?(\s|$)|\btee\s+\.env\b", "writing to a .env file"),
]
ASK = [
    (r"\bgit\s+push\b", "pushing to a remote"),
    (r"\bgit\s+rebase\b", "rewriting history"),
    (r"\bdocker\s+(system\s+prune|rm|rmi|volume\s+rm)\b", "removing docker resources"),
    (r"\brm\s+-[a-zA-Z]*r", "recursive delete"),
    (r"\b(cat|grep|less|head|tail)\b[^|;&]*\s\.env\b", "reading a .env file"),
]


def emit(decision: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # malformed input: do not block
    if payload.get("tool_name") != "Bash":
        return
    cmd = str(payload.get("tool_input", {}).get("command", ""))
    for pat, why in DENY:
        if re.search(pat, cmd):
            emit(
                "deny",
                f"harness guard: blocked ({why}). "
                "If this is really needed, the user must run it manually.",
            )
            return
    for pat, why in ASK:
        if re.search(pat, cmd):
            emit("ask", f"harness guard: needs confirmation ({why}).")
            return


if __name__ == "__main__":
    main()

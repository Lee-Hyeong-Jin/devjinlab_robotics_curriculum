#!/usr/bin/env python3
"""Roadmap state store for the dev graph (harness/roadmap.yaml).

The roadmap is the *state* that the outer loop node reads and writes. This tool
keeps the YAML editable by hand while giving agents a deterministic interface.
It uses a tiny purpose-built parser so it has no third-party dependency.

Usage:
  roadmap.py summary                 # one line per milestone
  roadmap.py next                    # JSON of the next runnable milestone (or null)
  roadmap.py get <id>                # JSON of one milestone
  roadmap.py set <id> <status> [note]# status: todo|in_progress|done|blocked
  roadmap.py list [--json]           # all milestones

Milestone format (harness/roadmap.yaml):
  milestones:
    - id: M1
      title: ...
      status: todo
      depends_on: [M0]
      goal: ...
      acceptance:
        - ...
      note: ...
"""

import json
import os
import re
import subprocess
import sys


def _root() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except Exception:
        return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


ROOT = _root()
PATH = os.path.join(ROOT, "harness", "roadmap.yaml")
STATUSES = ("todo", "in_progress", "done", "blocked")


def _parse(text: str) -> list[dict]:
    """Parse the restricted YAML subset used by roadmap.yaml."""
    items: list[dict] = []
    cur: dict | None = None
    list_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or line.strip() == "milestones:":
            continue
        m = re.match(r"^\s*-\s+id:\s*(\S+)\s*$", line)
        if m:
            cur = {"id": m.group(1), "depends_on": [], "acceptance": []}
            items.append(cur)
            list_key = None
            continue
        if cur is None:
            continue
        m = re.match(r"^\s{6,}-\s+(.*)$", line)
        if m and list_key:
            cur[list_key].append(m.group(1).strip().strip('"'))
            continue
        m = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            list_key = None
            if val == "" and key in ("acceptance", "depends_on"):
                cur[key] = []
                list_key = key
            elif val == "":
                cur[key] = ""
            elif val.startswith("["):
                cur[key] = [v.strip().strip('"') for v in val.strip("[]").split(",") if v.strip()]
            else:
                cur[key] = val.strip('"')
    for it in items:
        it.setdefault("status", "todo")
        it.setdefault("title", it["id"])
    return items


def load() -> tuple[str, list[dict]]:
    with open(PATH, encoding="utf-8") as f:
        text = f.read()
    return text, _parse(text)


def set_status(mid: str, status: str, note: str | None) -> None:
    if status not in STATUSES:
        sys.exit(f"invalid status {status!r}; use one of {STATUSES}")
    text, items = load()
    if mid not in {i["id"] for i in items}:
        sys.exit(f"unknown milestone {mid!r}")
    lines = text.splitlines()
    out, in_target, done_status, done_note = [], False, False, note is None
    for line in lines:
        m = re.match(r"^\s*-\s+id:\s*(\S+)\s*$", line)
        if m:
            if in_target and not done_note:
                out.append(f"      note: {note}")
                done_note = True
            in_target = m.group(1) == mid
        if in_target:
            if re.match(r"^\s+status:", line):
                line = re.sub(r"status:.*", f"status: {status}", line)
                done_status = True
            elif note is not None and re.match(r"^\s+note:", line):
                line = re.sub(r"note:.*", f"note: {note}", line)
                done_note = True
        out.append(line)
    if in_target and not done_note:
        out.append(f"      note: {note}")
    if not done_status:
        sys.exit(f"milestone {mid!r} has no status line to update")
    with open(PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def next_runnable(items: list[dict]) -> dict | None:
    done = {i["id"] for i in items if i["status"] == "done"}
    for i in items:  # in_progress first so an interrupted run resumes
        if i["status"] == "in_progress" and set(i["depends_on"]) <= done:
            return i
    for i in items:
        if i["status"] == "todo" and set(i["depends_on"]) <= done:
            return i
    return None


def main(argv: list[str]) -> None:
    cmd = argv[1] if len(argv) > 1 else "summary"
    _, items = load()
    if cmd == "summary":
        for i in items:
            mark = {"done": "[x]", "in_progress": "[>]", "blocked": "[!]"}.get(i["status"], "[ ]")
            print(f"{mark} {i['id']} {i['title']} ({i['status']})")
    elif cmd == "list":
        print(
            json.dumps(items, ensure_ascii=False, indent=2)
            if "--json" in argv
            else "\n".join(i["id"] for i in items)
        )
    elif cmd == "next":
        print(json.dumps(next_runnable(items), ensure_ascii=False))
    elif cmd == "get":
        found = [i for i in items if i["id"] == argv[2]]
        print(json.dumps(found[0] if found else None, ensure_ascii=False, indent=2))
    elif cmd == "set":
        set_status(argv[2], argv[3], " ".join(argv[4:]) or None)
        print(f"{argv[2]} -> {argv[3]}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)

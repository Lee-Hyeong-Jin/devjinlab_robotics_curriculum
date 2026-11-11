#!/usr/bin/env bash
# Prints the detected project stack(s), one per line: python | node | none
# Detection is file-based so it keeps working once real code lands.
set -u
root="$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")"
found=0
[ -f "$root/pyproject.toml" ] && { echo python; found=1; }
# The frontend lives in web/ (P2-4); a root package.json also counts.
{ [ -f "$root/package.json" ] || [ -f "$root/web/package.json" ]; } && { echo node; found=1; }
[ "$found" = 0 ] && echo none
exit 0

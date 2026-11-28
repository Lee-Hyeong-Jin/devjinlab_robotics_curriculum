#!/usr/bin/env python3
"""A mail server that delivers nothing: every message is appended to a file as one JSON line.

For tests that have to follow a mailed link (email verification, password reset) and for
trying those flows locally without a real mailbox:

    python3 scripts/dev/smtp_sink.py --port 2525 --out /tmp/outbox.jsonl &
    RC_SMTP_HOST=127.0.0.1 RC_SMTP_PORT=2525 RC_SMTP_STARTTLS=0 uv run rc api serve

Each line is ``{"to": [...], "from": "...", "subject": "...", "body": "..."}`` with the
subject and body decoded, so a reader does not have to undo base64 or quoted-printable.
It speaks just enough SMTP for ``smtplib``; no TLS, no authentication. Never expose it.
"""

from __future__ import annotations

import argparse
import json
import socketserver
from email import message_from_bytes, policy
from pathlib import Path


class Handler(socketserver.StreamRequestHandler):
    out: Path

    def _say(self, line: str) -> None:
        self.wfile.write(line.encode() + b"\r\n")
        self.wfile.flush()

    def handle(self) -> None:
        self._say("220 sink ready")
        recipients: list[str] = []
        while True:
            raw = self.rfile.readline()
            if not raw:
                return
            command = raw.decode(errors="replace").strip()
            verb = command.upper()
            if verb.startswith(("EHLO", "HELO")):
                self._say("250 sink")
            elif verb.startswith("RCPT TO:"):
                recipients.append(command[8:].strip().strip("<>"))
                self._say("250 ok")
            elif verb == "DATA":
                self._say("354 end with <CRLF>.<CRLF>")
                lines: list[bytes] = []
                while True:
                    line = self.rfile.readline()
                    if line in (b".\r\n", b".\n", b""):
                        break
                    # Undo SMTP dot-stuffing.
                    lines.append(line[1:] if line.startswith(b"..") else line)
                self._store(b"".join(lines), recipients)
                recipients = []
                self._say("250 stored")
            elif verb == "QUIT":
                self._say("221 bye")
                return
            else:
                self._say("250 ok")

    def _store(self, data: bytes, recipients: list[str]) -> None:
        message = message_from_bytes(data, policy=policy.default)
        body = message.get_body(preferencelist=("plain",))
        record = {
            "to": recipients,
            "from": str(message.get("From", "")),
            "subject": str(message.get("Subject", "")),
            "body": body.get_content() if body is not None else "",
        }
        with self.out.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2525)
    parser.add_argument("--out", type=Path, required=True, help="File to append messages to.")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.touch()
    Handler.out = args.out
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.host, args.port), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()

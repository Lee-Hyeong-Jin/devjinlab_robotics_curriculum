"""Outgoing mail (AC-AUTH.9): interface, SMTP implementation, in-memory fake for tests."""

from __future__ import annotations

import smtplib
import ssl
from collections.abc import Mapping
from dataclasses import dataclass, field
from email.message import EmailMessage
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Mail:
    to: str
    subject: str
    body: str


class Mailer(Protocol):
    def send(self, mail: Mail) -> None: ...


@dataclass(slots=True)
class FakeMailer:
    """Keeps every message in memory (tests, development)."""

    outbox: list[Mail] = field(default_factory=list)

    def send(self, mail: Mail) -> None:
        self.outbox.append(mail)


@dataclass(frozen=True, slots=True)
class SmtpConfig:
    host: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    sender: str = "no-reply@localhost"
    starttls: bool = True

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> SmtpConfig | None:
        """``RC_SMTP_HOST`` (required), ``_PORT``, ``_USER``, ``_PASSWORD``, ``_FROM``,
        ``_STARTTLS`` (``0`` to disable). ``None`` when no host is configured."""
        host = env.get("RC_SMTP_HOST")
        if not host:
            return None
        return cls(
            host=host,
            port=int(env.get("RC_SMTP_PORT") or 587),
            username=env.get("RC_SMTP_USER") or None,
            password=env.get("RC_SMTP_PASSWORD") or None,
            sender=env.get("RC_SMTP_FROM") or "no-reply@localhost",
            starttls=env.get("RC_SMTP_STARTTLS", "1") != "0",
        )


class SmtpMailer:
    def __init__(self, config: SmtpConfig, smtp: type[smtplib.SMTP] = smtplib.SMTP) -> None:
        self.config = config
        self._smtp = smtp

    def send(self, mail: Mail) -> None:
        message = EmailMessage()
        message["From"] = self.config.sender
        message["To"] = mail.to
        message["Subject"] = mail.subject
        message.set_content(mail.body)
        with self._smtp(self.config.host, self.config.port, timeout=10) as client:
            if self.config.starttls:
                client.starttls(context=ssl.create_default_context())
            if self.config.username:
                client.login(self.config.username, self.config.password or "")
            client.send_message(message)

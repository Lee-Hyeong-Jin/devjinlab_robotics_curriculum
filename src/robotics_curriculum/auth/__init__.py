"""Server-mode authentication and authorization (P2-2).

Local accounts (email + Argon2id password), server-side browser sessions, personal access
tokens (PATs), roles ``learner < author < admin``, and an append-only audit log. See
``docs/architecture/auth.md`` and ``docs/adr/0009-session-model.md``.

Needs the ``api`` extra (SQLAlchemy, argon2-cffi). Local mode (``rc`` CLI) does not use it.
"""

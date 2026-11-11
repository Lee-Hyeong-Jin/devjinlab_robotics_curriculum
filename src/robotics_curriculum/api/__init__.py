"""HTTP API (P2-1): a FastAPI app over the core library, served by ``rc api serve``.

FastAPI and uvicorn come from the optional ``api`` extra, so this package's ``__init__``,
:mod:`robotics_curriculum.api.settings` and :mod:`robotics_curriculum.api.cli` import neither;
build the app with :func:`robotics_curriculum.api.app.create_app`.
"""

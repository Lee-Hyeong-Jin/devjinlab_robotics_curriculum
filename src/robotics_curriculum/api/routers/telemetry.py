"""``POST /api/v1/telemetry/pageview``: the web tier reports page views (ADR 0017).

Not a public endpoint. The browser never calls it; the web server does, once per page it
serves, and only a connection from a trusted proxy is accepted, so the numbers cannot be
inflated from the internet.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response, status

from robotics_curriculum.api.clientip import client_address
from robotics_curriculum.api.deps import State
from robotics_curriculum.api.ops_schemas import PageViewIn
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.ops.traffic import is_bot, normalize_path, referrer_host, visitor_hash

router = APIRouter(
    prefix="/api/v1/telemetry", tags=["telemetry"], responses=problem_responses(403, 404, 422)
)

LOCALES = frozenset({"ko", "en"})


def _from_trusted_proxy(request: Request, state: State) -> bool:
    """Whether the connection itself (not a forwarded header) comes from our web tier."""
    peer = request.client.host if request.client else None
    if peer is None:
        return False
    # A trusted peer is exactly one for which the forwarded header would be believed: asking
    # with a marker address shows whether it was.
    return client_address(peer, "192.0.2.1", state.settings.trusted_proxies) == "192.0.2.1"


@router.post("/pageview", status_code=status.HTTP_204_NO_CONTENT)
def page_view(body: PageViewIn, request: Request, state: State) -> Response:
    """Count one page view.

    Stored: the day, the normalized path, the language, whether the client is automated,
    whether the reader is signed in, and the referring host. The address and user agent are
    used once, to derive a visitor pseudonym that changes every day, and are not stored.

    403 unless the caller is the web tier; 404 when monitoring is off.
    """
    if state.ops is None:
        raise HTTPException(404, "monitoring is not enabled on this server")
    if not _from_trusted_proxy(request, state):
        raise HTTPException(403, "page views are accepted from the web tier only")
    now = state.clock()
    day = now.date()
    user_agent = request.headers.get("user-agent")
    bot = is_bot(user_agent)
    address = client_address(
        request.client.host if request.client else None,
        request.headers.get("x-forwarded-for"),
        state.settings.trusted_proxies,
    )
    own_host = urlsplit(state.auth.config.public_url).hostname if state.auth else None
    state.ops.store.add_page_view(
        day=day,
        path=normalize_path(body.path),
        locale=body.locale if body.locale in LOCALES else "other",
        bot=bot,
        signed_in=body.signed_in,
        # Automated clients are counted as views, never as people.
        visitor=None if bot else visitor_hash(state.visit_key, day, address, user_agent),
        referrer=None if bot else referrer_host(body.referrer, [own_host] if own_host else []),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

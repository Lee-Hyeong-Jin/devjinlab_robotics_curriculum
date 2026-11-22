"""The caller's address when the API sits behind the web tier or a reverse proxy.

The browser never talks to this API: the web app does, on the browser's behalf. Taken at face
value, every request therefore comes from the web server's address. The audit log, the session
list and the per-address sign-in throttle all need the address of the person, which arrives in
``X-Forwarded-For`` and may only be believed when the request really came through a proxy this
deployment runs.
"""

from __future__ import annotations

import ipaddress
from collections.abc import Sequence

Network = ipaddress.IPv4Network | ipaddress.IPv6Network

DEFAULT_TRUSTED_PROXIES = ("127.0.0.1/32", "::1/128")
"""Loopback only: a web app on the same host. A container network has to be named explicitly."""


class TrustedProxyError(ValueError):
    """A trusted-proxy entry is not an address or a network."""


def parse_trusted_proxies(value: str | None) -> tuple[Network, ...]:
    """Parse ``RC_API_TRUSTED_PROXIES``: comma-separated addresses or CIDR networks.

    Args:
        value: The setting; ``None`` or blank means the loopback default.

    Returns:
        The networks whose members may say who the client is.

    Raises:
        TrustedProxyError: An entry is neither an address nor a network.
    """
    entries = [part.strip() for part in (value or "").split(",") if part.strip()]
    networks: list[Network] = []
    for entry in entries or list(DEFAULT_TRUSTED_PROXIES):
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError:
            raise TrustedProxyError(
                f"invalid RC_API_TRUSTED_PROXIES entry '{entry}' (use an address or a CIDR network)"
            ) from None
    return tuple(networks)


def _address(text: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    candidate = text.strip()
    # `[::1]:1234` and `1.2.3.4:1234` appear in the wild; the port is not part of the address.
    if candidate.startswith("["):
        candidate = candidate[1:].split("]", 1)[0]
    elif candidate.count(":") == 1:
        candidate = candidate.split(":", 1)[0]
    try:
        address = ipaddress.ip_address(candidate)
    except ValueError:
        return None
    mapped = getattr(address, "ipv4_mapped", None)
    return mapped if mapped is not None else address


def _trusted(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address, trusted: Sequence[Network]
) -> bool:
    return any(address.version == network.version and address in network for network in trusted)


def client_address(
    peer: str | None, forwarded_for: str | None, trusted: Sequence[Network]
) -> str | None:
    """The address of whoever is on the far side of this deployment's own proxies.

    The header is read right to left, skipping addresses of trusted proxies, and the first one
    that is not ours is the client: everything to its left was written by the client or by
    proxies we do not run, and anyone can put anything there.

    Args:
        peer: The address the connection came from.
        forwarded_for: The ``X-Forwarded-For`` header, if any.
        trusted: Networks of the proxies this deployment runs.

    Returns:
        The client address as text, or ``peer`` when the header may not be believed or holds
        nothing usable.
    """
    if peer is None:
        return None
    peer_address = _address(peer)
    if peer_address is None or not _trusted(peer_address, trusted) or not forwarded_for:
        return peer
    for hop in reversed(forwarded_for.split(",")):
        address = _address(hop)
        if address is None:
            # Garbage in the chain: stop believing it rather than skip over it.
            return peer
        if not _trusted(address, trusted):
            return str(address)
    # Every hop was one of our proxies: the request started inside the deployment.
    return peer

"""
Network guard: enforces the "no outbound traffic" promise instead of just stating it.

While the guard is active, any attempt to open a socket to a non-loopback address
raises ``OutboundNetworkBlocked``. Every attempt is recorded so the analysis report
can show exactly how many outbound connections were tried (expected: 0).
"""

from __future__ import annotations

import ipaddress
import socket
import threading
from contextlib import contextmanager
from typing import List

_lock = threading.RLock()
_depth = 0
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_create_connection = socket.create_connection
_original_getaddrinfo = socket.getaddrinfo

attempts: List[str] = []


class OutboundNetworkBlocked(ConnectionError):
    pass


def _is_local(host) -> bool:
    if host is None:
        return True
    host = str(host)
    if host in ("localhost", ""):
        return True
    try:
        return ipaddress.ip_address(host.split("%")[0]).is_loopback
    except ValueError:
        return False  # a hostname that isn't localhost → would need DNS → outbound


def _check(address) -> None:
    host = address[0] if isinstance(address, tuple) else address
    if not _is_local(host):
        attempts.append(str(host))
        raise OutboundNetworkBlocked(f"Outbound connection to {host!r} blocked by AegisIMINT network guard")


def _guarded_connect(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        _check(address)
    return _original_connect(self, address)


def _guarded_connect_ex(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        _check(address)
    return _original_connect_ex(self, address)


def _guarded_create_connection(address, *args, **kwargs):
    _check(address)
    return _original_create_connection(address, *args, **kwargs)


def _guarded_getaddrinfo(host, *args, **kwargs):
    if not _is_local(host):
        attempts.append(str(host))
        raise OutboundNetworkBlocked(f"DNS lookup for {host!r} blocked by AegisIMINT network guard")
    return _original_getaddrinfo(host, *args, **kwargs)


@contextmanager
def offline():
    """Context manager: block all non-loopback network access inside the block."""
    global _depth
    with _lock:
        if _depth == 0:
            socket.socket.connect = _guarded_connect
            socket.socket.connect_ex = _guarded_connect_ex
            socket.create_connection = _guarded_create_connection
            socket.getaddrinfo = _guarded_getaddrinfo
        _depth += 1
    start = len(attempts)
    report = {"blocked_attempts": 0, "hosts": []}
    try:
        yield report
    finally:
        report["hosts"] = attempts[start:]
        report["blocked_attempts"] = len(report["hosts"])
        with _lock:
            _depth -= 1
            if _depth == 0:
                socket.socket.connect = _original_connect
                socket.socket.connect_ex = _original_connect_ex
                socket.create_connection = _original_create_connection
                socket.getaddrinfo = _original_getaddrinfo

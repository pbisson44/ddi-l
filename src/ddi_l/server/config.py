"""Configuration for the HTTP API.

A plain dataclass with no Litestar import, so ``ddi serve --help`` can show
the defaults without the ``server`` extra installed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# 32 MiB: room for large real instances, small enough that one request
# cannot exhaust a worker's memory.
DEFAULT_MAX_BODY_BYTES = 32 * 1024 * 1024

# Bounds how long a client waits, not how long the work runs: a worker
# thread cannot be cancelled, so on timeout the client gets 504 while the
# thread finishes. `max_body_bytes` bounds the work itself.
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60.0

# Schema validation is CPU-bound Python holding the GIL, so running more jobs
# than cores adds memory without adding throughput.
DEFAULT_MAX_CONCURRENT_JOBS = max(1, os.cpu_count() or 1)


@dataclass(frozen=True)
class ServerConfig:
    """Runtime limits and exposure settings for :func:`ddi_l.server.create_app`."""

    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS
    # Documents processed at once; further requests get 503 until one ends.
    max_concurrent_jobs: int = DEFAULT_MAX_CONCURRENT_JOBS
    # Load the default schema at startup so the first request does not pay
    # the multi-second load inside its timeout.
    preload_schema: bool = True

    # Off unless asked for; allowing `*` makes every visited page a client.
    cors_allow_origins: tuple[str, ...] = field(default_factory=tuple)

    # Litestar serves its OpenAPI schema and docs UI from `/schema`. Useful when
    # the service is an internal tool, unwanted when it faces the internet.
    enable_openapi: bool = True

    def __post_init__(self) -> None:
        """Reject limits that would disable the protection they configure."""
        if self.max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be positive")
        if self.max_concurrent_jobs <= 0:
            raise ValueError("max_concurrent_jobs must be positive")

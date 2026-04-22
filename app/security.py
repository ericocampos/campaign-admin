ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1"}


def ensure_loopback_bind(host: str) -> None:
    if host not in ALLOWED_HOSTS:
        raise RuntimeError(
            f"refusing to start: app host is '{host}', must be one of {sorted(ALLOWED_HOSTS)}. "
            "This tool has no authentication and must not be exposed to non-loopback addresses."
        )

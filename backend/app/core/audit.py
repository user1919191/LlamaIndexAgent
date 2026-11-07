import logging


logger = logging.getLogger("security.audit")


def audit_event(event: str, **fields) -> None:
    logger.info("security_event=%s %s", event, " ".join(f"{key}={value}" for key, value in fields.items()))


def audit_login(*args, **kwargs) -> None:
    """Login success/failure is intentionally excluded from business audit logs."""
    return None

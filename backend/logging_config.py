import logging
import sys
import structlog

SENSITIVE_KEYS = {
    "aadhaar", "password", "token", "intake", "pan", "account_number",
    "vpa", "secret", "mfa_secret", "credit_card", "bank_details", "cvv"
}

def scrub_sensitive_pii_processor(logger, method_name, event_dict):
    """Sanitize sensitive PII keys and credentials before log rendering."""
    for key in list(event_dict.keys()):
        if any(sens in key.lower() for sens in SENSITIVE_KEYS):
            event_dict[key] = "[REDACTED_PII]"
    return event_dict

def setup_logging(production: bool = False):
    """Configure structured JSON logging for production or key-value console logging for dev."""
    log_level = logging.INFO

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        scrub_sensitive_pii_processor,
    ]

    if production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

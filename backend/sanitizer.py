import html
import os
import re


def sanitize_text(val: str | None) -> str | None:
    """
    Trim whitespace and escape HTML control characters to prevent XSS attacks.
    Returns None if input is None.
    """
    if val is None:
        return None
    val = val.strip()
    return html.escape(val, quote=True)


def sanitize_filename(val: str | None) -> str | None:
    """
    Sanitize a filename by removing directory traversal patterns, null bytes,
    and keeping only safe characters.
    """
    if not val:
        return val
    # Remove null bytes and path separators
    clean = os.path.basename(val.replace("\0", "").replace("\\", "/"))
    # Keep safe alphanumeric characters, dots, dashes, underscores
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean)
    return safe_name[:255] if safe_name else "file"


def sanitize_key(val: str | None) -> str | None:
    """
    Sanitize object storage keys to prevent path traversal.
    Ensures relative key paths without '..' segments or null bytes.
    """
    if not val:
        return val
    clean = val.replace("\0", "").replace("\\", "/").strip()
    # Remove leading slashes
    clean = clean.lstrip("/")
    # Disallow path traversal components
    parts = [p for p in clean.split("/") if p and p != ".."]
    return "/".join(parts)

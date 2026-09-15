import html
import os
import re
from typing import overload


@overload
def sanitize_text(val: None) -> None: ...
@overload
def sanitize_text(val: str) -> str: ...
def sanitize_text(val: str | None) -> str | None:
    """
    Trim whitespace and escape HTML control characters to prevent XSS attacks.
    Returns None if input is None.
    """
    if val is None:
        return None
    val = val.strip()
    return html.escape(val, quote=True)


@overload
def clean_string(val: None, max_length: int | None = None) -> None: ...
@overload
def clean_string(val: str, max_length: int | None = None) -> str: ...
def clean_string(val: str | None, max_length: int | None = None) -> str | None:
    """
    Sanitize raw user string input without HTML entity encoding to prevent double-escaping
    when stored in the database and later rendered via template escapeHtml() or export utilities.

    - Removes null bytes and non-printable control characters (preserves standard tabs and newlines).
    - Removes explicit script and iframe injection tags.
    - Trims leading/trailing whitespace.
    - Constrains to max_length if specified.
    """
    if val is None:
        return None
    # Remove null bytes and non-printable control chars except \t and \n
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", val)
    # Strip script/iframe injection tags if present
    cleaned = re.sub(r"(?i)<\s*(script|iframe|object|embed)[^>]*>.*?</\s*\1\s*>", "", cleaned)
    cleaned = re.sub(r"(?i)<\s*(script|iframe|object|embed)[^>]*>", "", cleaned)
    cleaned = cleaned.strip()
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned


sanitize_input = clean_string


@overload
def sanitize_filename(val: None) -> None: ...
@overload
def sanitize_filename(val: str) -> str: ...
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


@overload
def sanitize_key(val: None) -> None: ...
@overload
def sanitize_key(val: str) -> str: ...
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


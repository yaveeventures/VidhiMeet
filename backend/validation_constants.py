"""
Canonical Validation Constants and Statutory Limits for VidhiMeet.
Serves as the Single Source of Truth for both backend Pydantic schemas
and frontend client-side validation rules.
"""

# ── Financial & Banking Regex Patterns ────────────────────────────────────────
# Indian Financial System Code (IFSC): 4 alpha, literal '0', 6 alphanumeric
IFSC_REGEX = r"^[A-Z]{4}0[A-Z0-9]{6}$"

# Indian Bank Account Number: typically 6 to 18 digits
BANK_ACCOUNT_REGEX = r"^\d{6,18}$"

# Unified Payments Interface (UPI) Virtual Payment Address (VPA)
UPI_VPA_REGEX = r"^[\w\.\-]+@[\w\-]+$"


# ── Identity & Telephony Regex Patterns ───────────────────────────────────────
# 12-digit Indian Aadhaar number (with or without hyphens)
AADHAAR_REGEX = r"^\d{12}$|^\d{4}-\d{4}-\d{4}$"

# 10-digit Indian Mobile number starting with 6, 7, 8, or 9
MOBILE_IN_REGEX = r"^[6-9][0-9]{9}$"


# ── Statutory & Regulatory Limits ─────────────────────────────────────────────
# DPDP Act 2023 Section 9 - Minimum Age for personal data consent without parental verification
DPDPA_MIN_AGE_YEARS = 18

# Password bounds
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128

# User Full Name bounds
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 160

# Bar Council Registration Number max length
BAR_NUMBER_MAX_LENGTH = 100


# ── File Upload & Document Constraints ────────────────────────────────────────
# Maximum upload size: 20 Megabytes
MAX_DOCUMENT_SIZE_BYTES = 20 * 1024 * 1024

# Allowed document MIME types
ALLOWED_DOCUMENT_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# Allowed file extensions
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".docx"]


def get_public_validation_rules() -> dict:
    """
    Returns a dictionary of validation rules safe to expose publicly to frontend clients
    via GET /api/v1/public/validation-rules.
    """
    return {
        "ifsc_regex": IFSC_REGEX,
        "bank_account_regex": BANK_ACCOUNT_REGEX,
        "upi_vpa_regex": UPI_VPA_REGEX,
        "aadhaar_regex": AADHAAR_REGEX,
        "mobile_in_regex": MOBILE_IN_REGEX,
        "dpdpa_min_age_years": DPDPA_MIN_AGE_YEARS,
        "password_min_length": PASSWORD_MIN_LENGTH,
        "password_max_length": PASSWORD_MAX_LENGTH,
        "name_min_length": NAME_MIN_LENGTH,
        "name_max_length": NAME_MAX_LENGTH,
        "max_document_size_bytes": MAX_DOCUMENT_SIZE_BYTES,
        "allowed_document_mime_types": ALLOWED_DOCUMENT_MIME_TYPES,
        "allowed_document_extensions": ALLOWED_DOCUMENT_EXTENSIONS,
    }

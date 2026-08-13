from functools import lru_cache
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./lexconnect.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-secret-change-before-production"
    jwt_issuer: str = "lexconnect"
    access_token_minutes: int = 60
    refresh_token_days: int = 14
    allowed_origins: str = "http://localhost:8080"
    platform_fee_percent: int = 5
    video_provider: str = "jitsi"
    jitsi_app_id: str = ""
    jitsi_app_secret: str = ""
    jitsi_domain: str = "meet.jit.si"
    daily_api_key: str = ""
    daily_domain: str = "lexconnect"
    aws_region: str = "ap-south-1"
    document_bucket: str = ""
    max_document_bytes: int = 10 * 1024 * 1024
    presigned_url_expiry_seconds: int = 900  # 15 minutes max link validity
    data_encryption_key: str = ""
    trust_proxy: bool = False
    phonepe_merchant_id: str = ""
    phonepe_salt_key: str = ""
    phonepe_salt_index: str = "1"
    phonepe_env: str = "sandbox"
    # ── Rate Limiting Configurable Settings ───────────────────────────────────
    rate_limit_enabled: bool = True
    rate_limit_auth_per_min: int = 10           # Stricter: Login, register, refresh, password reset
    rate_limit_public_per_min: int = 60         # Moderate: Public search, stats, health checks
    rate_limit_authenticated_per_min: int = 200 # Looser: Authenticated user actions
    rate_limit_admin_per_min: int = 120         # Admin console data queries
    rate_limit_uploads_per_min: int = 15        # Presigned URLs & document uploads
    rate_limit_strict_per_min: int = 10         # Sensitive operations (purge, fee changes)
    rate_limit_global_per_min: int = 120        # Default fallback
    # Auth Exponential Backoff Settings (Per-IP & Per-Account)
    rate_limit_auth_account_max_attempts: int = 5     # Max free attempts before backoff kicks in
    rate_limit_auth_backoff_base_seconds: float = 2.0   # Base delay multiplier
    rate_limit_auth_backoff_max_seconds: float = 300.0  # Max delay cap (5 mins)
    rate_limit_auth_window_seconds: int = 600           # Sliding window for auth attempts (10 mins)
    # ── Data Retention (DPDP Act §8(7)) ──────────────────────────────────────
    # Number of days to retain completed/disputed bookings (default: 7 years for tax/legal compliance)
    retention_completed_days: int = 2555   # ~7 years
    # Number of days to retain cancelled/refunded bookings before purging
    retention_cancelled_days: int = 365    # 1 year
    # Number of days to retain orphaned refresh tokens after expiry
    retention_token_days: int = 30
    # ── NTP Time Synchronization (CERT-In / DPDP forensic timestamp compliance) ─
    # Ordered list of NTP servers — NPL and NIC are Indian government sources.
    # Override via NTP_SERVERS env var (comma-separated) in production.
    ntp_servers: str = "time.nplindia.org,time.nplindia.in,time.nic.in,pool.ntp.org"
    # Seconds to wait for each NTP server before trying the next one
    ntp_timeout_seconds: float = 3.0
    # Maximum acceptable clock drift (seconds) before a CERT-In alert is logged
    ntp_max_drift_seconds: float = 2.0
    # Run an NTP drift check on application startup
    ntp_sync_on_startup: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("jwt_secret")
    @classmethod
    def secure_secret(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return value

    @field_validator("video_provider")
    @classmethod
    def supported_video_provider(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in {"jitsi", "daily"}:
            raise ValueError("VIDEO_PROVIDER must be either 'jitsi' or 'daily'")
        return value

    @model_validator(mode="after")
    def production_safety_checks(self):
        if not self.production:
            return self

        if self.jwt_secret == "development-only-secret-change-before-production":
            raise ValueError("JWT_SECRET must be replaced in production")
        if not self.data_encryption_key:
            raise ValueError("DATA_ENCRYPTION_KEY is required in production")
        if not self.document_bucket:
            raise ValueError("DOCUMENT_BUCKET is required in production")
        if not self.phonepe_merchant_id or not self.phonepe_salt_key:
            raise ValueError("PhonePe merchant ID and salt key are required in production")
        if self.video_provider == "jitsi" and (not self.jitsi_app_id or not self.jitsi_app_secret):
            raise ValueError("JITSI_APP_ID and JITSI_APP_SECRET are required for production Jitsi rooms")
        if self.video_provider == "daily" and not self.daily_api_key:
            raise ValueError("DAILY_API_KEY is required when VIDEO_PROVIDER=daily in production")
        for origin in self.origins:
            if not origin.startswith("https://"):
                raise ValueError("ALLOWED_ORIGINS must contain only HTTPS origins in production")
        return self
    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]

    @property
    def production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Reset script: delete ALL users (lawyers, clients, admin) and related data,
then seed exactly three demo accounts.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from backend.db import Base, SessionLocal, engine
from backend.models import (
    AuditLog, Booking, LawyerProfile, Message,
    Practice, RefreshToken, Role, User, WebhookEvent,
)
from backend.security import hash_password

Base.metadata.create_all(engine)
db = SessionLocal()

try:
    # Delete everything in dependency order
    db.execute(text("DELETE FROM messages"))
    db.execute(text("DELETE FROM audit_logs"))
    db.execute(text("DELETE FROM refresh_tokens"))
    db.execute(text("DELETE FROM webhook_events"))
    db.execute(text("DELETE FROM bookings"))
    db.execute(text("DELETE FROM lawyer_profiles"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    print("[OK] All existing data deleted.")

    # Seed demo accounts
    pw = hash_password("ChangeMe-Immediately-123!")

    admin = User(email="admin@lawyergrid.com", full_name="LawyerGrid Admin",
                 role=Role.ADMIN, password_hash=pw)
    db.add(admin)
    db.flush()

    lawyer_user = User(email="aanya@lawyergrid.com", full_name="Adv. Aanya Rao",
                       role=Role.LAWYER, password_hash=pw)
    db.add(lawyer_user)
    db.flush()
    db.add(LawyerProfile(
        user_id=lawyer_user.id, practice=Practice.FAMILY,
        bar_number="DL/2014/02841", languages=["English", "Hindi"],
        hourly_fee_minor=180000, rating=4.9, verified=True,
    ))

    client = User(email="client@lawyergrid.com", full_name="Demo Client",
                  role=Role.CLIENT, password_hash=pw)
    db.add(client)

    db.commit()
    print("[OK] Demo accounts created:")
    print("  Admin  -> admin@lawyergrid.com")
    print("  Lawyer -> aanya@lawyergrid.com")
    print("  Client -> client@lawyergrid.com")
    print("  Password (all): ChangeMe-Immediately-123!")
finally:
    db.close()

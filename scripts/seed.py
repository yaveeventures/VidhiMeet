import os
from sqlalchemy import select
from backend.db import Base, SessionLocal, engine
from backend.models import LawyerProfile, Practice, Role, User
from backend.security import hash_password

if os.getenv("ENVIRONMENT", "development") == "production":
    raise SystemExit("Refusing to seed a production environment")

Base.metadata.create_all(engine)
db = SessionLocal()
try:
    records = [
        ("admin@VidhiMeet.com", "VidhiMeet Admin", Role.ADMIN, None),
        ("surajgundi1@gmail.com", "Suraj Gundi", Role.ADMIN, None),
        ("aanya@VidhiMeet.com", "Adv. Aanya Rao", Role.LAWYER, Practice.FAMILY),
        ("client@VidhiMeet.com", "Demo Client", Role.CLIENT, None),
    ]
    for email, name, role, practice in records:
        if db.scalar(select(User).where(User.email == email)):
            continue
        user = User(email=email, full_name=name, role=role,
                    password_hash=hash_password("ChangeMe-Immediately-123!"))
        db.add(user); db.flush()
        if practice:
            db.add(LawyerProfile(user_id=user.id, practice=practice, bar_number="DL/2014/02841",
                                 languages=["English", "Hindi"], hourly_fee_minor=180000,
                                 rating=4.9, verified=True))
    db.commit()
finally:
    db.close()

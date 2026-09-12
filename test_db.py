from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from late_checkout.models import Base, Booking, User

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
u = User(name="t", email="t@e", role="guest")
db.add(u)
db.commit()
dt = datetime.now(timezone.utc)
b = Booking(user_id=u.id, room_number="101", original_checkout=dt)
db.add(b)
db.commit()
db.refresh(b)
print("Saved dt tzinfo:", b.original_checkout.tzinfo)

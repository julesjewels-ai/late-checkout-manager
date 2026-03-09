from typing import Generator

from sqlalchemy.orm import Session

from late_checkout.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

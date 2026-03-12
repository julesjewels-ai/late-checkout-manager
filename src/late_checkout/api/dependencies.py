from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from late_checkout.core.database import SessionLocal
from late_checkout.services.extension import ExtensionService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_extension_service(db: Session = Depends(get_db)) -> ExtensionService:
    return ExtensionService(db=db)

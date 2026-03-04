from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from late_checkout.core.config import settings

# For sqlite we need connect_args={"check_same_thread": False}, but not for postgres.
# Check if it's sqlite to conditionally add the argument.
from sqlalchemy.pool import StaticPool

connect_args = {}
poolclass = None

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if settings.DATABASE_URL == "sqlite:///:memory:":
        poolclass = StaticPool

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    poolclass=poolclass
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

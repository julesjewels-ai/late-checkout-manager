from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from late_checkout.core.config import settings

from sqlalchemy.pool import StaticPool

# For sqlite we need connect_args={"check_same_thread": False}, but not for postgres.
# Check if it's sqlite to conditionally add the argument.
connect_args = {}
poolclass = None
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if settings.DATABASE_URL == "sqlite:///:memory:":
        poolclass = StaticPool

engine_args: dict = {"connect_args": connect_args}
if poolclass:
    engine_args["poolclass"] = poolclass

engine = create_engine(
    settings.DATABASE_URL,
    **engine_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

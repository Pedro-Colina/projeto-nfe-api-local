import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

if os.path.exists(".env.local"):
    load_dotenv(".env.local")
elif os.path.exists(".env"):
    load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada!")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()
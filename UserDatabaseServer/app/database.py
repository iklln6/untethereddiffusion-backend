#from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://comfyuser:comfypass@localhost/comfydb")

print('DATABASE_URL: '+str(DATABASE_URL))


# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


# Session Factory
AsyncSessionLocal = sessionmaker( bind=engine, expire_on_commit=False, class_=AsyncSession )

Base = declarative_base()

# Dependency for getting a session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

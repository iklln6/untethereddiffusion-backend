import asyncio
from fastapi import FastAPI
from app.routes import router
from app.models import Base
from app.database import engine
from sqlalchemy.exc import OperationalError




app = FastAPI()

@app.on_event("startup")
async def startup_event():
    for attempt in range(20):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database connected and initialized")
            break
        except Exception as e:
            print(f"[X] Attempt {attempt+1}/20: Waiting for database to be ready: {str(e)}")
            await asyncio.sleep(5)
    else:
        print("[-] Failed to connect to database after 20 retries")
        raise




app.include_router(router)





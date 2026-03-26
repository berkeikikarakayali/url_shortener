from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from services.shortener import ShortenerService
import models

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def home():
    return {"message": "URL Shortener API çalışıyor"}


@app.post("/shorten")
async def shorten_url(original_url: str, db: AsyncSession = Depends(get_db)):
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url

    new_url = await ShortenerService.create_short_url(db, original_url)

    return {
        "original_url": new_url.original_url,
        "short_code": new_url.short_code,
        "short_url": f"http://localhost:8000/{new_url.short_code}"
    }
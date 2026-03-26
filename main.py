from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from services.shortener import ShortenerService
import models
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
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
    "short_url": f"{BASE_URL}/{new_url.short_code}"
    }

@app.get("/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    url = await ShortenerService.get_by_code(db, short_code)

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url.original_url, status_code=307)
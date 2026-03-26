from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from services.shortener import ShortenerService
from services.analytics import AnalyticsService
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

@app.get("/stats/{short_code}")
async def get_url_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    url = await ShortenerService.get_by_code(db, short_code)

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    clicks = await AnalyticsService.get_clicks_for_url(db, url.id)

    clicks_data = []
    for click in clicks:
        clicks_data.append({
            "id": click.id,
            "ip_address": click.ip_address,
            "user_agent": click.user_agent,
            "country": click.country,
            "device_type": click.device_type,
            "clicked_at": click.clicked_at
        })

    return {
        "original_url": url.original_url,
        "short_code": url.short_code,
        "total_clicks": url.total_clicks,
        "created_at": url.created_at,
        "click_events": clicks_data
    }

@app.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    url = await ShortenerService.get_by_code(db, short_code)

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    await AnalyticsService.record_click(
        db=db,
        url=url,
        ip_address=client_ip,
        user_agent=user_agent
    )

    await ShortenerService.increment_click_count(db, url)

    return RedirectResponse(url=url.original_url, status_code=307)
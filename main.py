from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from database import engine, Base, get_db
from services.shortener import ShortenerService
from services.analytics import AnalyticsService
from services.device import DeviceService
import models
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    total_links = await ShortenerService.get_total_links(db)
    total_clicks = await AnalyticsService.get_total_clicks(db)
    recent_urls = await ShortenerService.get_recent_urls(db)

    recent_links = []
    for url in recent_urls:
        recent_links.append({
            "short_code": url.short_code,
            "short_url": f"{BASE_URL}/{url.short_code}",
            "original_url": url.original_url,
            "total_clicks": url.total_clicks
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "total_links": total_links,
            "total_clicks": total_clicks,
            "recent_links": recent_links
        }
    )


@app.post("/shorten-form", response_class=HTMLResponse)
async def shorten_url_form(
    request: Request,
    original_url: str = Form(...),
    custom_alias: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    try:
        if not original_url.startswith(("http://", "https://")):
            original_url = "https://" + original_url

        alias = custom_alias.strip() if custom_alias else None
        if alias == "":
            alias = None

        new_url = await ShortenerService.create_short_url(db, original_url, alias)

        total_links = await ShortenerService.get_total_links(db)
        total_clicks = await AnalyticsService.get_total_clicks(db)
        recent_urls = await ShortenerService.get_recent_urls(db)

        recent_links = []
        for url in recent_urls:
            recent_links.append({
                "short_code": url.short_code,
                "short_url": f"{BASE_URL}/{url.short_code}",
                "original_url": url.original_url,
                "total_clicks": url.total_clicks
            })

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "short_url": f"{BASE_URL}/{new_url.short_code}",
                "original_url": new_url.original_url,
                "short_code": new_url.short_code,
                "total_links": total_links,
                "total_clicks": total_clicks,
                "recent_links": recent_links
            }
        )
    except Exception as e:
        total_links = await ShortenerService.get_total_links(db)
        total_clicks = await AnalyticsService.get_total_clicks(db)
        recent_urls = await ShortenerService.get_recent_urls(db)

        recent_links = []
        for url in recent_urls:
            recent_links.append({
                "short_code": url.short_code,
                "short_url": f"{BASE_URL}/{url.short_code}",
                "original_url": url.original_url,
                "total_clicks": url.total_clicks
            })

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": f"Something went wrong: {str(e)}",
                "total_links": total_links,
                "total_clicks": total_clicks,
                "recent_links": recent_links
            }
        )


@app.get("/stats/{short_code}", response_class=HTMLResponse)
async def get_url_stats(
    request: Request,
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
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
            "browser": click.browser,
            "clicked_at": click.clicked_at
        })

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "request": request,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "total_clicks": url.total_clicks,
            "created_at": url.created_at,
            "click_events": clicks_data
        }
    )


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

    device_info = DeviceService.parse_user_agent(user_agent)

    await AnalyticsService.record_click(
        db=db,
        url=url,
        ip_address=client_ip,
        user_agent=user_agent,
        device_type=device_info["device_type"],
        browser=device_info["browser"]
    )

    await ShortenerService.increment_click_count(db, url)

    return RedirectResponse(url=url.original_url, status_code=307)
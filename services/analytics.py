from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ClickEvent, ShortenedURL


class AnalyticsService:
    @staticmethod
    async def record_click(
        db: AsyncSession,
        url: ShortenedURL,
        ip_address: str | None = None,
        user_agent: str | None = None,
        country: str | None = None,
        device_type: str | None = None,
        browser: str | None = None
    ) -> ClickEvent:
        click = ClickEvent(
            url_id=url.id,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country,
            device_type=device_type,
            browser=browser
        )

        db.add(click)
        await db.commit()
        await db.refresh(click)

        return click

    @staticmethod
    async def get_clicks_for_url(db: AsyncSession, url_id: int) -> list[ClickEvent]:
        result = await db.execute(
            select(ClickEvent).where(ClickEvent.url_id == url_id)
        )
        return result.scalars().all()
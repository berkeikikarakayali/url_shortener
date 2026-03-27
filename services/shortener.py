import nanoid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ShortenedURL


class ShortenerService:
    ALPHABET = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    CODE_LENGTH = 6

    @staticmethod
    async def generate_unique_code(db: AsyncSession) -> str:
        while True:
            code = nanoid.generate(
                ShortenerService.ALPHABET,
                ShortenerService.CODE_LENGTH
            )

            result = await db.execute(
                select(ShortenedURL).where(ShortenedURL.short_code == code)
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                return code

    @staticmethod
    async def create_short_url( db: AsyncSession, original_url: str, custom_alias: str | None = None ) -> ShortenedURL:
        if custom_alias:
            if " " in custom_alias:
                raise ValueError("Alias cannot contain spaces.")

            result = await db.execute(
                select(ShortenedURL).where(ShortenedURL.short_code == custom_alias)
            )
            existing = result.scalar_one_or_none()

            if existing:
                raise ValueError("This alias is already in use.")

            short_code = custom_alias
        else:
            short_code = await ShortenerService.generate_unique_code(db)

        new_url = ShortenedURL(
            original_url=original_url,
            short_code=short_code
        )

        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)

        return new_url

    @staticmethod
    async def get_by_code(db: AsyncSession, short_code: str) -> ShortenedURL | None:
        result = await db.execute(
            select(ShortenedURL).where(ShortenedURL.short_code == short_code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def increment_click_count(db: AsyncSession, url: ShortenedURL):
        url.total_clicks += 1
        await db.commit()
        await db.refresh(url)

    @staticmethod
    async def get_total_links(db: AsyncSession) -> int:
        result = await db.execute(select(ShortenedURL))
        urls = result.scalars().all()
        return len(urls)

    @staticmethod
    async def get_recent_urls(db: AsyncSession, limit: int = 5) -> list[ShortenedURL]:
        result = await db.execute(
            select(ShortenedURL).order_by(ShortenedURL.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
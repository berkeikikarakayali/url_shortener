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
            code = nanoid.generate(ShortenerService.ALPHABET, ShortenerService.CODE_LENGTH)

            result = await db.execute(
                select(ShortenedURL).where(ShortenedURL.short_code == code)
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                return code

    @staticmethod
    async def create_short_url(db: AsyncSession, original_url: str) -> ShortenedURL:
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
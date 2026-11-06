"""Timepad API: события по городу. Документация: dev.timepad.ru"""

from __future__ import annotations

import asyncio
import logging

import httpx

from src.config import settings
from src.sources.base import RawPost, Source

logger = logging.getLogger(__name__)

API_URL = "https://api.timepad.ru/v1"


class TimepadSource(Source):
    id = "timepad"
    schedule_minutes = 60

    def __init__(self, settings):
        self._client = httpx.AsyncClient(
            base_url=API_URL,
            headers={"Authorization": f"Bearer {settings.timepad_token}"},
            timeout=30.0,
        )
        self._cities = settings.timepad_cities
        self._limit = settings.timepad_limit

    async def fetch(self) -> list[RawPost]:
        params = {
            "cities": self._cities,
            "limit": self._limit,
            "sort_by": "date",
        }
        response = await self._client.get("/events", params=params)

        if response.status_code == 401:
            raise RuntimeError(
                "Timepad: нет/неверный TIMEPAD_TOKEN — проверь .env")
        if response.status_code == 400:  # вдруг параметр называется иначе
            params.pop("sort_by", None)
            response = await self._client.get("/events", params=params)
        response.raise_for_status()

        events = response.json().get("values", [])

        posts = []
        for event in events:
            try:
                posts.append(self._to_raw_post(event))
            except Exception as exc:  # одно кривое событие не должно рвать всю выгрузку
                logger.warning(
                    "Не удалось разобрать событие %s: %s", event.get("id"), exc)

        logger.info("Timepad: получено событий: %d", len(posts))
        return posts

    def _to_raw_post(self, event: dict) -> RawPost:
        external_id = str(event["id"])
        title = event.get("title", "Без названия")
        starts_at = event.get("starts_at", "")
        city = (event.get("location") or {}).get("city", "")
        organizer = (event.get("organizer") or {}).get("name", "")
        url = event.get("url", f"https://timepad.ru/event/{external_id}/")

        description = (event.get("description_short")
                       or event.get("description") or "")
        description = description[:2000]  # не скармливаем LLM простыни

        text = (
            f"Мероприятие: {title}\n"
            f"Начало: {starts_at}\n"
            f"Город: {city}\n"
            f"Организатор: {organizer}\n\n"
            f"{description}"
        ).strip()

        return RawPost(
            source_id=self.id,
            external_id=external_id,
            text=text,
            url=url,
            meta={
                "title": title,
                "starts_at": starts_at,
                "ends_at": event.get("ends_at"),
                "city": city,
                "price": event.get("price"),
                "categories": event.get("categories"),
            },
        )

    async def close(self) -> None:
        await self._client.aclose()


async def _selftest() -> None:
    """Проверка без бота и БД:  python -m src.sources.timepad"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    source = TimepadSource(settings)
    try:
        posts = await source.fetch()
        for post in posts[:5]:
            print("---")
            print(post.url)
            print(post.text[:300])
        print(f"\nВсего: {len(posts)}")
    finally:
        await source.close()


if __name__ == "__main__":
    asyncio.run(_selftest())

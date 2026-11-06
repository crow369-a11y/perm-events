"""Список активных источников. Новый источник = добавить сюда."""

from src.config import Settings
from src.sources.base import Source
from src.sources.timepad import TimepadSource


def build_sources(settings: Settings) -> list[Source]:
    """Собирает все активные источники. Планировщик будет обходить этот список."""
    sources: list[Source] = [
        TimepadSource(settings),
        # TgChannelsSource(settings),   # следующий
        # VkWallSource(settings),
    ]
    return sources

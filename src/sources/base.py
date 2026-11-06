"""Абстрактный Source + RawPost: интерфейс, который реализует каждый источник."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawPost:
    """Сырая единица данных от источника.

    Сохраняется в БД как есть, потом передаётся на извлечение в LLM.
    """

    source_id: str        # "timepad", "tg/perm_it", ...
    external_id: str      # id события/сообщения на стороне источника
    text: str             # текст, который отдаём LLM
    url: str              # ссылка на оригинал / регистрацию
    published_at: datetime | None = None
    meta: dict[str, Any] = field(default_factory=dict)  # всё остальное от источника


class Source(ABC):
    """Общий интерфейс всех источников.

    Добавление нового источника:
    1. унаследоваться от Source и реализовать fetch()
    2. добавить его в registry.py
    Всё. Ни планировщик, ни БД, ни бот менять не нужно.
    """

    #: уникальный идентификатор; используется в дедупликации и настройках
    id: str = "abstract"

    #: как часто опрашивать источник (минуты); планировщик читает это
    schedule_minutes: int = 60

    @abstractmethod
    async def fetch(self) -> list[RawPost]:
        """Вернуть порцию постов с источника."""
        ...

    async def close(self) -> None:
        """Освободить ресурсы (http-клиент и т.п.). Переопредели при необходимости."""
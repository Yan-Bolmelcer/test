import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Добавим путь к корню проекта для импорта core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.utils import star

class Dummy:
    def __init__(self):
        self.called = False

    async def handler(self, update, context):
        self.called = True


@pytest.mark.asyncio
async def test_star_decorator_accepts_short_text():
    dummy = Dummy()
    wrapped = star(10)(dummy.handler)

    class Update:
        class EffectiveChat:
            id = 1
        effective_chat = EffectiveChat()

        class Message:
            text = "Hello"
        message = Message()

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()

    await wrapped(Update(), context)
    assert dummy.called


@pytest.mark.asyncio
async def test_star_decorator_rejects_long_text():
    dummy = Dummy()
    wrapped = star(5)(dummy.handler)

    class Update:
        class EffectiveChat:
            id = 1
        effective_chat = EffectiveChat()

        class Message:
            text = "This is too long"
        message = Message()

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()

    await wrapped(Update(), context)

    # Проверим, что основная функция не вызвана
    assert not dummy.called
    # Проверим, что отправлено сообщение об ошибке
    context.bot.send_message.assert_awaited_once()

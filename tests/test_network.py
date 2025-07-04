import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.network import fetch_json_get, fetch_json_post

@pytest.mark.asyncio
async def test_fetch_json_get_success():
    update = MagicMock()
    update.effective_chat.id = 1

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("core.network.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '{"key": "value"}'

        await fetch_json_get(
            url="https://example.com",
            payload={},
            update=update,
            context=context,
            empty_message="Нет данных"
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited()


@pytest.mark.asyncio
async def test_fetch_json_post_success():
    update = MagicMock()
    update.effective_chat.id = 1

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("core.network.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        await fetch_json_post(
            url="https://example.com",
            payload={},
            update=update,
            context=context,
            fallback_message="Ошибка"
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited()


@pytest.mark.asyncio
async def test_fetch_json_get_failure():
    update = MagicMock()
    update.effective_chat.id = 1

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("core.network.requests.get") as mock_get:
        mock_get.side_effect = Exception("fail")

        await fetch_json_get(
            url="https://example.com",
            payload={},
            update=update,
            context=context,
            empty_message="Нет данных"
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited()


@pytest.mark.asyncio
async def test_fetch_json_post_failure():
    update = MagicMock()
    update.effective_chat.id = 1

    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("core.network.requests.post") as mock_post:
        mock_post.side_effect = Exception("fail")

        await fetch_json_post(
            url="https://example.com",
            payload={},
            update=update,
            context=context,
            fallback_message="Ошибка"
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited()

import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.network import fetch_and_send_file

@pytest.mark.asyncio
async def test_fetch_and_send_file_success(tmp_path):
    update = MagicMock()
    update.effective_chat.id = 123

    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.sendDocument = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    test_content = b"%PDF-1.4 test file"
    with patch("core.network.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = test_content

        await fetch_and_send_file(
            url="https://example.com",
            file_type="TestFile",
            update=update,
            context=context
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.sendDocument.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_and_send_file_failure():
    update = MagicMock()
    update.effective_chat.id = 123

    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("core.network.requests.get") as mock_get:
        mock_get.return_value.status_code = 500

        await fetch_and_send_file(
            url="https://example.com",
            file_type="BrokenFile",
            update=update,
            context=context
        )

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited()
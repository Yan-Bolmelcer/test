import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Добавим путь к корню проекта для импорта core и команд
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.utils import star
from commands.general import start, help_command, about_command

class Dummy:
    def __init__(self):
        self.called = False

    async def handler(self, update, context):
        self.called = True

@pytest.mark.asyncio
async def test_star_decorator_accepts_short_text():
    dummy = Dummy()
    wrapped = star(10)(dummy.handler)

    update = MagicMock()
    update.message.text = "Hello"

    context = MagicMock()
    context.bot.send_message = AsyncMock()

    await wrapped(update, context)
    assert dummy.called

@pytest.mark.asyncio
async def test_star_decorator_rejects_long_text():
    dummy = Dummy()
    wrapped = star(5)(dummy.handler)

    update = MagicMock()
    update.message.text = "This is too long"

    context = MagicMock()
    context.bot.send_message = AsyncMock()

    await wrapped(update, context)
    assert not dummy.called

@pytest.mark.asyncio
async def test_start_command_sends_message():
    update = MagicMock()
    update.effective_chat.id = 123

    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    context.user_data = {}

    with patch("commands.general.help_keyboard", new_callable=AsyncMock) as mock_keyboard:
        mock_keyboard.return_value = "mock_keyboard"
        context.bot.send_message.return_value.message_id = 42

        await start(update, context)

        context.bot.send_chat_action.assert_awaited_once()
        context.bot.send_message.assert_awaited_once()
        assert context.user_data["start_msg_id"] == 42

@pytest.mark.asyncio
async def test_help_command_replaces_previous():
    update = MagicMock()
    update.effective_chat.id = 111

    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.delete_message = AsyncMock()
    context.user_data = {"next_step_msg": 77}

    with patch("commands.general.help_keyboard", new_callable=AsyncMock) as mock_keyboard:
        mock_keyboard.return_value = "markup"
        context.bot.send_message.return_value.message_id = 99

        await help_command(update, context)

        context.bot.delete_message.assert_awaited_once_with(chat_id=111, message_id=77)
        context.bot.send_message.assert_awaited_once()
        assert context.user_data["next_step_msg"] == 99

@pytest.mark.asyncio
async def test_about_command_sends_markdown():
    update = MagicMock()
    update.effective_chat.id = 321

    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    await about_command(update, context)

    context.bot.send_chat_action.assert_awaited_once()
    context.bot.send_message.assert_awaited_once()
    args, kwargs = context.bot.send_message.await_args
    assert kwargs["parse_mode"] == "Markdown"
    assert "🤖 *АРБИС Бот*" in kwargs["text"]
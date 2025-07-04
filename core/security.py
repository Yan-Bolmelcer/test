import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Допусти только авторизованных пользователей (если используется)
AUTHORIZED_USERS = []  # Добавь Telegram ID сотрудников, если нужно

# Минимальный интервал между сообщениями от одного пользователя (сек)
RATE_LIMIT_SECONDS = 3


def is_authorized(user_id: int) -> bool:
    return not AUTHORIZED_USERS or user_id in AUTHORIZED_USERS


def security_checks(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        user_text = update.message.text if update.message else ""

        # 1. Проверка авторизации
        if not is_authorized(user_id):
            logger.warning(f"❌ Неавторизованный пользователь: {user_id}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🚫 У вас нет доступа к этому боту.",
            )
            return

        # 2. Проверка на флуд
        now = datetime.now()
        last_call = context.user_data.get("last_call")
        if last_call and (now - last_call) < timedelta(seconds=RATE_LIMIT_SECONDS):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⏳ Подождите немного перед следующей командой.",
            )
            return
        context.user_data["last_call"] = now

        # 3. Санитарная проверка ввода
        if user_text:
            if len(user_text) > 200:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ Запрос слишком длинный. Пожалуйста, сократите его до 200 символов.",
                )
                return
            if re.search(
                r"(select|insert|<script|drop\s+table)", user_text, re.IGNORECASE
            ):
                logger.warning(f"🛑 Подозрительный ввод от {user_id}: {user_text}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🚫 Некорректный запрос.",
                )
                return

        return await func(update, context, *args, **kwargs)

    return wrapper

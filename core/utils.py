import asyncio
from functools import wraps
from telegram.ext import ContextTypes
from telegram import Update

async def send_typing_action(context: ContextTypes.DEFAULT_TYPE, chat_id: int, delay: float = 0.3):
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    await asyncio.sleep(delay)

def star(n):
    def decorate(fn):
        @wraps(fn)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if len(update.message.text.strip()) > n:
                await inputError(update, context, n)
                return
            await fn(update, context)
        return wrapper
    return decorate

async def inputError(update: Update, context: ContextTypes.DEFAULT_TYPE, n: int):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Вы ввели слишком длинный запрос. Пожалуйста, сократите до {n} символов",
    )

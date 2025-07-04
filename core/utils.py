import asyncio
from telegram.ext import ContextTypes
from telegram import Update

async def send_typing_action(context: ContextTypes.DEFAULT_TYPE, chat_id: int, delay: float = 0.3):
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    await asyncio.sleep(delay)

def star(n):
    def decorate(fn):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if len(update.message.text.strip()) > n:
                await inputError(update, context)
                return
            await fn(update, context)
        return wrapper
    return decorate

async def inputError(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы ввели слишком длинный запрос. Пожалуйста, сократите до 200 символов",
    )

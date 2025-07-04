import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram import ReplyKeyboardMarkup, KeyboardButton

from core.ai import recognize_intent
from core.utils import send_typing_action
from core.security import security_checks

from commands.docs import help_keyboard
from commands.docs import (
    birthday,
    personnelData,
    vacationLeftovers,
    taxCertificate,
    billingStatement,
    vacationWithoutPay,
    getFile,
    checklist,
    feedbackRequest,
)

intent_map = {
    "birthday": birthday,
    "personnel": personnelData,
    "vacation_leftovers": vacationLeftovers,
    "tax_certificate": taxCertificate,
    "billing_statement": billingStatement,
    "vacation_without_pay": vacationWithoutPay,
    "file": getFile,
    "checklist": checklist,
}

WELCOME_MESSAGES = [
    "👋 Привет! Я помогу с документами по работе: справки, отпуск, расчётник и не только. Напиши, что тебе нужно 😊",
    "📄 Привет! Хочешь справку, расчётный лист или в отпуск? Просто напиши, и я помогу.",
    "💼 Добро пожаловать! Я бот, который помогает с кадровыми вопросами. Чем могу помочь?",
    "✉️ Приветствую! Напиши, какой документ или информация тебе нужна — я всё организую.",
]


@security_checks
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    intent = recognize_intent(user_text)

    if not intent:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🤖 Извините, я не совсем понял ваш запрос. Попробуйте выбрать вариант из предложенных ниже.",
            reply_markup=await help_keyboard(),
        )
        return

    func = intent_map.get(intent)
    if func:
        await func(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Интент не реализован"
        )


@security_checks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(context, update.effective_chat.id)
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(random.choice(WELCOME_MESSAGES)),
    )
    context.user_data["start_msg_id"] = msg.message_id


@security_checks
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(context, update.effective_chat.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "🤖 *АРБИС Бот*"
            "Я умею:"
            "- Показывать дни рождения"
            "- Присылать справки и документы"
            "- Помогать с чеклистами и отчетами"
        ),
        parse_mode="Markdown",
    )


@security_checks
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous = context.user_data.get("next_step_msg")
    if previous:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=previous
            )
        except Exception:
            pass
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите доступную команду:",
        reply_markup=await help_keyboard(),
    )
    context.user_data["next_step_msg"] = msg.message_id

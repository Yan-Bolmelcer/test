import datetime
import pytz
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.utils import send_typing_action, star
from core.network import fetch_json_get, fetch_json_post, fetch_and_send_file

LEARN = "РаботаСоСтажерами"
EXIT = "ExitИнтервью"
INTERVIEW = "ИтогиСобеседования"
FEEDBACK = "Feedback"
BASE_URL = "https://dev1.arbis29.ru/ZUP_demo/hs/dataForBot"


async def birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_json_get(
        f"{BASE_URL}/employeeBirthdays",
        {},
        update,
        context,
        "Нет данных о днях рождения",
    )


async def personnelData(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_json_get(
        f"{BASE_URL}/personnelData",
        {"EmployeeId": update.effective_chat.id},
        update,
        context,
        "Нет кадровых данных",
    )


async def vacationLeftovers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = datetime.datetime.now(pytz.timezone("Europe/Moscow")).isoformat()
    await fetch_json_get(
        f"{BASE_URL}/vacationLeftovers",
        {"EmployeeId": update.effective_chat.id, "Date": date},
        update,
        context,
        "Остатков отпусков не найдено",
    )


async def taxCertificate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_json_post(
        f"{BASE_URL}/personalIncomeTaxCertificate",
        {
            "EmployeeId": str(update.effective_chat.id),
            "StartDate": "2022-01-01T00:00:00+03:00",
            "EndDate": "2022-12-31T23:59:59+03:00",
        },
        update,
        context,
        "Ваш запрос на справку 2-НДФЛ обработан",
    )


async def vacationWithoutPay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_json_post(
        f"{BASE_URL}/vacationWithoutPay",
        {
            "EmployeeId": str(update.effective_chat.id),
            "StartDate": "2022-01-01T00:00:00+03:00",
            "EndDate": "2022-12-31T23:59:59+03:00",
        },
        update,
        context,
        "Ваш запрос на отпуск без сохранения обработан",
    )


async def getFile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Укажите тип файла. Например: /file ФайлФАК",
        )
        return
    file_type = " ".join(context.args)
    await fetch_and_send_file(f"{BASE_URL}/file", file_type, update, context)


async def billingStatement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = "2018-03-04T16:11:09.466126+03:00"
    await fetch_and_send_file(
        f"{BASE_URL}/billingStatement", f"BillingStatement_{date}", update, context
    )


async def checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Exit Интервью", callback_data=EXIT),
            InlineKeyboardButton("Итоги Собеседования", callback_data=INTERVIEW),
            InlineKeyboardButton("Работа Со Стажерами", callback_data=LEARN),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите вариант для заполнения:",
        reply_markup=reply_markup,
    )


async def checklistRequest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await fetch_json_get(
        f"{BASE_URL}/checklist",
        {"TypeOfChecklist": query.data},
        update,
        context,
        "Нет данных по чеклисту",
    )


async def feedbackRequest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await update.callback_query.message.edit_reply_markup(None)
    payload = {
        "EmployeeName": "Test",
        "Date": datetime.datetime.now(pytz.timezone("Europe/Moscow")).isoformat(),
        "Content": str(query.data),
        "EmployeeId": str(update.effective_chat.id),
        "Type": "АРБИС_РаботаСоСтажерами",
    }
    await fetch_json_post(
        f"{BASE_URL}/feedback", payload, update, context, "Спасибо! Ваш отзыв принят!"
    )


async def help_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎂 Дни рождения", callback_data="SEND:/birthday")],
        [
            InlineKeyboardButton(
                "📄 Персональные данные", callback_data="SEND:/personnel"
            )
        ],
        [
            InlineKeyboardButton(
                "🧾 Расчетный лист", callback_data="SEND:/billingStatement"
            )
        ],
        [
            InlineKeyboardButton(
                "🏖 Остатки отпусков", callback_data="SEND:/vacationLeftovers"
            )
        ],
        [
            InlineKeyboardButton(
                "📥 Отпуск без содержания", callback_data="SEND:/vacationWithoutPay"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Справка 2-НДФЛ", callback_data="SEND:/taxCertificate"
            )
        ],
        [InlineKeyboardButton("📂 Запрос файла", callback_data="SEND:/file ФайлФАК")],
        [InlineKeyboardButton("✅ Чеклист", callback_data="SEND:/checklist")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def command_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_reply_markup(None)
    command_line = query.data[5:]
    command = command_line.lstrip("/").split()[0]
    commands = {
        "birthday": birthday,
        "personnel": personnelData,
        "billingStatement": billingStatement,
        "vacationLeftovers": vacationLeftovers,
        "vacationWithoutPay": vacationWithoutPay,
        "taxCertificate": taxCertificate,
        "file": getFile,
        "checklist": checklist,
    }
    func = commands.get(command)

    if func:
        context.args = command_line.lstrip("/").split()[1:]
        await func(update, context)
        try:
            await query.message.delete()
        except Exception:
            pass
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Команда не найдена."
        )

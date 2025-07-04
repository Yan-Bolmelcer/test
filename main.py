import logging
import os
from dotenv import load_dotenv
load_dotenv()
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from commands.general import start, about_command, help_command, handle_text
from commands.docs import (
    birthday,
    checklist,
    feedbackRequest,
    checklistRequest,
    command_router,
    personnelData,
    taxCertificate,
    vacationLeftovers,
    vacationWithoutPay,
    getFile,
    billingStatement,
)

from core.utils import star

LEARN = "РаботаСоСтажерами"
EXIT = "ExitИнтервью"
INTERVIEW = "ИтогиСобеседования"
FEEDBACK = "Feedback"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(os.getenv("BOT_TOKEN"))
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("birthday", birthday))
    application.add_handler(CommandHandler("personnel", personnelData))
    application.add_handler(CommandHandler("vacationLeftovers", vacationLeftovers))
    application.add_handler(CommandHandler("taxCertificate", taxCertificate))
    application.add_handler(CommandHandler("vacationWithoutPay", vacationWithoutPay))
    application.add_handler(CommandHandler("file", getFile))
    application.add_handler(CommandHandler("billingStatement", billingStatement))
    application.add_handler(CommandHandler("checklist", checklist))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(command_router, pattern="^SEND:"))
    application.add_handler(
        CallbackQueryHandler(checklistRequest, pattern=f"^{LEARN}|{EXIT}|{INTERVIEW}$")
    )
    application.add_handler(
        CallbackQueryHandler(feedbackRequest, pattern=f"^{FEEDBACK}$")
    )
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    

    application.run_polling()

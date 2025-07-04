import os
import json
import requests
from requests.auth import HTTPBasicAuth
from telegram import Update
from telegram.ext import ContextTypes

from core.utils import send_typing_action
from core.config import BASE_URL, LOGIN


async def fetch_json_get(
    url: str,
    payload: dict,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    empty_message: str,
):
    await send_typing_action(context, update.effective_chat.id)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id, text="⏳ Одну минуточку..."
    )
    try:
        res = requests.get(url, auth=HTTPBasicAuth(LOGIN, ""), params=payload)
        print(res.url)
        text = empty_message
        if res.status_code == 200 and res.text.strip() and res.text != "{}":
            res.encoding = "utf-8"
            text_parse = json.loads(res.text, strict=False)
            if isinstance(text_parse, dict):
                text = "\n".join(f"{k}: {v}" for k, v in text_parse.items())
            elif isinstance(text_parse, list):
                text = "\n".join(str(x) for x in text_parse)
        await message.edit_text(text)
        res.raise_for_status()
    except Exception as err:
        print(f"Error: {err}")
        await message.edit_text("⚠️ Произошла ошибка. Попробуйте позже.")


async def fetch_json_post(
    url: str,
    payload: dict,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    fallback_message: str,
):
    await send_typing_action(context, update.effective_chat.id)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id, text="⏳ Одну минуточку..."
    )
    try:
        res = requests.post(
            url, auth=HTTPBasicAuth(LOGIN, ""), data=json.dumps(payload)
        )
        print(res.url)
        res.encoding = "utf-8"
        text = res.text.strip() or fallback_message
        await message.edit_text(text)
        res.raise_for_status()
    except Exception as err:
        print(f"Error: {err}")
        await message.edit_text("⚠️ Произошла ошибка. Попробуйте позже.")


async def fetch_and_send_file(
    url: str, file_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_typing_action(context, update.effective_chat.id)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id, text="⏳ Одну минуточку..."
    )
    try:
        payload = {"EmployeeId": str(update.effective_chat.id), "FileType": file_type}
        res = requests.get(url, auth=HTTPBasicAuth(LOGIN, ""), params=payload)
        print(res.url)

        if res.status_code == 200 and res.content:
            user_dir = os.path.join("files", str(update.effective_chat.id))
            os.makedirs(user_dir, exist_ok=True)
            file_path = os.path.join(user_dir, f"{file_type}.pdf")

            with open(file_path, "wb") as f:
                f.write(res.content)

            with open(file_path, "rb") as f:
                await context.bot.sendDocument(
                    chat_id=update.effective_chat.id, document=f, caption=f"{file_type}"
                )

            os.remove(file_path)

            await message.delete()
        elif res.status_code == 404:
            await message.edit_text(
                "⚠️ Файл не найден. Проверьте правильность запроса или попробуйте позже."
            )
        else:
            await message.edit_text("⚠️ Не удалось получить файл. Сервер вернул ошибку.")
    except Exception as err:
        print(f"Error while fetching file: {err}")
        await message.edit_text(
            "⚠️ Произошла ошибка при получении файла. Попробуйте позже."
        )

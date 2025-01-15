from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def open_app_kb(webapp_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🏷️ Market", web_app=WebAppInfo(url=webapp_url)))
    return keyboard.as_markup()


def withdraw_kb(request_id: int, amount: float) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text=f"✅ Вывести {amount} TON", callback_data=f"complete_withdraw:{request_id}"
    ))

    return keyboard.as_markup()

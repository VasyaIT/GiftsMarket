from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def open_app_kb(webapp_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🏷️ Market", web_app=WebAppInfo(url=webapp_url)))
    return keyboard.as_markup()

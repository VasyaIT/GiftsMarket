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


def activate_order_kb(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="✅ Выставить", callback_data=f"activate_order:{order_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_order:{order_id}"),
    )
    return keyboard.as_markup()

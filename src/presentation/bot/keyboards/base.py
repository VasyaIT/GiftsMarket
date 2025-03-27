from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def order_kb(gift_type: str, gift_number: int, direct_link: str) -> InlineKeyboardMarkup:
    order_name_text = " ".join(part.capitalize() for part in gift_type.split("_"))
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"🎁 {order_name_text} - #{gift_number}", url=direct_link))
    return keyboard.as_markup()


def stars_order_kb(amount: float, direct_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"⭐ Order for {amount:.2f} Stars", url=direct_link))
    return keyboard.as_markup()

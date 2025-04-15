from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def order_kb(gift_type: str, gift_number: int, direct_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"🎁 {gift_type} - #{gift_number}", url=direct_link))
    return keyboard.as_markup()


def stars_order_kb(amount: float, direct_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"⭐ Order for {amount:.2f} Stars", url=direct_link))
    return keyboard.as_markup()


def giveaway_kb(url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Participate", url=url)
    return keyboard.as_markup()

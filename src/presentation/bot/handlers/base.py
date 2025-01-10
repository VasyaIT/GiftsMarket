from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import CallbackQuery, Message

from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import open_app_kb
from src.presentation.bot.services.text import get_admin_text, get_start_text
from src.presentation.bot.services.user import (
    ban_user,
    get_count_gifts,
    get_count_users,
    unban_user
)
from src.presentation.bot.services.wallet import complete_withdraw_request


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, config: Config) -> None:
    await message.answer(get_start_text(), reply_markup=open_app_kb(config.bot.WEBAPP_URL))


@router.message(Command("admin"))
async def admin_handler(message: Message, config: Config) -> None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    count_users = await get_count_users(config.postgres)
    count_gifts = await get_count_gifts(config.postgres)

    await message.answer(get_admin_text(count_users, count_gifts))


@router.message(F.text.startswith("/ban"))
async def ban_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/ban")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/ban [user id]</code>"
        )
    if await ban_user(config.postgres, user_id):
        return await message.answer(f"✅ Пользователь #{user_id} заблокирован")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(F.text.startswith("/unban"))
async def unban_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/unban")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/unban [user id]</code>"
        )
    if await unban_user(config.postgres, user_id):
        return await message.answer(f"✅ Пользователь #{user_id} разблокирован")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.callback_query(F.data.startswith("withdraw_completed:"))
async def withdraw_success_callback(call: CallbackQuery, config: Config) -> AnswerCallbackQuery | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)

    request_id = call.data.replace("withdraw_completed:", "")
    await complete_withdraw_request(int(request_id), config.postgres)
    await call.message.edit_text(f"{call.message.text}\n\n✅ Вывод исполнен", reply_markup=None)

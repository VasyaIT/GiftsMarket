from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import CallbackQuery, Message

from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import open_app_kb
from src.presentation.bot.services.text import get_start_text
from src.presentation.bot.services.wallet import complete_withdraw_request


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, config: Config) -> None:
    await message.answer(get_start_text(), reply_markup=open_app_kb(config.bot.WEBAPP_URL))


@router.callback_query(F.startswith("withdraw_completed:"))
async def withdraw_success_callback(call: CallbackQuery, config: Config) -> AnswerCallbackQuery | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)

    request_id = call.data.replace("withdraw_completed:", "")
    await complete_withdraw_request(int(request_id), config.postgres)
    await call.message.edit_text(f"{call.message.text}\n\n✅ Вывод исполнен", reply_markup=None)

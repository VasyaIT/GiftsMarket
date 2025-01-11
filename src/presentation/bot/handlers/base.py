from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.methods import AnswerCallbackQuery, SendMessage
from aiogram.types import CallbackQuery, Message

from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import open_app_kb
from src.presentation.bot.services import text, user
from src.presentation.bot.services.market import activate_order
from src.presentation.bot.services.wallet import complete_withdraw_request


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, config: Config) -> None:
    await message.answer(text.get_start_text(), reply_markup=open_app_kb(config.bot.WEBAPP_URL))


@router.message(Command("admin"))
async def admin_handler(message: Message, config: Config) -> None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    count_users = await user.get_count_users(config.postgres)
    count_gifts = await user.get_count_gifts(config.postgres)

    await message.answer(text.get_admin_text(count_users, count_gifts))


@router.message(F.text.startswith("/user"))
async def user_info_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/user")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/user [user id]</code>"
        )
    if not (user_info := await user.get_full_user_info(config.postgres, user_id)):
        return await message.answer(f"✅ Пользователь #{user_id} заблокирован")
    await message.answer(text.get_full_user_info_text(user_info))


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
    if await user.ban_user(config.postgres, user_id):
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
    if await user.unban_user(config.postgres, user_id):
        return await message.answer(f"✅ Пользователь #{user_id} разблокирован")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.callback_query(F.data.startswith("withdraw_completed:"))
async def withdraw_success_callback(
    call: CallbackQuery, config: Config, bot: Bot,
) -> AnswerCallbackQuery | SendMessage | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)

    request_id = call.data.replace("withdraw_completed:", "")
    withdraw_request = await complete_withdraw_request(int(request_id), config.postgres)
    if not withdraw_request:
        return call.message.answer(
            "❌ <b>Ошибка при выводе</b>\n\n"
            f"Заявки на вывод #{request_id} не существует"
        )
    await call.message.edit_text(f"{call.message.text}\n\n✅ Вывод исполнен", reply_markup=None)
    await bot.send_message(
        withdraw_request.user_id,
        f"✅ Your withdrawal of {withdraw_request.amount} TON has been successfully completed"
    )


@router.callback_query(F.data.startswith("activate_order:"))
async def accept_order_callback(
    call: CallbackQuery, config: Config, bot: Bot,
) -> AnswerCallbackQuery | SendMessage | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)

    order_id = call.data.replace("activate_order:", "")
    order = await activate_order(int(order_id), config.postgres)
    if not order:
        return call.message.answer(
            "❌ <b>Ошибка при выставлении подарка</b>\n\n"
            f"Подарка с id: {order_id} не существует"
        )
    await call.message.edit_text(f"{call.message.text}\n\n✅ Подарок выставлен", reply_markup=None)
    await bot.send_message(
        order.seller_id,
        f"✅ Your gift <b>{order.type} - #{order.number}</b> has been successfully put up for sale"
        "⚠️ Be sure to be online, your gift can be bought at any time!"
    )


@router.callback_query(F.data.startswith("reject_order:"))
async def reject_order_callback(
    call: CallbackQuery, config: Config
) -> AnswerCallbackQuery | SendMessage | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)
    await call.message.edit_text(f"{call.message.text}\n\n❌ Подарок отклонён", reply_markup=None)


@router.message(F.text.startswith("/addbalance"))
async def add_balance_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id, amount = message.text.split("/addbalance")[1].split()
        user_id, amount = int(user_id), float(amount)
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды."
            "\nОтправь команду в формате <code>/addbalance [user id] [amount]</code>"
        )
    if await user.add_balance_user(config.postgres, user_id, amount):
        return await message.answer(f"✅ Баланс пользователю #{user_id} пополнен на {amount} TON")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")

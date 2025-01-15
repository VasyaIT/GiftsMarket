from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.methods import AnswerCallbackQuery, SendMessage
from aiogram.types import CallbackQuery, Message

from src.application.common.const import PriceList
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import open_app_kb
from src.presentation.bot.services import market, text, user, wallet


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, config: Config) -> None:
    await message.answer(text.get_start_text(), reply_markup=open_app_kb(config.bot.WEBAPP_URL))


@router.message(Command("admin"))
async def admin_handler(message: Message, config: Config) -> None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    count_users = await user.get_count_users(config.postgres)
    count_all_gifts, count_completed_gifts = await market.get_count_gifts(config.postgres)

    await message.answer(text.get_admin_text(count_users, count_all_gifts, count_completed_gifts))


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


@router.callback_query(F.data.startswith("complete_withdraw:"))
async def withdraw_success_callback(
    call: CallbackQuery, config: Config, bot: Bot,
) -> AnswerCallbackQuery | SendMessage | None:
    if call.from_user.id not in config.bot.moderators_chat_id:
        return call.answer("У тебя нет прав", show_alert=True)

    request_id = call.data.replace("complete_withdraw:", "")
    withdraw_request = await wallet.get_withdraw_request(int(request_id), config.postgres)
    if not withdraw_request:
        return call.message.answer(f"❌ <b>Заявка на вывод #{request_id} уже исполнена</b>")
    await wallet.complete_withdraw_request(int(request_id), config.postgres)
    await wallet.send_transaction(withdraw_request, config.tonapi)
    await call.message.edit_text(
        f"{call.message.text}\n\n✅ Вывод исполнен", reply_markup=None, parse_mode="html"
    )
    await bot.send_message(
        withdraw_request.user_id,
        f"✅ Your withdrawal of {withdraw_request.amount} TON has been successfully completed"
    )


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


@router.message(F.text.startswith("/cancel"))
async def cancel_order_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        order_id = int(message.text.split("/cancel")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/cancel [order id]</code>"
        )

    if await market.cancel_order(order_id, config.postgres):
        return await message.answer(f"✅ Ордер с ID {order_id} отменён")
    await message.answer(f"❌ Ордер с ID {order_id} не найден")


@router.message(F.text.startswith("/confirm"))
async def confirm_order_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        order_id = int(message.text.split("/confirm")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/confirm [order id]</code>"
        )

    if await market.confirm_order(order_id, config):
        return await message.answer(f"✅ Ордер с ID {order_id} завершён")
    await message.answer(f"❌ Ордер с ID {order_id} не найден")


@router.message(F.text.startswith("/order"))
async def order_info_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        gift_type, gift_number = message.text.split("/order")[1].split()
        gift_number = int(gift_number)
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\n"
            "Отправь команду в формате <code>/order [gift_type] [gift number]</code>"
        )

    if not (orders := await market.get_order_info(gift_type.upper(), gift_number, config.postgres)):
        return await message.answer(f"❌ Ордер {gift_type} - #{gift_number} не найден")
    answer_text = ""
    for order in orders:
        answer_text += f"{text.get_order_info_text(order)}\n\n"
        if order.id != orders[-1].id:
            answer_text += "-" * 50 + "\n\n"
    await message.answer(answer_text.strip())


@router.message(F.text.startswith("/delete"))
async def delete_order_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        order_id = int(message.text.split("/delete")[1].strip())
    except ValueError:
        return await message.answer(
            f"❌ Неверный формат команды.\nОтправь команду в формате <code>/delete [order id]</code>"
        )

    if await market.delete_order(order_id, config.postgres):
        return await message.answer(f"✅ Ордер с ID {order_id} удалён")
    await message.answer(f"❌ Ордер с ID {order_id} не найден")

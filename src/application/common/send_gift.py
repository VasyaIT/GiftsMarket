from aiogram import Bot
from pyrogram.client import Client
from pyrogram.errors import BadRequest, PeerIdInvalid, RPCError

from src.application.common.utils import send_message
from src.entrypoint.config import Config


async def send_gift(user_id: int, gift_id: int, client: Client, bot: Bot, config: Config) -> bool:
    is_success, message = False, None

    try:
        is_success = await client.send_gift(user_id, gift_id)
    except (PeerIdInvalid, ValueError):
        message = f"PeerIdInvalid when sending a gift. user id: {user_id}, gift id: {gift_id}"
    except BadRequest:
        message = f"TelegramBadRequest when sending a gift. user id: {user_id}, gift id: {gift_id}"
    except RPCError:
        message = f"RPCError when sending a gift. user id: {user_id}, gift id: {gift_id}"
    except Exception as e:
        message = f"Error when sending a gift. user id: {user_id}, gift id: {gift_id}:\n\n{e}"

    if message:
        await send_message(bot, message, config.bot.owners_chat_id, parse_mode=None)
    return is_success

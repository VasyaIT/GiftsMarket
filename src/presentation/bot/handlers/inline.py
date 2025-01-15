from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.application.common.utils import build_direct_link
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import order_kb
from src.presentation.bot.services.market import get_order


inline_router = Router()
INLINE_IMAGE_URL = ""


@inline_router.inline_query()
async def inline_query(inline_query: InlineQuery, config: Config, bot_username: str) -> None:
    try:
        order_id = int(inline_query.query)
    except ValueError:
        return

    order = await get_order(order_id, config.postgres)
    if not order:
        return

    direct_link = build_direct_link(bot_username, f"gift_{order.id}")
    result = InlineQueryResultArticle(
        id=str(order.id),
        title=f"🎁 {order.type.name} - #{order.number}",
        thumbnail_url=INLINE_IMAGE_URL,
        input_message_content=InputTextMessageContent(
            message_text=f"🎁 {order.type.name} - #{order.number}"
        ),
        reply_markup=order_kb(order.type, order.number, direct_link)
    )

    await inline_query.answer([result])

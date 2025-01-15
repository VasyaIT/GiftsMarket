from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.application.common.const import GIFT_TYPE_MAP, INLINE_IMAGE_URL
from src.application.common.utils import build_direct_link
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import order_kb
from src.presentation.bot.services.market import get_gift


inline_router = Router()


@inline_router.inline_query()
async def inline_query(inline_query: InlineQuery, config: Config, bot_username: str) -> None:
    try:
        order_id = int(inline_query.query)
    except ValueError:
        return

    order = await get_gift(order_id, config.postgres)
    if not order:
        return

    direct_link = build_direct_link(bot_username, f"gift_{order.id}")
    order_name_text = [key for key, value in GIFT_TYPE_MAP.items() if value == order.type][0]
    rarity_text = f"🪙 Rarity: {order.rarity.name}" if order.rarity else ""
    result = InlineQueryResultArticle(
        id=str(order.id),
        title=f"🎁 {order_name_text} - #{order.number}",
        thumbnail_url=INLINE_IMAGE_URL,
        input_message_content=InputTextMessageContent(
            message_text=(
                f"💸 <b>{order_name_text} - #{order.number} in Nest Store!</b>\n\n"
                f"💎 Price: {order.price:.2f} TON\n"
                f"🔦 Background: {order.background}%\n"
                f"❄️ Pattern: {order.pattern}%\n"
                f"🎃 Model: {order.model}%\n"
                f"{rarity_text}"
            )
        ),
        reply_markup=order_kb(order.type, order.number, direct_link)
    )

    await inline_query.answer([result])

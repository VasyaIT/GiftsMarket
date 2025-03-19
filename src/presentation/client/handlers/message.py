from pyrogram.client import Client
from pyrogram.enums import GiftAttributeType
from pyrogram.types import Message

from src.application.common.const import GIFT_TYPE_MAP
from src.application.common.utils import calculate_gift_rarity
from src.domain.entities.market import CreateOrderDM
from src.entrypoint.config import Config
from src.presentation.bot.services.market import create_order
from src.presentation.bot.services.user import create_user_if_not_exist


async def receive_gift(client: Client, message: Message) -> Message | None:
    if not (gift := message.gift) or not gift.attributes:
        return
    if not (user := message.from_user) or client.me and client.me.id == user.id:
        return

    pattern = model = background = 0
    for attribute in gift.attributes:
        attribute_rarity = attribute.rarity / 10 if attribute.rarity else 0
        if attribute.type is GiftAttributeType.MODEL and attribute.name:
            model, model_name = attribute_rarity, attribute.name
        elif attribute.type is GiftAttributeType.BACKDROP and attribute.name:
            background, background_name = attribute_rarity, attribute.name
        elif attribute.type is GiftAttributeType.SYMBOL and attribute.name:
            pattern, pattern_name = attribute_rarity, attribute.name

    gift_type = GIFT_TYPE_MAP.get(gift.title or "")
    if not gift_type:
        return await message.reply_text("This gift was not found in the nest store.")

    config = Config()
    await create_user_if_not_exist(user.id, user.username, user.first_name, config.postgres)

    order_data = CreateOrderDM(
        id=gift.id,
        seller_id=user.id,
        number=gift.number if gift.number else 0,
        type=gift_type,
        pattern=pattern,
        model=model,
        background=background,
        pattern_name=pattern_name,
        model_name=model_name,
        background_name=background_name,
        rarity=calculate_gift_rarity(model),
        is_active=False,
    )
    await create_order(order_data, config.postgres)
    text = (
        "✅ Your gift has been successfully uploaded to the store.\n\n"
        "Go to the @nestore_robot and post a gift to the market"
    )
    await client.send_message(user.id, text)

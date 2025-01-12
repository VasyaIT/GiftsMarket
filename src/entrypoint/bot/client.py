import sys
from pathlib import Path

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.enums import GiftAttributeType
from pyrogram.types import Message


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))


from src.application.common.const import GIFT_TYPE_MAP  # noqa: E402
from src.application.common.utils import calculate_gift_rarity, get_bot, send_message  # noqa: E402
from src.domain.entities.market import CharacteristicsOrderDM  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.presentation.bot.services.market import get_all_inactive, update_order  # noqa: E402


config = Config()
bot = get_bot(config.bot.BOT_TOKEN)
app = Client("my_account", config.bot.API_ID, config.bot.API_HASH)


@app.on_message(filters.private)
async def check_user_gifts(client: Client, message: Message) -> Message | None:
    if not (user := message.from_user):
        return
    if not user.username:
        return await client.send_message(
            user.id,
            "Add a username to your account to send a gift"
        )
    gifts = await get_all_inactive(user.id, config.postgres)
    if not gifts:
        return await client.send_message(
            user.id,
            "Your newly created gifts were not found in the application"
        )

    pattern = model = background = 0
    gift_is_exist = False
    for user_gift in gifts:
        async for gift in client.get_user_gifts(user.username):
            if (
                gift.number == user_gift.number and gift.title
                and GIFT_TYPE_MAP.get(gift.title) == user_gift.type
            ):
                if not gift.attributes:
                    continue
                for attribute in gift.attributes:
                    attribute_rarity = attribute.rarity / 10 if attribute.rarity else 0
                    if attribute.type is GiftAttributeType.MODEL:
                        model = attribute_rarity
                    elif attribute.type is GiftAttributeType.BACKDROP:
                        background = attribute_rarity
                    elif attribute.type is GiftAttributeType.SYMBOL:
                        pattern = attribute_rarity
                characteristics = CharacteristicsOrderDM(
                    pattern=pattern,
                    model=model,
                    background=background,
                    rarity=calculate_gift_rarity(model),
                    is_active=True,
                )
                gift_is_exist = True
                await update_order(characteristics.model_dump(), user_gift.id, config.postgres)
                await client.send_message(
                    user.id,
                    f"✅ Gift <b>{user_gift.type.name} - #{user_gift.number}</b> "
                    "has been successfully placed in the store!"
                )
                await send_message(
                    bot,
                    f"➕ @{user.username} #<code>{user.id}</code> выставил новый подарок: "
                    f"<b>{user_gift.type.name} - #{user_gift.number}</b>",
                    [config.bot.DEPOSIT_CHAT_ID],
                    message_thread_id=config.bot.MODERATION_THREAD_ID,
                )
        if not gift_is_exist:
            await client.send_message(
                user.id,
                f"❌ The gifts you created in the app are not found in your profile\n"
                "⚠️ Make sure you entered the gift number and type correctly in the app\n\n"
                "<i>Perhaps they are hidden, try to turn on the visibility of gifts</i>"
            )


app.run()

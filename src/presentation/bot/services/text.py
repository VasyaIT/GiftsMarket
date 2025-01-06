def get_buy_gift_text(type_name: str, gift_number: int, buyer_username: str) -> str:
    return (
        f"💰 Your gift was bought - <b>{type_name} #{gift_number}</b>\n\n"
        f"📤 Transfer your gift {buyer_username}, then go to the market and confirm the transfer of the gift"
    )


def get_cancel_gift_text(type_name: str, gift_number: int) -> str:
    return (
        f"❗ The buyer canceled the purchase of your gift - <b>{type_name} #{gift_number}</b>\n\n"
        "⚠️ <b>Don't transfer your gift! If the transfer has occurred, please contact support</b>"
    )


def get_confirm_transfer_text(type_name: str, gift_number: int) -> str:
    return (
        f"✅ The seller transferred you a gift - <b>{type_name} #{gift_number}</b>\n\n"
        "Go to the market and confirm receipt of the gift\n\n"
        "⚠️ <i>Be sure to check if you have received the gift for real!"
        "Check your profile, and only then confirm receipt!</i>"
    )


def get_accept_transfer_text(type_name: str, gift_number: int) -> str:
    return f"✅ The order was completed successfully - <b>{type_name} #{gift_number}</b>"


def get_withdraw_request_text(username: str | None, user_id: int, amount: float, wallet: str) -> str:
    username_text = "" if not username else f"@{username} "
    return (
        f"👛 Заявка на вывод средств от пользователя {username_text}#<code>{user_id}</code>"
        f"\n\nСумма: <b>{amount}</b> TON\nАдрес кошелька: <code>{wallet}</code>"
    )


def get_start_text() -> str:
    return (
        "🎁 <b>The best gift market in Telegram is already here!</b>\n\n"
        "🔥 Buy and sell gifts quickly and securely!"
    )


def get_deposit_text(
    username: str | None, user_id: int, is_testnet: bool, ton_amount: float, hash: str
) -> str:
    user_data_text = f"{f'@{username}' if username else ''} #<code>{user_id}</code>"
    link_text = "testnet." if is_testnet else ""
    return (
        f"💸 {user_data_text.strip()} пополнил баланс на {ton_amount} TON\n\n"
        f"🔗 <b><a href='https://{link_text}tonviewer.com/transaction/{hash}'>Транзакция</a></b>"
    )


def get_canceled_text_to_owner(username: str | None, user_id: int) -> str:
    username_text = "" if not username else f"@{username} "
    return (
        f"❗ Пользователь {username_text}#<code>{user_id}</code> отменил покупку подарка!\n\n"
        "⚠️ Если он создаст заявку на вывод в ближайшее время, убедитесь, что продавец не передал ему подарок"
    )

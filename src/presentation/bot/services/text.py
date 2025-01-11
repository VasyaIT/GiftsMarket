from src.domain.entities.user import FullUserInfoDM
bfrom src.application.common.const import SECONDS_TO_SEND_GIFT


def get_buy_gift_text(type_name: str, gift_number: int) -> str:
    return (
        f"💰 Your gift was bought - <b>{type_name} #{gift_number}</b>\n\n"
        f"📤 Confirm or cancel the order in the app"
    )


def get_cancel_gift_text(type_name: str, gift_number: int) -> str:
    return (
        f"❗ The buyer canceled the purchase of your gift - <b>{type_name} #{gift_number}</b>\n\n"
        "⚠️ <b>Don't transfer your gift! If the transfer has occurred, please contact support</b>"
    )


def get_seller_accept_text(type_name: str, gift_number: int) -> str:
    return (
        f"✅ The seller accepted your deal for a gift - <b>{type_name} #{gift_number}</b>\n\n"
        f"🕑 Wait for the seller to send you a gift and you will receive a notification in the bot"
    )


def get_seller_cancel_text(type_name: str, gift_number: int) -> str:
    return (
        f"❌ The seller canceled your gift order - <b>{type_name} #{gift_number}</b>\n\n"
        f"💸 The TONs have been returned to your balance in the app"
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


def get_admin_text(count_users: int, count_gifts: int) -> str:
    return (
        f"<b>Количество пользователей</b>: {count_users}\n<b>Количество подарков</b>: {count_gifts}"
    )


def get_seller_canceled_admin_text(username: str | None, user_id: int) -> str:
    username_text = "" if not username else f"@{username} "
    return (
        f"❗ {username_text}#<code>{user_id}</code> не отправил подарок в течение {SECONDS_TO_SEND_GIFT} минут. "
        "Сделка отменена!"
        "\n\n⚠️ Если этот пользователь часто игнорирует сделку, "
        "вы можете заблокировать его отправив <code>/ban [user id]</code>"
    )


def get_full_user_info_text(user_info_data: FullUserInfoDM) -> str:
    username_text = f"👨‍🦱 <b>Username</b>: <b>@{user_info_data.username}</b>\n"
    first_name_text = f"🗿 <b>Имя</b>: <b>@{user_info_data.first_name}</b>\n"
    if not user_info_data.username:
        username_text = ""
    if not user_info_data.first_name:
        first_name_text = ""

    orders_text = f"\n🛍️ <b>Последние ордера: </b>"
    for order in user_info_data.orders[:7]:
        user_text = "покупатель" if order.buyer_id == user_info_data.id else "продавец"
        completed_date_text = "\n"
        if order.completed_order_date:
            completed_date_text = f"\n<b>Дата завершения: </b>{order.completed_order_date}\n"
        orders_text += (
            f"\n<b>ID: </b>{order.id}\n<b>Подарок</b>:  <b>{order.type} #{order.number}</b>"
            f"\n<b>Цена: </b>{order.price}\n<b>Дата создания: </b>{order.created_order_date}"
            f"<b>Статус: </b>{order.status.name}\n<b>Пользователь: </b>{user_text}{completed_date_text}"
        )
    if not user_info_data.orders:
        orders_text = ""

    withdraws_text = f"\n👛 <b>Последние выводы:</b>"
    for withdraw in user_info_data.withdraw_requests[:5]:
        withdraws_text += f"\n<code>{withdraw.wallet}</code> - {withdraw.amount} TON"
    if not user_info_data.withdraw_requests:
        withdraws_text = ""

    return (
        f"🔒 ID: <code>{user_info_data.id}</code>\n"
        f"{username_text}"
        f"{first_name_text}"
        f"💰 <b>Баланс: </b>{user_info_data.balance:.2f} TON\n"
        f"📅 <b>Дата регистрации: </b>{user_info_data.created_at.strftime("%d.%m.%y, %H:%M")}\n"
        f"{orders_text.rstrip()}"
        f"{withdraws_text}\n"
        f"💸 <b>Общая выведенная сумма: </b>{user_info_data.total_withdrawn} TON"
    )

from src.application.common.const import MINUTES_TO_SEND_GIFT
from src.domain.entities.market import OrderDM
from src.domain.entities.user import FullUserInfoDM


def get_buy_gift_text(type_name: str, gift_number: int) -> str:
    return (
        f"💰 Your gift was bought - <b>{type_name} #{gift_number}</b>"
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


def get_buy_stars_text(amount: float) -> str:
    return (
        f"💰 Your stars was bought - <b>{amount:.2f} ⭐</b>\n\n"
        f"📤 Confirm or cancel the order in the app"
    )


def get_cancel_star_text(amount: float) -> str:
    return (
        f"❗ The buyer canceled the purchase of your stars - <b>{amount:.2f} ⭐</b>"
    )


def get_seller_accept_star_text(amount: float) -> str:
    return (
        f"✅ The seller accepted your deal for a {amount:.2f} Stars\n\n"
        f"🕑 Wait for the seller to send you a Stars and you will receive a notification in the bot"
    )


def get_seller_cancel_star_text(amount: float) -> str:
    return (
        f"❌ The seller canceled order for buy {amount:.2f} Stars\n\n"
        f"💸 The TONs have been returned to your balance in the app"
    )


def get_confirm_transfer_stars_text(amount: float) -> str:
    return (
        f"✅ The seller transferred you {amount:.2f} Stars\n\n"
        "Go to the market and confirm receipt of the Stars\n\n"
        "⚠️ <i>Be sure to check if you have received the Stars for real!</i>"
    )


def get_accept_transfer_stars_text(amount: float) -> str:
    return f"✅ The order for {amount:.2f} Stars was completed successfully"


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


def get_admin_text(
    count_users: int, count_gifts: int, count_completed_gifts: int, total_balance: float
) -> str:
    return (
        f"<b>Количество пользователей</b>: {count_users}\n<b>Количество подарков</b>: {count_gifts}"
        f"\n<b>Количество завершённых сделок</b>: {count_completed_gifts}\n"
        f"<b>Общий баланс пользователей: </b>{total_balance:.1f} TON"
    )


def get_seller_canceled_admin_text(user_id: int) -> str:
    return (
        f"❗ Пользователь #<code>{user_id}</code> не отправил подарок в течение {MINUTES_TO_SEND_GIFT} минут. "
        "Сделка отменена!"
        "\n\n⚠️ Если этот пользователь часто игнорирует сделку, "
        "вы можете заблокировать его отправив <code>/ban [user id]</code>"
    )


def get_full_user_info_text(user_info_data: FullUserInfoDM) -> str:
    username_text = f"👨‍🦱 <b>Username</b>: <b>@{user_info_data.username}</b>\n"
    first_name_text = f"🗿 <b>Имя</b>: <b>{user_info_data.first_name}</b>\n"
    if not user_info_data.username:
        username_text = ""
    if not user_info_data.first_name:
        first_name_text = ""

    orders_text = f"\n🛍️ <b>Последние ордера: </b>"
    for order in user_info_data.orders[:5]:
        user_text = "покупатель" if order.buyer_id == user_info_data.id else "продавец"
        completed_date_text = "\n"
        if order.completed_order_date:
            completed_date_text = f"\n<b>Дата завершения: </b>{order.completed_order_date}\n"
        orders_text += (
            f"\n<b>ID: </b>{order.id}\n<b>Подарок</b>:  <b>{order.type.name} #{order.number}</b>"
            f"\n<b>Цена: </b>{order.price} TON"
            f"\n<b>Пользователь: </b>{user_text}{completed_date_text}"
        )
    if not user_info_data.orders:
        orders_text = ""

    withdraws_text = f"\n👛 <b>Последние выводы:</b>"
    for withdraw in user_info_data.withdraw_requests[:5]:
        withdraws_text += f"\n<code>{withdraw.wallet}</code> - {withdraw.amount:.2f} TON"
    withdraws_text += "\n"
    if not user_info_data.withdraw_requests:
        withdraws_text = ""

    return (
        f"🔒 ID: <code>{user_info_data.id}</code>\n"
        f"{username_text}"
        f"{first_name_text}"
        f"💰 <b>Баланс: </b>{user_info_data.balance:.2f} TON\n"
        f"📅 <b>Дата регистрации: </b>{user_info_data.created_at.strftime("%d.%m.%y, %H:%M")}\n"
        f"{orders_text}"
        f"{withdraws_text}"
        f"\n💸 <b>Общая выведенная сумма: </b>{user_info_data.total_withdrawn} TON"
    )


def get_order_info_text(order_info: OrderDM) -> str:
    buyer_text = ""
    if order_info.buyer_id:
        buyer_text = f"👨‍🦱 <b>Продавец: </b>@{order_info.seller_id} #<code>{order_info.buyer_id}</code>\n"
    created_order_text = ""
    completed_order_text = ""
    if order_info.completed_order_date:
        completed_order_text = (
            f"📅 <b>Дата завершения сделки: </b>{order_info.completed_order_date.strftime("%d.%m.%y, %H:%M")}"
        )

    return (
        f"🔒 ID: <code>{order_info.id}</code>\n"
        f"🔎 Тип: <code>{order_info.type.name}</code>\n"
        f"➕ Номер: <code>{order_info.number}</code>\n"
        f"💰 <b>Цена: </b>{order_info.price} TON\n\n"
        f"{buyer_text}"
        f"🔦 <b>Модель: </b>{order_info.model}%\n"
        f"❄️ <b>Фон: </b>{order_info.background}%\n"
        f"🎃 <b>Узор: </b>{order_info.pattern}%\n\n"
        f"{created_order_text}"
        f"{completed_order_text}"
    )

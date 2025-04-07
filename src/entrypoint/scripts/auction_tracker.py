import asyncio
import sys
from datetime import datetime
from pathlib import Path

from bullmq import Queue


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.application.common.const import HistoryType  # noqa: E402
from src.domain.entities.history import CreateHistoryDM  # noqa: E402
from src.domain.entities.user import UpdateUserBalanceDM  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.history import HistoryGateway  # noqa: E402
from src.infrastructure.gateways.market import MarketGateway  # noqa: E402
from src.infrastructure.gateways.user import UserGateway  # noqa: E402


async def start_auction_tracker() -> None:
    config = Config()
    session_maker = new_session_maker(config.postgres)
    queue = Queue("gifts", {"connection": config.redis.REDIS_URL})  # type: ignore

    async with session_maker() as session:
        market_gateway, user_gateway = MarketGateway(session), UserGateway(session)
        history_gateway = HistoryGateway(session)
        orders = await market_gateway.get_auction_orders()
        if not orders:
            return
        for order in orders:
            if not order.buyer_id:
                data = dict(is_active=False, min_step=None, auction_end_time=None, price=None)
                await market_gateway.withdraw_from_market(data, id=order.id)
                await market_gateway.delete_auction_bids(gift_id=order.id)
                await session.commit()
                return
            now = datetime.now()
            updated_data = {"is_completed": True, "completed_order_date": now}
            await market_gateway.update_order(updated_data, id=order.id)
            await user_gateway.update_balance(
                UpdateUserBalanceDM(id=order.seller_id, amount=order.price)
            )
            await history_gateway.save(
                CreateHistoryDM(
                    user_id=order.buyer_id,
                    type=HistoryType.FINAL_BID_GIFT,
                    price=order.price,
                    gift=order.type,
                    gift_number=order.number,
                    model_name=order.model_name,
                )
            )
            await session.commit()

            await queue.add("send_gift", {"user_id": order.buyer_id, "gift_id": order.gift_id})

    await queue.close()


if __name__ == "__main__":
    asyncio.run(start_auction_tracker())

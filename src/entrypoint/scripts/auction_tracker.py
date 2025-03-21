import asyncio
import sys
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.domain.entities.user import UpdateUserBalanceDM  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.market import MarketGateway  # noqa: E402
from src.infrastructure.gateways.user import UserGateway  # noqa: E402


async def start_auction_tracker() -> None:
    config = Config()
    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        market_gateway, user_gateway = MarketGateway(session), UserGateway(session)
        orders = await market_gateway.get_auction_orders()
        if not orders:
            return
        for order in orders:
            now = datetime.now()
            if order.auction_end_time and order.auction_end_time > now:
                updated_data = {"is_completed": True, "completed_order_date": now}
                await market_gateway.update_order(updated_data, id=order.id)
                await user_gateway.update_balance(
                    UpdateUserBalanceDM(id=order.seller_id, amount=order.price)
                )
                await session.commit()


if __name__ == "__main__":
    asyncio.run(start_auction_tracker())

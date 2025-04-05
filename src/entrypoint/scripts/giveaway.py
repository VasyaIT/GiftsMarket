import asyncio
import sys
from pathlib import Path

from bullmq import Queue


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.giveaway import GiveawayGateway  # noqa: E402


async def start_giveaway_tracker() -> None:
    config = Config()
    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        giveaway_gateway = GiveawayGateway(session)
        gateways = await giveaway_gateway.get_ended_giveaways()
        if not gateways:
            return
        for giveaway in gateways:
            await session.commit()

            queue = Queue("gifts", {"connection": config.redis.REDIS_URL})  # type: ignore
            await queue.add("send_gift", {"user_id": giveaway.buyer_id, "gift_id": order.gift_id})
            await queue.close()


if __name__ == "__main__":
    asyncio.run(start_giveaway_tracker())

import asyncio
import sys
from pathlib import Path

from bullmq import Queue


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.giveaway import GiveawayGateway  # noqa: E402
from src.infrastructure.gateways.market import MarketGateway  # noqa: E402


async def start_giveaway_tracker() -> None:
    config = Config()
    queue = Queue("gifts", {"connection": config.redis.REDIS_URL})  # type: ignore
    session_maker = new_session_maker(config.postgres)

    async with session_maker() as session:
        giveaway_gateway, market_gateway = GiveawayGateway(session), MarketGateway(session)
        gateways = await giveaway_gateway.get_ended_giveaways()
        if not gateways:
            return
        for giveaway in gateways:
            winners_ids = []
            gifts = await market_gateway.get_user_gifts_by_ids(giveaway.gifts_ids)
            count_participants = len(giveaway.participants_ids)
            if count_participants:
                tasks = []
                for index, gift in enumerate(gifts):
                    user_id = giveaway.participants_ids[index % count_participants]
                    winners_ids.append(user_id)
                    tasks.append(queue.add("send_gift", {"user_id": user_id, "gift_id": gift.gift_id}))
                await asyncio.gather(*tasks)
            else:
                await market_gateway.update_giveaway_gifts({"is_completed": False}, giveaway.gifts_ids)

            await giveaway_gateway.update_giveaway(
                {"is_completed": True, "winners_ids": winners_ids}, id=giveaway.id
            )
            await session.commit()

    await queue.close()


if __name__ == "__main__":
    asyncio.run(start_giveaway_tracker())

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
            count_participants = len(giveaway.participants_ids)
            for index, gift_id in enumerate(giveaway.gifts_ids):
                user_id = giveaway.participants_ids[index % count_participants]
                queue = Queue("gifts", {"connection": config.redis.REDIS_URL})  # type: ignore
                await queue.add("send_gift", {"user_id": user_id, "gift_id": gift_id})
                await queue.close()

            await giveaway_gateway.update_giveaway({"is_completed": True}, id=giveaway.id)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(start_giveaway_tracker())

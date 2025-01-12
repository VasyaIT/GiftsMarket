import asyncio
import sys
from pathlib import Path

from aiogram.exceptions import TelegramAPIError
from aiogram.types.input_file import FSInputFile


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.application.common.utils import get_bot  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.user import UserGateway  # noqa: E402


async def send_broadcast_message(message: str, photo_path: str) -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    photo = FSInputFile(photo_path)
    session_maker = new_session_maker(config.postgres)

    async with session_maker() as session:
        gateway = UserGateway(session)
        users = await gateway.get_all()

    for user in users:
        try:
            await bot.send_photo(user.id, photo, caption=message)
        except TelegramAPIError:
            pass
        await asyncio.sleep(0.2)

    await bot.session.close()


if __name__ == "__main__":
    message = ""
    photo_path = ""
    asyncio.run(send_broadcast_message(message, photo_path))

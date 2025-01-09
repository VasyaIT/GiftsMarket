import asyncio
import sys
from pathlib import Path

from aiogram.types.input_file import FSInputFile


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.application.common.utils import get_bot  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402


async def send_dump_file() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    file = FSInputFile(config.app.DB_DUMP_FILE_PATH)
    for owner_chat_id in config.bot.owners_chat_id:
        await bot.send_document(owner_chat_id, file)
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(send_dump_file())

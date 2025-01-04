import asyncio
import sys
from pathlib import Path
from traceback import format_exc

from aiogram.utils.markdown import hpre


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from entrypoint.config import Config  # noqa: E402
from infrastructure.tonapi.deposit import run_tracker  # noqa: E402
from src.application.common.utils import get_bot, send_message  # noqa: E402


async def start_deposit_tracker() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    try:
        await run_tracker(config, bot)
    except Exception:
        message = f"DEPOSIT TRACKER ERROR:\n{format_exc(chain=False)[:4000]}"
        await send_message(bot, hpre(message), config.bot.owners_chat_id)
        raise


if __name__ == "__main__":
    asyncio.run(start_deposit_tracker())

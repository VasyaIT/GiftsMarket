import asyncio
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.entrypoint.bot.run import start_bot  # noqa: E402


def main() -> None:
    asyncio.run(start_bot())


if __name__ == "__main__":
    print("Bot started")
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")

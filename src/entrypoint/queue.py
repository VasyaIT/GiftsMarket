import asyncio
import signal
from typing import Callable

from aiogram import Bot
from bullmq.job import Job
from bullmq.types import WorkerOptions
from bullmq.worker import Worker
from pyrogram.client import Client

from src.application.common.send_gift import send_gift
from src.entrypoint.config import Config


class CustomWorker(Worker):
    def __init__(
        self,
        name: str,
        processor: Callable[[Job, str, Client, Bot, Config], asyncio.Future],
        client: Client,
        bot: Bot,
        config: Config,
        opts: WorkerOptions = {},
    ) -> None:
        super().__init__(name, processor, opts)  # type: ignore
        self.telegram_client = client
        self.processor = processor
        self.bot = bot
        self.config = config

    async def processJob(self, job: Job, token: str) -> None:
        self.jobs.add((job, token))
        result = await self.processor(job, token, self.telegram_client, self.bot, self.config)
        if not self.forceClosing:
            await self.scripts.moveToCompleted(
                job,
                result,
                job.opts.get("removeOnComplete", False),
                token,
                self.opts,
                fetchNext=False,
            )
            job.returnvalue = result
            job.attemptsMade = job.attemptsMade + 1
        self.emit("completed", job, result)
        self.jobs.remove((job, token))


async def process(job, _, client: Client, bot: Bot, config: Config) -> None:
    await send_gift(
        int(job.data.get("user_id") or 0), int(job.data.get("gift_id") or 0), client, bot, config
    )


async def run_queue(client: Client, bot: Bot, config: Config) -> None:
    shutdown_event = asyncio.Event()

    def signal_handler(signal, frame) -> None:
        print("Signal received, shutting down.")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    worker = CustomWorker("gifts", process, client, bot, config, {"connection": config.redis.REDIS_URL})  # type: ignore

    await shutdown_event.wait()
    await worker.close()
    asyncio.get_running_loop().stop()

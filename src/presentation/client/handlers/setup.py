from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers.message_handler import MessageHandler

from src.presentation.client.handlers.message import receive_gift


def setup_client_handlers(client: Client) -> None:
    client.add_handler(MessageHandler(receive_gift, filters=filters.private))

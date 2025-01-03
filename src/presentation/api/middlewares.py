from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.entrypoint.config import AppConfig


def setup_middlewares(app: FastAPI, app_config: AppConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_allowed_origins,
        allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
        allow_credentials=True
    )

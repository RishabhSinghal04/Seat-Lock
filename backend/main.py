import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core import Config, dispose_engine, get_config, init_engine, setup_logging
from fastapi import FastAPI
from granian import Granian
from granian.constants import Interfaces

logger: logging.Logger = logging.getLogger(__name__)

config: Config = get_config()
setup_logging(debug=config.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("starting app")
    init_engine()
    yield
    await dispose_engine()
    logger.info("shutdown complete")


app = FastAPI(lifespan=lifespan, version="0.0.1", title="SeatLock")


if __name__ == "__main__":
    Granian(
        target="main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
        reload_ignore_dirs=["logs"],
    ).serve()

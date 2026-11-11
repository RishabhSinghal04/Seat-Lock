import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from granian import Granian
from granian.constants import Interfaces

from app.core import Config, dispose_engine, get_config, init_engine, setup_logging
from app.core.exceptions.base import AppError

logger: logging.Logger = logging.getLogger(__name__)

config: Config = get_config()
setup_logging(debug=config.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("starting app")
    init_engine()
    yield
    await dispose_engine()
    logger.info("shutdown complete")


app = FastAPI(lifespan=lifespan, version="0.0.1", title="SeatLock")


@app.exception_handler(AppError)
async def global_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        content={
            "error": exc.message,
            "code": exc.status_code,
            "path": str(request.url),
            "extra": exc.extra,
        },
        status_code=exc.status_code,
    )


if __name__ == "__main__":
    Granian(
        target="app.main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
        reload_ignore_dirs=["logs"],
    ).serve()

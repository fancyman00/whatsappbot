from contextlib import asynccontextmanager

from app.services.database import create_tables
from fastapi import FastAPI

from app.api.webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    print("FastAPI завершил работу.")


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(webhook_router)
    return app


app = get_app()

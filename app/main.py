from fastapi import APIRouter, FastAPI
from fastapi.concurrency import asynccontextmanager

from app.infrastructure.logging.logging import setup_logging
from app.infrastructure.redis.client import close_redis
from app.presentation.middleware.logging import LoggingMiddleware
from app.presentation.routers.templates import router as templates_router
from app.presentation.routers.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    yield

    await close_redis()


app = FastAPI(
    title="Async Report Generator",
    description="Сервис асинхронной генерации отчетов в Excel и PDF",
    version="0.1.0",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(templates_router)
api_router.include_router(reports_router)

app.include_router(api_router)
app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

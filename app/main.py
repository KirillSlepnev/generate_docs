from fastapi import APIRouter, FastAPI

from app.infrastructure.logging.logging import setup_logging
from app.presentation.middleware.logging import LoggingMiddleware
from app.presentation.routers.templates import router as templates_router
from app.presentation.routers.reports import router as reports_router

app = FastAPI(
    title="Async Report Generator",
    description="Сервис асинхронной генерации отчетов в Excel и PDF",
    version="0.1.0",
)

setup_logging()

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(templates_router)
api_router.include_router(reports_router)

app.include_router(api_router)
app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi import APIRouter, FastAPI

from app.presentation.routers.templates import router as templates_router
from app.presentation.routers.reports import router as reports_router

app = FastAPI(
    title="Async Report Generator",
    description="Сервис асинхронной генерации отчетов в Excel и PDF",
    version="0.1.0",
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(templates_router)
api_router.include_router(reports_router)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

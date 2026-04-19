from uuid import UUID

from celery import Celery

from app.config import settings
from app.domain.repositories.message_bus import IMessageBus

celery_app = Celery(
    "reports",
    backend=settings.celery_result_backend,
    broker=settings.celery_broker_url,
    include=["app.infrastructure.celery_tasks.worker"],
)


class CeleryBus(IMessageBus):
    async def publish_generate_report_task(self, report_id: UUID):
        celery_app.send_task(
            "app.infrastructure.celery_tasks.worker.generate_report",
            args=[str(report_id)],
        )

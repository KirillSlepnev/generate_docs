from asyncio import current_task
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
    async_sessionmaker,
)
from app.application.services.report_service import ReportService
from app.application.services.template_service import TemplateService
from app.config import settings
from app.domain.models.value_objects import OutputFormat
from app.domain.repositories.data_source import IDataSource
from app.domain.repositories.file_storage import IFileStorage
from app.domain.repositories.message_bus import IMessageBus
from app.domain.repositories.report import IReportRepository
from app.domain.repositories.report_template import ITemplateRepository
from app.infrastructure.celery_tasks.celery_bus import CeleryBus
from app.infrastructure.data_source.sql_data_source import SQLDataSource
from app.infrastructure.database.repositories.report_repository import (
    SQLAlchemyReportRepository,
)
from app.infrastructure.database.repositories.template_repository import (
    SQLAlchemyTemplateRepository,
)
from app.infrastructure.generators.excel_generator import ExcelGenerator
from app.infrastructure.generators.pdf_generator import PDFGenerator
from app.infrastructure.storage.s3_storage import MinioStorage


engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@asynccontextmanager
async def scoped_session() -> AsyncGenerator[AsyncSession, None]:
    """Специальная сессия для Celery (потокобезопасная)"""
    scoped_factory = async_scoped_session(async_session_maker, scopefunc=current_task)
    try:
        async with scoped_factory() as session:
            yield session
    finally:
        await scoped_factory.remove()


async def get_template_repository_impl(
    session: AsyncSession = Depends(get_session),
) -> ITemplateRepository:
    return SQLAlchemyTemplateRepository(session)


async def get_report_repository_impl(
    session: AsyncSession = Depends(get_session),
) -> IReportRepository:
    return SQLAlchemyReportRepository(session)


async def get_message_bus_impl() -> IMessageBus:
    return CeleryBus()


async def get_file_storage_impl() -> IFileStorage:
    return MinioStorage()


async def get_data_source_impl(
    session: AsyncSession = Depends(get_session),
) -> IDataSource:
    return SQLDataSource(session)


async def get_template_service_impl(
    repo: ITemplateRepository = Depends(get_template_repository_impl),
) -> TemplateService:
    return TemplateService(repo)


async def get_report_service_impl(
    template_repo: ITemplateRepository = Depends(get_template_repository_impl),
    report_repo: IReportRepository = Depends(get_report_repository_impl),
    message_bus: IMessageBus = Depends(get_message_bus_impl),
    file_storage: IFileStorage = Depends(get_file_storage_impl),
    data_source: IDataSource = Depends(get_data_source_impl),
) -> ReportService:
    generators = {
        OutputFormat.EXCEL: ExcelGenerator(),
        OutputFormat.PDF: PDFGenerator(),
    }

    return ReportService(
        template_repo=template_repo,
        report_repo=report_repo,
        message_bus=message_bus,
        file_storage=file_storage,
        data_source=data_source,
        generators=generators,
    )

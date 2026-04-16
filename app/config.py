from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "reports"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/reports"

    redis_url: str = "redis://redis:6379/0"

    rabbitmq_default_user: str = "guest"
    rabbitmq_default_pass: str = "guest"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"

    celery_broker_url: str = "amqp://guest:guest@rabbitmq:5672//"
    celery_result_backend: str = "redis://redis:6379/1"

    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "reports"
    minio_secure: bool = False

    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

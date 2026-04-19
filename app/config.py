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

    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "reports"
    s3_region: str = "us-east-1"
    s3_public_endpoint_url: str = "http://localhost:9000"
    s3_secure: bool = False

    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

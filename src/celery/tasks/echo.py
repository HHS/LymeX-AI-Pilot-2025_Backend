from src.celery.worker import celery
from loguru import logger
from src.celery.tasks.base import BaseTask


@celery.task(
    base=BaseTask,
    name="src.celery.tasks.echo",
)
def echo_task(message: str) -> None:
    logger.info(f"Echoing message: {message}")

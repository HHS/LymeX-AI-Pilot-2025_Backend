import asyncio
from celery import Celery
from src.infrastructure.database import init_db
from src.environment import environment
from loguru import logger
from celery.signals import worker_process_init


@worker_process_init.connect
def beanie_worker_init(**kwargs):
    logger.info("Initializing Beanie for Celery worker")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())


celery = Celery(
    "worker",
    broker=environment.rabbitmq_url,
    backend=environment.mongo_celery_backend,
    include=["src.celery.tasks.echo", "src.celery.tasks.send_email"],
)

celery.conf.task_routes = {
    "src.celery.tasks.send_email": {"queue": "celery.send_email"},
    "src.celery.tasks.*": {"queue": "celery.default"},
}
celery.conf.task_acks_late = True

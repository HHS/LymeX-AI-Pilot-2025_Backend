import asyncio

from loguru import logger

from celery import Celery
from celery.signals import worker_process_init
from src.environment import environment
from src.infrastructure.database import init_db


@worker_process_init.connect
def beanie_worker_init(**kwargs):
    logger.info("Initializing Beanie for Celery worker")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.info("Starting Beanie database connection")
    loop.run_until_complete(init_db())
    logger.info("Beanie database connection started")


celery_queues = [
    "src.celery.tasks.echo",
    "src.celery.tasks.send_email",
    "src.celery.tasks.analyze_competitive_analysis",
    "src.celery.tasks.analyze_product_profile",
    "src.celery.tasks.analyze_claim_builder",
    "src.celery.tasks.analyze_performance_testing",
    "src.celery.tasks.analyze_test_comparison",
    "src.celery.tasks.analyze_clinical_trial",
    "src.celery.tasks.analyze_regulatory_pathway",
    "src.celery.tasks.analyze_regulatory_background",
    "src.celery.tasks.analyze_milestone_planning",
    "src.celery.tasks.analyze_checklist",
    "src.celery.tasks.index_system_data",
]

celery = Celery(
    "worker",
    broker=environment.rabbitmq_url,
    backend=environment.mongo_celery_backend,
    include=celery_queues,
)

celery.conf.task_routes = {
    "src.celery.tasks.send_email": {"queue": "celery.send_email"},
    "src.celery.tasks.analyze_competitive_analysis": {
        "queue": "celery.analyze_competitive_analysis"
    },
    "src.celery.tasks.analyze_product_profile": {
        "queue": "celery.analyze_product_profile"
    },
    "src.celery.tasks.analyze_claim_builder": {"queue": "celery.analyze_claim_builder"},
    "src.celery.tasks.analyze_performance_testing": {
        "queue": "celery.analyze_performance_testing"
    },
    "src.celery.tasks.analyze_test_comparison": {
        "queue": "celery.analyze_test_comparison"
    },
    "src.celery.tasks.analyze_clinical_trial": {
        "queue": "celery.analyze_clinical_trial"
    },
    "src.celery.tasks.analyze_regulatory_pathway": {
        "queue": "celery.analyze_regulatory_pathway"
    },
    "src.celery.tasks.analyze_regulatory_background": {
        "queue": "celery.analyze_regulatory_background"
    },
    "src.celery.tasks.analyze_milestone_planning": {
        "queue": "celery.analyze_milestone_planning"
    },
    "src.celery.tasks.analyze_checklist": {
        "queue": "celery.analyze_checklist"
    },
    "src.celery.tasks.index_system_data": {"queue": "celery.index_system_data"},
    "src.celery.tasks.*": {"queue": "celery.default"},
}
celery.conf.task_acks_late = True

from celery import Task
from loguru import logger

class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

from src.celery.worker import celery
import os

number_of_workers = os.getenv("CELERY_WORKERS", 2)


def start_celery_worker() -> None:
    # Start the Celery worker
    celery.worker_main(
        [
            "worker",
            "-Q celery.default,celery.send_email",
            f"-c {number_of_workers}",
        ]
    )


if __name__ == "__main__":
    start_celery_worker()

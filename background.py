from src.celery.worker import celery


def start_celery_worker() -> None:
    # Start the Celery worker
    celery.worker_main(
        [
            "worker",
            "-Q celery.default,celery.send_email",
            "-c 8",
        ]
    )


if __name__ == "__main__":
    start_celery_worker()

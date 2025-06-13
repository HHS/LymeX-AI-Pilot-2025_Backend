from src.celery.worker import celery
import os

number_of_workers = os.getenv("CELERY_WORKERS", 2)


def start_celery_worker() -> None:
    # Start the Celery worker
    queues = [
        "celery.default",
        "celery.send_email",
        "celery.analyze_competitive_analysis",
        "celery.analyze_product_profile",
        "celery.analyze_claim_builder",
        "celery.analyze_performance_testing",
        "celery.performance_testing",
        "celery.analyze_test_comparison",
        "celery.analyze_clinical_trial",
        "celery.analyze_regulatory_pathway",
        "celery.analyze_milestone_planning",
    ]
    queues = ",".join(queues)
    celery.worker_main(
        [
            "worker",
            f"-Q {queues}",
            f"-c {number_of_workers}",
        ]
    )


if __name__ == "__main__":
    start_celery_worker()

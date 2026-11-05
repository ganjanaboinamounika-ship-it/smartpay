from app.workers.celery_app import celery_app


@celery_app.task(name="smartpay.test_task")
def test_task(name: str):
    message = f"Hello {name}! Celery is working with SMARTPAY."

    print(message)

    return {
        "status": "SUCCESS",
        "message": message,
    }
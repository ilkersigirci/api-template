from worker.runner import build_worker
from worker.tasks.ml_inference import ml_inference_task
from worker.tasks.ml_training import train_model_task


def main() -> None:
    worker = build_worker(
        workflows=[
            ml_inference_task,
            train_model_task,
        ]
    )
    worker.start()


if __name__ == "__main__":
    main()

from worker.runner import build_worker
from worker.tasks.complex_task import long_running_process
from worker.tasks.failing_task import failing_process
from worker.tasks.pydantic_parse_task import pydantic_parse_check


def main() -> None:
    worker = build_worker(
        workflows=[
            long_running_process,
            failing_process,
            pydantic_parse_check,
        ]
    )
    worker.start()


if __name__ == "__main__":
    main()

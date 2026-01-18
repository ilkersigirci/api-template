# api-template

FastAPI Template with Industry Standard Observability

## Logfire

- [Logfire](https://github.com/pydantic/logfire) is Uncomplicated Observability for Python by Pydantic Team.

- Create a new project in [Logfire](https://logfire-us.pydantic.dev) with name `api-template`

- Setup logfire in your project

```bash
# Authenticate with Logfire, one time operation
logfire auth

# Initialize your local project to use Logfire
logfire projects use api-template
```

- Set in your `.env` file: `OLTP_LOG_METHOD=logfire`

## Taskiq

- [Taskiq](https://github.com/taskiq-python/taskiq) is distributed task queue with full async support.
- Like celery but better with async support and more broker support like Redis, RabbitMQ, Kafka, etc.

- The official docs recommend [taskiq-aio-pika](https://pypi.org/project/taskiq-aio-pika/) as the broker and [taskiq-redis](https://pypi.org/project/taskiq-redis/) as the result backend for production use.

- Test taskiq with RabbitMQ and Redis

```bash
# Run Redis and RabbitMQ in docker
make run-taskiq-services

# Run the taskiq workers
make run-taskiq-workers

# Test the taskiq workers
make run-taskiq-main

# (Optional) Run taskiq scheduler for periodic tasks
make run-taskiq-scheduler
```

### Taskiq Dashboard

Task statuses

Let's assume we have a task do_smth, there are all states it can embrace:

- **queued** - the task has been sent to the queue without an error;
- **running** - the task is grabbed by a worker and is being processed;
- **success** - the task is fully processed without any errors;
- **failure** - an error occurred during the task processing;
- **abandoned** - taskiq dashboard was shut down while the task was still in queued or running state, so it probably missed an event on task success/failure.

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```

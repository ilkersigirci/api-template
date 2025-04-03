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

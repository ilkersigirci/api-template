# fastapi-template

FastAPI Template with Industry Standard Observability

## Logfire

- [Logfire](https://github.com/pydantic/logfire) is Uncomplicated Observability for Python by Pydantic Team.
- Create a new project in [Logfire](https://logfire-us.pydantic.dev) with name `api-template`

```bash
logfire auth
logfire projects use api-template
```

Set in `.env`: `OLTP_LOG_METHOD=logfire`

## Hatchet

Background workflows are powered by [Hatchet](https://hatchet.run).

Required env:
- `HATCHET_CLIENT_TOKEN`

Run workers:

```bash
# General worker
cd api-workers-general && make run-worker

# ML worker
cd api-workers-ml && make run-worker
```

## Migrations

```bash
alembic upgrade "<revision_id>"
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

## Example API Requests

General workflow request:

```bash
TASK_ID=$(curl -X POST http://localhost:8000/api/v1/tasks/general/long-running \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}' \
  -s | jq -r '.metadata.id')

curl -X GET http://localhost:8000/api/v1/tasks/general/$TASK_ID
```

ML requests:

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ml/inference \
  -H "Content-Type: application/json" \
  -d '{"model_id": "test-model", "input_data": {"features": [1, 2, 3]}}'

curl -X POST http://localhost:8000/api/v1/tasks/ml/training \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "dataset-123", "model_configuration": {"input_size": 10, "output_size": 1}, "hyperparameters": {"epochs": 5, "learning_rate": 0.01, "batch_size": 32}}'
```

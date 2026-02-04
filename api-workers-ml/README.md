# API Workers ML

This package contains the machine learning task workers for the API template project.

## Overview

The ML workers run independently from regular workers and process ML-specific tasks from a dedicated RabbitMQ queue (`taskiq_ml`). They use the `ml_broker` from `api-shared` to listen to and process machine learning tasks.

## Architecture

- **Queue**: `taskiq_ml` (configurable via `TASKIQ_ML_QUEUE`)
- **Routing Key**: `taskiq_ml` (configurable via `TASKIQ_ML_ROUTING_KEY`)
- **Exchange**: `taskiq` (configurable via `TASKIQ_ML_EXCHANGE`)
- **Broker**: Uses `ml_broker` from `api_shared.broker`

## Development

### Prerequisites

- Python 3.11+
- uv package manager
- RabbitMQ server running
- Redis server running

### Running Locally

```bash
# From the api-workers-ml directory
uv run --module taskiq worker worker.broker:broker \
  --use-process-pool \
  --workers 3 \
  -fsd \
  -tp src/worker/tasks/*.py
```

### Configuration

Environment variables for ML workers:

```bash
# Worker configuration
ML_WORKER_COUNT=3

# Queue configuration
TASKIQ_ML_QUEUE=taskiq_ml
TASKIQ_ML_ROUTING_KEY=taskiq_ml
TASKIQ_ML_EXCHANGE=taskiq

# RabbitMQ connection (shared with regular workers)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

## Task Organization

All ML tasks should be defined in `src/worker/tasks/` directory and decorated with the broker:

```python
from worker.broker import broker

@broker.task(task_name="ml_inference")
async def ml_inference_task(model_id: str, input_data: dict) -> dict:
    """Process ML inference."""
    # Your ML task logic here
    return predictions
```

### Example Tasks

The following example tasks are provided:

- `ml_inference_task`: Perform ML inference on input data
- `train_model_task`: Train an ML model with given configuration

## Docker

### Building

```bash
# From the project root
docker build -t api-template-worker-ml:latest \
  --build-context api-shared=./api-shared \
  -f api-workers-ml/Dockerfile \
  api-workers-ml
```

### Running

```bash
# Using docker-compose
docker-compose up -d api-template-worker-ml

# Or standalone
docker run -d \
  --name api-template-worker-ml \
  --env-file .env \
  api-template-worker-ml:latest
```

## Task Types

### Inference Tasks

For real-time or batch ML inference:

```python
@broker.task(task_name="ml_inference")
async def ml_inference_task(model_id: str, input_data: dict) -> dict:
    # Load model
    # Perform inference
    # Return predictions
    pass
```

### Training Tasks

For model training workflows:

```python
@broker.task(task_name="train_model")
async def train_model_task(
    dataset_id: str,
    model_config: dict,
    hyperparameters: dict,
) -> dict:
    # Load dataset
    # Train model
    # Save model
    # Return metrics
    pass
```

## Best Practices

1. **Resource Management**: ML tasks typically require more memory and CPU
2. **Timeouts**: Set appropriate timeouts for training tasks (can be hours)
3. **Checkpointing**: Implement checkpointing for long-running training tasks
4. **Model Caching**: Cache loaded models to avoid repeated loading
5. **GPU Support**: Configure CUDA/GPU support if needed
6. **Monitoring**: Track model inference latency and training progress

## Testing

```bash
# Run tests
uv run pytest tests/

# With coverage
uv run pytest --cov=worker tests/
```

## Monitoring

- **RabbitMQ Management UI**: http://localhost:15672
  - Check queue depth for `taskiq_ml`
  - Monitor consumer count
  - View message rates

- **Taskiq Dashboard**: Configured via `TASKIQ_DASHBOARD_URL`
  - View task execution history
  - Monitor task success/failure rates
  - Track execution times

## Troubleshooting

### Tasks not being picked up

1. Verify workers are running: `docker-compose ps api-template-worker-ml`
2. Check RabbitMQ queue bindings in Management UI
3. Verify routing key configuration matches

### High memory usage

1. Reduce `ML_WORKER_COUNT`
2. Implement model unloading after inference
3. Use smaller batch sizes
4. Enable model quantization

### Slow inference

1. Enable model caching
2. Use GPU if available
3. Optimize batch processing
4. Consider using ONNX runtime

## Dependencies

ML-specific dependencies should be added to `pyproject.toml`:

```toml
[project.dependencies]
# Add ML libraries as needed:
# torch = "^2.0.0"
# transformers = "^4.30.0"
# scikit-learn = "^1.3.0"
# numpy = "^1.24.0"
```

## See Also

- [Multiple Brokers Documentation](../docs/multiple_brokers.md)
- [Project Structure](../docs/project_structure.md)
- [Taskiq Documentation](https://taskiq-python.github.io/)

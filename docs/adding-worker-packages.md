# Adding New Worker Packages

This guide explains how to add new worker packages to the project. The architecture supports multiple worker types, each with its own broker and queue configuration.

## Architecture Overview

- **Primary Broker**: `general` - Handles regular worker tasks
- **Optional Brokers**: `ml`, etc. - Can be enabled/disabled in brokers.yml

## Adding a New Worker Package

### 1. Add Broker Configuration to brokers.yml

Edit `brokers.yml` and add your new broker configuration:

```yaml
brokers:
  # Existing brokers...
  general:
    queue: taskiq_general
    routing_key: "#"
    exchange: taskiq_general_exchange
    description: "General purpose worker tasks"

  # Your new broker
  custom:
    queue: taskiq_custom
    routing_key: "#"
    exchange: taskiq_custom_exchange
    description: "Custom specialized tasks"
```

### 2. Create Worker Package Directory

Create a new directory following the pattern:

```
api-workers-custom/
├── Dockerfile
├── Makefile
├── pyproject.toml
├── README.md
├── src/
│   └── worker/
│       ├── __init__.py
│       ├── broker.py
│       ├── main.py
│       ├── core/
│       │   └── telemetry.py
│       └── tasks/
│           └── your_tasks.py
└── tests/
    └── __init__.py
```

### 3. Configure Worker Broker

In `api-workers-custom/src/worker/broker.py`:

```python
"""
Custom Worker-specific broker initialization.

This module ensures that OpenTelemetry is set up before the broker is initialized.
"""

from worker.core.telemetry import setup_opentelemetry_worker

# Setup telemetry before importing broker
setup_opentelemetry_worker()

from api_shared.broker import get_broker  # noqa: E402

# Get the custom-specific broker
broker = get_broker("custom")

if broker is None:
    raise RuntimeError(
        "Custom broker is not enabled. Enable it in brokers.yml."
    )

__all__ = ["broker"]
```

### 4. Access the Broker in Your Code

#### In API code (to kick tasks):

```python
from api_shared.broker import get_broker

custom_broker = get_broker("custom")
if custom_broker:
    # Kick a task
    await your_task.kiq()
```

#### In worker tasks:

```python
from worker.broker import broker

@broker.task
async def your_custom_task():
    # Your task logic
    pass
```

## Benefits of This Architecture

1. **Easy Expansion**: Add new workers by following a simple pattern
2. **Centralized Configuration**: All broker settings in one YAML file
3. **No Code Changes**: The core system automatically handles new brokers
4. **Simple Enabling**: Just define a broker in YAML to enable it

## Running Workers

Each worker package can be run independently:

```bash
# Run primary workers
cd api-workers-general && taskiq worker worker.broker:broker

# Run ML workers (if enabled)
cd api-workers-ml && taskiq worker worker.broker:broker

# Run your custom workers (if enabled)
cd api-workers-custom && taskiq worker worker.broker:broker
```

## Testing

When `ENVIRONMENT=test`, all configured brokers use in-memory backends automatically, making testing straightforward without needing actual RabbitMQ/Redis connections.

# API Workers ML

ML background workers are powered by Hatchet and process ML-specific workflows.

## Run locally

```bash
uv run --module worker.main
```

## Required environment

- `HATCHET_CLIENT_TOKEN`
- `HATCHET_WORKER_NAME` (optional, defaults to `ml-worker`)
- `HATCHET_WORKER_SLOTS` (optional, defaults to `100`)

## Workflows

- `ml_inference`
- `train_model`

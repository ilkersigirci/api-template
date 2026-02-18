# API Workers General

General background workers are powered by Hatchet.

## Run locally

```bash
uv run --module worker.main
```

## Required environment

- `HATCHET_CLIENT_TOKEN`
- `HATCHET_WORKER_NAME` (optional, defaults to `general-worker`)
- `HATCHET_WORKER_SLOTS` (optional, defaults to `100`)

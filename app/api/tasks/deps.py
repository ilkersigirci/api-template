from app.external.runner import ExternalRunner, get_external_runner


def get_runner() -> ExternalRunner:
    return get_external_runner()

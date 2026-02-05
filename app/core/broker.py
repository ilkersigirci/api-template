import taskiq_fastapi
from api_shared.broker import broker_manager

for _, broker_instance in broker_manager.get_all_brokers().items():
    taskiq_fastapi.init(broker_instance, "app.api.application:get_app")

__all__ = ["broker_manager"]

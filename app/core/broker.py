import taskiq_fastapi
from api_shared.broker import broker, ml_broker

taskiq_fastapi.init(broker, "app.api.application:get_app")
taskiq_fastapi.init(ml_broker, "app.api.application:get_app")

import taskiq_fastapi
from api_shared.broker import broker

taskiq_fastapi.init(broker, "app.api.application:get_app")

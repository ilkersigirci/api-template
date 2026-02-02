## https://github.com/mosquito/aio-pika/blob/master/aio_pika/abc.py
### Available AMQP Exchange Types
```python
class ExchangeType(str, Enum):
    FANOUT = "fanout" # Ignore routing keys completely
    DIRECT = "direct" # Routing key must EXACTLY match the binding key
    TOPIC = "topic"   # Pattern matching with wildcards (binding routing_key of AioPikaBroker)
    HEADERS = "headers"
    X_DELAYED_MESSAGE = "x-delayed-message"
    X_CONSISTENT_HASH = "x-consistent-hash"
    X_MODULUS_HASH = "x-modulus-hash"
```

## https://github.com/taskiq-python/taskiq-aio-pika/blob/master/taskiq_aio_pika/broker.py
### Binding `routing_key` comes from `AioPikaBroker` definition
``` python
self._routing_key = routing_key
```
### Queue binds to `exchange_name` with a binding `routing_key`
```python
await queue.bind(
    exchange=self._exchange_name,
    routing_key=self._routing_key,
)
```
### Message `routing_key` comes from `message.task_name`
```python
routing_key = message.task_name
# Because direct exchange uses exact routing key for routing
if self._exchange_type == ExchangeType.DIRECT:
    routing_key = self._routing_key
```
### Workers listen to queues with `self._queue_name`
```python
async def listen(self) -> AsyncGenerator[AckableMessage, None]:
    queue = await self.declare_queues(self.read_channel)  # Gets queue by self._queue_name
    async with queue.iterator() as iterator:
        async for message in iterator:  # Iterates ALL messages from this queue
            yield AckableMessage(data=message.body, ack=message.ack)
```
Workers receive all messages from the queue (that comes from the `AioPikaBroker` definition), regardless of which exchange they came from.

## https://github.com/taskiq-python/taskiq/blob/master/taskiq/abc/broker.py
### `message.task_name` comes from `@broker.task(task_name="")`
```python
def task(  # type: ignore[misc]
        self,
        task_name: str | None = None,
        **labels: Any,
    ) -> Any:
        """
        Decorator that turns function into a task.
        This decorator converts function to
        a `TaskiqDecoratedTask` object.
        This object can be called as a usual function,
        because it uses decorated function in it's __call__
        method.
        !! You have to use it with parentheses in order to
        get autocompletion. Like this:
        >>> @task()
        >>> def my_func():
        >>>     ...
        :param task_name: custom name of a task, defaults to decorated function's name.
        :param labels: some addition labels for task.

        :returns: decorator function or AsyncTaskiqDecoratedTask.
        """
```

## http://docs.celeryq.dev/en/latest/userguide/routing.html#exchanges-queues-and-routing-keys
The client sending messages is typically called a publisher, or a producer, while the entity receiving messages is called a consumer. \
The broker is the message server, routing messages from producers to consumers. \
Messages are sent to exchanges. \
An exchange routes messages to one or more queues. \
The message waits in the queue until someone consumes it. \
The message is deleted from the queue when it has been acknowledged. \
The steps required to send and receive messages are:
1) Create an exchange
2) Create a queue
3) Bind the queue to the exchange. (with a binding routing_key)

## Summary Table
| Component                 | Who Defines It                | When Set        | Purpose                                                              |
|---------------------------|-------------------------------|-----------------|----------------------------------------------------------------------|
| **exchange_name**         | Broker constructor            | Broker creation | Which exchange to publish to / consume from                          |
| **queue_name**            | Broker constructor            | Broker creation | Which queue to create / consume from                                 |
| **routing_key** (binding) | Broker constructor            | `startup()`     | Pattern to bind queue to exchange                                    |
| **routing_key** (message) | Func name / `task_name` param | Task kicks      | How to route this specific message (with its broker's exchange_name) |





https://github.com/taskiq-python/taskiq/issues/181 \
uv run --module taskiq worker app.worker.broker:broker --use-process-pool --workers 4 -fsd -tp [app/worker/tasks/*.py]

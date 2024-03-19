import pika
from fastapi import FastAPI
from pika.exchange_type import ExchangeType
from starlette.requests import Request
from json import dumps

# amqp://admin:admin@0.0.0.0:5672/
# parameters = pika.URLParameters(url="amqp://admin:admin@0.0.0.0:5672/")

parameters = pika.ConnectionParameters(
    host="0.0.0.0",
    port=5672,
    virtual_host="/",
    credentials=pika.PlainCredentials(
        username="admin",
        password="admin"
    )
)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
queue = "log"
channel.queue_declare(queue=queue, durable=True)


async def lifespan(app):
    yield
    connection.close()

app = FastAPI()


@app.get(path="/")
async def index(request: Request):
    channel.basic_publish(
        exchange=ExchangeType.fanout,
        routing_key=queue,
        properties=pika.BasicProperties(
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=pika.DeliveryMode.Persistent
        ),
        body=dumps({"path": request.base_url.path, "method": request.method}).encode(),
    )
    return "OK"


if __name__ == '__main__':
    from uvicorn import run
    run(app)

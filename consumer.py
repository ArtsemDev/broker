from json import loads

import pika
from pika.adapters.blocking_connection import BlockingChannel


def callback(ch: BlockingChannel, method, properties: pika.BasicProperties, body):
    if properties.content_type == "application/json":
        data = loads(body)
        print(data)
    else:
        print(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


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
channel.basic_consume(queue=queue, on_message_callback=callback)

channel.start_consuming()

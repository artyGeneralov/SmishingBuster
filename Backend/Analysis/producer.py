import pika
import time
from .analyzer import analyze

def myAnswer(data):
    analysis_results = analyze(data)
    return analysis_results

def on_request(ch, method, properties, body):
    print(f"Received request: {body.decode()}")
    response = myAnswer(body.decode())
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=str(response).encode('utf-8')
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Sent response: {response}")

connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

queue_name = 'message_analysis_queue'
channel.queue_declare(queue=queue_name)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=on_request)
print("Awaiting RPC requests")
channel.start_consuming()

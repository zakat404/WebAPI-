import pika
import logging
from utils import retry

logging.basicConfig(level=logging.INFO)

def callback(ch, method, properties, body):
    message = body.decode()
    logging.info(f"Received message: {message}")

@retry(times=5, delay=5, exceptions=(pika.exceptions.AMQPConnectionError,))
def establish_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='broker'))
    return connection

def main():
    connection = establish_connection()
    channel = connection.channel()

    channel.queue_declare(queue='image_queue')

    channel.basic_consume(queue='image_queue', on_message_callback=callback, auto_ack=True)

    logging.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()

import pika
import logging
import json
import uuid
import time

from datetime import datetime
from opensearchpy import OpenSearch
from pika.exceptions import AMQPConnectionError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# RabbitMQ connection parameters
rabbitmq_params = pika.ConnectionParameters(
    'rabbitmq',
    credentials=pika.PlainCredentials('user', 'password')
)

# OpenSearch connection setup
opensearch_client = OpenSearch(
    hosts=[{'host': 'opensearch-node', 'port': 9200}],
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False
)

def connect_rabbitmq(params, max_retries=5):
    """ Attempt to connect to RabbitMQ server with exponential backoff """
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(params)
            logging.info("Successfully connected to RabbitMQ")
            return connection
        except AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {str(e)}")
            time.sleep(retry_delay)
            retry_delay *= 2
    logging.error("Max retries reached, exiting...")
    return None

def reformat_message(original_message, session_id):
    """ Reformat the message according to opensearch specs """
    return {
        "timestamp": datetime.now().isoformat(),
        "sourcetype": "nginx",
        "index": "nginx",
        "fields": {
            "region": "us-east-1",
            "sessionid": session_id
        },
        "event": original_message
    }

def send_to_opensearch(transformed_message):
    """ Send the transformed message to OpenSearch """
    index_name = transformed_message['sourcetype']
    try:
        response = opensearch_client.index(index=index_name, body=transformed_message)
        logging.info(f"Document indexed successfully: {response}")
    except Exception as e:
        logging.error(f"Error indexing document: {str(e)}")

def consume_message(channel, queue_name, session_id):
    """ Set up a consumer on the specified RabbitMQ queue """
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        logging.info(f"Received message: {message}")
        transformed_message = reformat_message(message, session_id)
        send_to_opensearch(transformed_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    logging.info(f"Waiting for messages in queue '{queue_name}'. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except AMQPConnectionError:
        logging.error("Connection dropped, attempting to reconnect...")
        return False
    return True

def main():
    logging.info("Consumer is starting up")
    session_id = uuid.uuid4().hex

    connection = connect_rabbitmq(rabbitmq_params)
    if connection:
        channel = connection.channel()
        if consume_message(channel, 'log_queue', session_id):
            logging.info("Consumer shut down normally")
        else:
            logging.error("Consumer exiting due to dropped connection")
            exit(1)
    else:
        logging.warning("Consumer did not start due to failed connection")
        exit(1)

if __name__ == '__main__':
    main()

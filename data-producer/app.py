import argparse
import json
import logging
import pika
import requests

from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# RabbitMQ connection parameters
rabbitmq_params = pika.ConnectionParameters(
    'rabbitmq',
    credentials=pika.PlainCredentials('user', 'password')
)

def connect_rabbitmq(params):
    """ Attempt to connect to RabbitMQ server """
    try:
        connection = pika.BlockingConnection(params)
        logging.debug("Successfully connected to RabbitMQ")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to RabbitMQ: {str(e)}")
        return None

def fetch_logs(url):
    """ Fetch logs from the given URL """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()  # Split text into lines for individual processing
    else:
        logging.error(f"Failed to fetch logs from {url}")
        return []

def convert_time_to_iso8601(log_event):
    """ Convert time field in log to ISO 8601 format """
    log_dict = json.loads(log_event)
    time_str = log_dict.get('time', '')
    
    dt = datetime.strptime(time_str, '%d/%b/%Y:%H:%M:%S %z')
    log_dict['time'] = dt.isoformat()
    return json.dumps(log_dict)

def send_message(channel, queue_name, message):
    """ Send a message to the specified RabbitMQ queue """
    channel.queue_declare(queue=queue_name, durable=True)
    logging.debug(f"Queue '{queue_name}' declared")
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    logging.debug(f"Published message to queue '{queue_name}': {message}")
    logging.info(f"Sent message: {message}")

def parse_arguments():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-n', '--num', type=int, default=None, help='Number of logs to process')
    return parser.parse_args()

def main():
    args = parse_arguments()
    logging.info("Producer is starting up")
    connection = connect_rabbitmq(rabbitmq_params)
    
    if connection:
        channel = connection.channel()
        try:
            # URL to fetch the nginx logs
            url = "https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_json_logs/nginx_json_logs"
            logs = fetch_logs(url)
            for i, log_event in enumerate(logs):
                if args.num is not None and i >= args.num:
                    break
                formatted_log = convert_time_to_iso8601(log_event)
                send_message(channel, 'log_queue', formatted_log)
        finally:
            logging.debug("Closing RabbitMQ connection")
            connection.close()
            logging.info("Producer shut down")
    else:
        logging.warning("Producer did not start due to failed connection")

if __name__ == '__main__':
    main()

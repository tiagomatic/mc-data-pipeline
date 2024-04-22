#!/bin/bash
echo "Producing messages to the data pipeline..."

docker build -f data-producer/Dockerfile -t mc-opensearch-produce-data data-producer/
docker run --network mc-opensearch_app-network -it mc-opensearch-produce-data "$@"

echo "All messages have been produced."

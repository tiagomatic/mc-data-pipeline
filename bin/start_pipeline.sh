#!/bin/bash
echo "Starting the data pipeline..."
docker-compose build --no-cache
docker-compose up -d
echo "Data pipeline started. OpenSearch Dashboards can be found at http://localhost:5601. (This link may take up to a few minutes to become accessible.)"

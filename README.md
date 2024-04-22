# mc-opensearch

This repository provides a Docker Compose setup for running OpenSearch and OpenSearch Dashboards with auxiliary scripts for managing the data pipeline, tailored for development and testing environments.

## Prerequisites

Before you begin, ensure Docker and Docker Compose are installed on your machine:

- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

## Repository Structure

This project includes several components organized as follows:
- `bin/`: Bash scripts for managing the data pipeline.
- `data-consumer/`: Dockerfile and source code for the data consumer service.
- `data-producer/`: Dockerfile and source code for the data producer service.
- `docker-compose.yml`: Docker Compose configuration file.
- `README.md`: Documentation for using this repository.
- `architectural-design.png`: Diagram of the system architecture.
- `design.md`: Detailed design documentation of the project.

## Getting Started

This repo contains helper scripts for managing the data pipeline. Make sure to run the commands below from the repository's root directory:.

### Starting the Pipeline
The following command uses the docker-compose.yaml defined in this repo to stand up the data pipeline:
```bash
./bin/start_pipeline.sh
```

### Check Pipeline Status
The following command checks the `docker ps` status of each other component in the data pipeline: 
```bash
./bin/pipeline_status.sh
```

### Produce Events
The following command will pull all events listed [here](https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_json_logs/nginx_json_logs) and send them as event messages into the data pipeline:
```bash
./bin/produce_events.sh
```

### Monitoring the Pipeline
The following command tails all service logs separated or individual, tailable ones depending on what you define as your arguments:
```bash
./bin/monitor_pipeline.sh
```

### Stopping the Pipeline
The following command stops the pipeline gracefully:
```bash
./bin/stop_pipeline.sh
```

### OpenSearch Dashboards
Once the pipeline is up, OpenSearch Dashboards can be accessed through http://localhost:5601.


## Using docker-compose.yml
This project utilizes Docker Compose to simplify the deployment and management of the data pipeline's services, which include the Data Producer, RabbitMQ (Message Queue), Data Consumer, and OpenSearch (Datastore).

Below, you will find an overview of the `docker-compose.yml` file's main sections.

### Docker Compose File Breakdown
The `docker-compose.yml` file is structured into several key sections:

1. version: Specifies the Docker Compose file version that is being used.
2. services: Defines the containers and their configurations. Each service corresponds to a container that will be deployed:
    - Data Producer: Configured to build from a Dockerfile, possibly setting environment variables and depends on the availability of other services like RabbitMQ.
    - RabbitMQ: Set up as the message queue. It might include volume mappings for persistence and port configurations for accessibility.
    - Data Consumer: Similar setup to the Data Producer, might also depend on RabbitMQ and OpenSearch.
    - OpenSearch: Configured with volume mappings for data persistence and ports for accessing its APIs and interfacing with OpenSearch Dashboards.
3. networks: Defines the networks used by containers. Helps isolate and manage the communication between containers.
4. volumes: Declares bind volumes for containers. This setting is useful for data that needs to persist across container restarts and recreations in a local dev environment. Defining each volume in the sevice without the leading `./` would make them persistent volumes (pvs), which are more suitable for a deployed environment.

### Customizing the Configuration
You can modify the `docker-compose.yml` file to fit specific requirements, such as changing service versions, adjusting volume bindings (from bind volumes to pvs, for example), or adding more environment variables. Be sure to understand each component's role and dependencies when making changes.

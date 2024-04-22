# Data Pipeline Design

This document outlines the design and architecture of a data pipeline developed to process and analyze web log data efficiently. The pipeline utilizes Dockerized components including a custom Python-based producer and consumer, RabbitMQ as a message queue, and OpenSearch as a datastore. This document describes the technical solution, the rationale behind key architectural decisions, and the expected flow of data through the system.

## System Overview

The data pipeline is designed to ingest web log data, process it to extract meaningful information, and store it for analysis and visualization. It consists of the following main components:
- **Data Producer**: A custom Python application that fetches logs, transforms each log event, and pushes each log event to RabbitMQ.
- **Message Queue (RabbitMQ)**: Buffers the logs between the producer and consumer to handle load efficiently and ensure data integrity.
- **Data Consumer**: Another Python application that consumes messages from RabbitMQ, performs any final processing needed, and stores the data in OpenSearch.
- **Datastore (OpenSearch)**: Used to index and make the log data searchable for analysis and visualization purposes.

## Component Design

### Data Producer

The Data Producer is responsible for fetching log data from external sources (e.g., a web server API), transforming this data into a standardized format, and pushing it to RabbitMQ. In the case of the example (a static GitHub file), the producer disaggregates all of the log events and converts each event's `time` field to comply with the ISO format required for datetime indexing in OpenSearch.

The decision to handle time transformation logic in the producer is to surface latency and errors upfront, aligning with API contracts rather than allowing issues to propagate downstream. This approach simplifies debugging and improves data integrity by ensuring that only valid, well-formed data is sent through the pipeline.

**Key Decisions**:
- **Custom Python Application**: Python is chosen for its robust library support and simplicity in handling HTTP requests and JSON data, making it ideal for integration and rapid development of the log processing logic.
- **Transformation at the Source**: Performing data transformation as close to the source as possible minimizes the processing burden on downstream components and improves response times by immediately handling errors or anomalies in data format or content.

### RabbitMQ

RabbitMQ acts as the central messaging layer in the pipeline, decoupling the data production from consumption. This ensures that neither the producer nor the consumer are directly dependent on each other's availability or performance, thus enhancing the system's robustness and scalability.

**Key Decisions**:
- **Use of RabbitMQ**: Chosen for its reliability, high availability, and strong support for complex routing scenarios. RabbitMQ ensures that data is not lost in transit and can handle high throughput, which is crucial for log-processing applications.

### Data Consumer

The Data Consumer retrieves messages from RabbitMQ, applies any necessary final transformations, and stores the data in OpenSearch. The consumer wraps the event with crucial fields of `sourcetype` and `index`, as well as other useful metadata such as region, Opensearch session uuid, and the document's datetime.

This additional business logic handles tasks such as schema enforcement and data normalization, thus ensuring that data is ready for query and analysis in Opensearch.

**Key Decisions**:
- **Custom Python Consumer**: Utilizes Python's flexibility for its business logic alongside the efficiency of libraries such as `pika` for RabbitMQ integration and `opensearch-py` for Opensearch integration. This combination ensures that logic is understandable to other developers, messages are processed reliably, and that log events are stored promptly in OpenSearch.

### Datastore (OpenSearch)

OpenSearch is used for storing, searching, and analyzing the ingested log data. It provides powerful full-text search capabilities and real-time analytics, making it suitable for applications that require quick insights from large volumes of data.

### Storage and Volume Management

For local development:
- **Bind Mounts**: Used to directly mount development directories into containers, allowing for quick iterations and real-time code changes without the need for container rebuilds.

For remote deployment:
- **Persistent Volumes (PVs)**: Utilized to ensure data persistence across container restarts and deployments, providing robustness and stability for higher environments.


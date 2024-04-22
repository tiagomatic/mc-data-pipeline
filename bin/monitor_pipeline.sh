#!/bin/bash

# Function to show help menu
usage() {
    echo "Usage: $0 [OPTIONS] [SERVICE...]"
    echo "  -f, --follow    Tail the logs of a specific service"
    echo "  -n, --num       Number of lines to display from the log (default 50)"
    echo "  -h, --help      Show this help message"
    echo "  SERVICE         Specify the service name to monitor logs"
    echo "                  Required when using --follow, optional otherwise"
}

# Parsing command line options
follow_logs=false
service_name=""
tail_lines=50  # default number of lines to tail

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--follow) follow_logs=true ;;
        -n|--num) 
            if [[ "$2" =~ ^[0-9]+$ ]]; then
                tail_lines=$2
                shift
            else
                echo "Error: '-n' requires a numeric argument."
                usage
                exit 1
            fi
            ;;
        -h|--help) usage; exit ;;
        -*|--*) echo "Unknown option: $1"; usage; exit 1 ;;
        *) if [ -n "$service_name" ]; then
               echo "Error: Multiple services specified. Only one service can be monitored with --follow."
               usage
               exit 1
           fi
           service_name="$1"
           ;;
    esac
    shift
done

# Check if service name is provided with --follow
if [ "$follow_logs" = true ] && [ -z "$service_name" ]; then
    echo "Error: A service name must be specified with --follow."
    usage
    exit 1
fi

# Function to display logs
display_logs() {
    local service=$1
    echo "Showing logs for $service:"
    if [ "$follow_logs" = true ]; then
        docker-compose logs -f $service
    else
        docker-compose logs --tail=$tail_lines $service
    fi
}

# If no service is specified and not following, show logs for all services
if [ -z "$service_name" ] && [ "$follow_logs" = false ]; then
    services=("rabbitmq" "data-consumer" "opensearch-node" "opensearch-dashboards")
    for service in "${services[@]}"; do
        display_logs $service
        echo -e "\nPress any key to continue to next service..."
        read -n 1 -s
    done
else
    display_logs $service_name
fi

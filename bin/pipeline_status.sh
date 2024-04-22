#!/bin/bash

# Function to show help menu
usage() {
    echo "Usage: $0 [SERVICE...]"
    echo "  This script displays the status of specified components in the data pipeline."
    echo "  If no services are specified, the status of all components will be shown."
}

# Parse service names from command line arguments
services=()
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) usage; exit ;;
        -*|--*) echo "Unknown option: $1"; usage; exit 1 ;;
        *) services+=("$1") ;;
    esac
    shift
done

# Function to display the status
display_status() {
    if [ ${#services[@]} -eq 0 ]; then
        echo "Displaying the status of all components in the data pipeline..."
        docker-compose ps
    else
        echo "Displaying the status of selected services..."
        for service in "${services[@]}"; do
            echo "Status of $service:"
            docker-compose ps $service
        done
    fi
}

# Display the status based on the provided arguments
display_status

#!/bin/bash

# Docker Cleanup Script
# This script removes unused Docker containers and images
# Usage: ./docker-cleanup.sh

echo "======================================"
echo "  Docker Cleanup Script"
echo "======================================"

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not installed."
    exit 1
  fi
}

# Function to remove stopped containers
remove_containers() {
  echo -e "\n[1/4] Removing stopped containers..."
  
  CONTAINERS=$(docker ps -a -q -f status=exited -f status=created -f status=dead)
  
  if [ -z "$CONTAINERS" ]; then
    echo "No stopped containers to remove."
  else
    echo "Found stopped containers. Removing..."
    docker rm $CONTAINERS
    echo "Stopped containers removed successfully."
  fi
}

# Function to remove dangling images (unused and untagged)
remove_dangling_images() {
  echo -e "\n[2/4] Removing dangling images (untagged)..."
  
  DANGLING_IMAGES=$(docker images -f "dangling=true" -q)
  
  if [ -z "$DANGLING_IMAGES" ]; then
    echo "No dangling images to remove."
  else
    echo "Found dangling images. Removing..."
    docker rmi $DANGLING_IMAGES
    echo "Dangling images removed successfully."
  fi
}

# Function to remove unused networks
remove_networks() {
  echo -e "\n[3/4] Removing unused networks..."
  docker network prune -f
  echo "Unused networks removed successfully."
}

# Function to remove unused volumes
remove_volumes() {
  echo -e "\n[4/4] Removing unused volumes..."
  docker volume prune -f
  echo "Unused volumes removed successfully."
}

# Main function
main() {
  check_docker
  
  echo -e "\nStarting cleanup process..."
  
  # Get initial disk usage
  INITIAL_SPACE=$(docker system df)
  
  # Remove containers, images, networks, and volumes
  remove_containers
  remove_dangling_images
  remove_networks
  remove_volumes
  
  # Display summary
  echo -e "\n======================================"
  echo "  Cleanup Complete"
  echo "======================================"
  echo -e "\nInitial disk usage:"
  echo "$INITIAL_SPACE"
  echo -e "\nCurrent disk usage:"
  docker system df
  echo -e "\nDocker cleanup completed successfully!"
}

# Execute main function
main

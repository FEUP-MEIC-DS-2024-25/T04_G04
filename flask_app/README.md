# Flask Application Docker Image

This repository contains a Dockerized Flask application. Follow the instructions below to pull the Docker image and run the container with your own API key.

## Prerequisites

- Docker installed on your machine
- A valid API key

## Pull the Docker Image

First, pull the Docker image from Docker Hub:

```sh
docker pull luiscarlos21/optireq:1.0.0
```

## Run the Docker Container

Run the Docker container with your API key as an environment variable. Replace `your_api_key` with your actual API key:
  
```sh
docker run -d -p 5000:5000 -e API_KEY=your_api_key luiscarlos21/optireq:1.0.0
```

## Build and run the Docker container to apply recent code changes

```sh
docker-compose up
```
If doesn't work try adding --build

## Access the Application

Access the Flask application by navigating to http://localhost:5000 in your web browser.

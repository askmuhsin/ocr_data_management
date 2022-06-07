#!/bin/bash
docker build -t ocr_service:latest .
docker run \
    --name ocr_service_container \ 
    -p 8123:8123 ocr_service:latest \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \ 
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY



#!/bin/bash
echo "docker build ... "
# docker build -t ocr_service:latest . ;

echo "docker run ...";
docker run \
    -p 8123:8123 \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --name ocr_service_container ocr_service:latest;

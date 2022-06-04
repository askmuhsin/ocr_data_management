#!/bin/bash
docker build -t ocr_service:latest .
docker run --name ocr_service_container -p 8123:8123 ocr_service:latest

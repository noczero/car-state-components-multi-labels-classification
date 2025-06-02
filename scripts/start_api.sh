#!/bin/bash
cd "$(dirname "$0")/.." || exit

echo "Starting Backend on port 8001..."

uvicorn main:app --host 0.0.0.0 --reload --port 8081
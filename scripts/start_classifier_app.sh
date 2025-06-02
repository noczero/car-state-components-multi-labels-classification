#!/bin/bash

cd "$(dirname "$0")/../www/apps/classifier" || exit

echo "Starting Classifier App on port 8080..."

npm run dev -- --port 8080

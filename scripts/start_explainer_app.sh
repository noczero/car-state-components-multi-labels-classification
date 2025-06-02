#!/bin/bash

cd "$(dirname "$0")/../www/apps/explainer" || exit

echo "Starting Explainer App on port 8082..."

npm run dev -- --port 8082

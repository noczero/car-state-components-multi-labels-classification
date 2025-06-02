#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(dirname "$0")"

echo "Starting all services..."

echo "Launching Backend service..."
"$SCRIPT_DIR/start_api.sh" &
API_PID=$!
echo "Backend PID: $API_PID"

echo "Launching Classifier App service..."
"$SCRIPT_DIR/start_classifier_app.sh" &
CLASSIFIER_APP_PID=$!
echo "Classifier App PID: $CLASSIFIER_APP_PID"

echo "Launching Explainer App service..."
"$SCRIPT_DIR/start_explainer_app.sh" &
EXPLAINER_APP_PID=$!
echo "Explainer App PID: $EXPLAINER_APP_PID"

echo "All services launched."
echo "Backend PID: $API_PID | Classifier App PID: $CLASSIFIER_APP_PID | Explainer App PID: $EXPLAINER_APP_PID"
echo "Press Ctrl+C to stop all services."

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "Stopping services..."

    echo "Stopping Backend (PID $API_PID)..."
    kill $API_PID

    echo "Stopping Classifier App (PID $CLASSIFIER_APP_PID)..."
    pkill -P $CLASSIFIER_APP_PID
    kill $CLASSIFIER_APP_PID

    echo "Stopping Explainer App (PID $EXPLAINER_APP_PID)..."
    pkill -P $EXPLAINER_APP_PID
    kill $EXPLAINER_APP_PID

    echo "Services stop commands issued. Check logs/terminals for confirmation."
    exit 0
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

wait $API_PID
wait $CLASSIFIER_APP_PID
wait $EXPLAINER_APP_PID

echo "All services have naturally terminated or one of them has."
cleanup
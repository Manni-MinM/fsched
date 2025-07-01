#! /bin/bash

cd ../master/
source .venv/bin/activate
make gunicorn-cluster-manager&
make gunicorn-controller&
make gunicorn-scheduler&
make gunicorn-predictor&
deactivate

cd ../worker/
make start-worker PORT=3000&
make start-worker PORT=3100&

cd ../tests/
source .venv/bin/activate
python main.py
deactivate

PORTS=(3000 3100 8000 8100 8200 8300)

for PORT in "${PORTS[@]}"; do
    echo "Checking port $PORT..."

    PIDS=$(lsof -ti :$PORT)


    if [ -n "$PIDS" ]; then
        echo "Processes found on port $PORT: $PIDS"


        echo "$PIDS" | xargs kill -9

        echo "Processes on port $PORT have been killed."
    else
        echo "No processes found on port $PORT."
    fi
done

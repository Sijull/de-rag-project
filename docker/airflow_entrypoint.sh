#!/bin/bash
set -e

# This is the host and port for your Postgres container
DB_HOST="postgres-db"
DB_PORT="5432"

# 1. Wait for the Postgres database to be ready
# We use a simple loop and 'nc' (netcat) to check if the port is open
echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do   
  sleep 0.1
done
echo "Postgres is up!"

# 2. Run the Airflow database initialization (it's safe to run multiple times)
echo "Initializing/upgrading Airflow database..."
airflow db upgrade

# 3. Create the Airflow admin user (safe to run multiple times)
echo "Creating Airflow admin user..."
airflow users create \
    --username "${AIRFLOW__WEBSERVER__USERNAME:-airflow}" \
    --password "${AIRFLOW__WEBSERVER__PASSWORD:-airflow}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true
echo "Admin user created or already exists."

# 4. Hand off to the original Airflow command (e.g., "webserver" or "scheduler")
exec "$@"
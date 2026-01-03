#!/bin/bash
set -e

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-production_control}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"

if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable is not set"
    exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

echo "Waiting for PostgreSQL to be ready..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is ready"

echo "Checking if database '$DB_NAME' exists..."

DB_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" postgres 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo "Database '$DB_NAME' does not exist. Creating..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" postgres
    echo "Database '$DB_NAME' created successfully."
else
    echo "Database '$DB_NAME' already exists."
fi

echo "Running database migrations..."
python -m alembic upgrade head
echo "Database migrations completed successfully"

exec "$@"

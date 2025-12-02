#!/bin/bash
set -e

echo ""
echo "======================================"
echo "Migrating local PostgreSQL → Docker PostgreSQL"
echo "======================================"
echo ""

# ------------------------------
# CONFIG — update if needed
# ------------------------------

LOCAL_DB_NAME="language_bot"
LOCAL_DB_USER="postgres"
LOCAL_DB_HOST="localhost"

DOCKER_CONTAINER="bot_db"
DOCKER_DB_NAME="language_bot"
DOCKER_DB_USER="postgres"

DUMP_FILE="dump.sql"

# ------------------------------
# CREATE LOCAL DUMP (NO OWNERS)
# ------------------------------

echo "Creating local dump..."
pg_dump -U "$LOCAL_DB_USER" \
       -h "$LOCAL_DB_HOST" \
       -d "$LOCAL_DB_NAME" \
       -F c \
       --no-owner \
       --no-privileges \
       -f "$DUMP_FILE"

echo "Local dump created: $DUMP_FILE"
echo ""


# ------------------------------
# COPY DUMP INTO DOCKER
# ------------------------------

echo "Copying dump into Docker container ($DOCKER_CONTAINER)..."
docker cp "$DUMP_FILE" "$DOCKER_CONTAINER":"/$DUMP_FILE"
echo "Dump copied"
echo ""


# ------------------------------
# DROP & RECREATE SCHEMA
# ------------------------------

echo "Dropping schema 'public' inside Docker DB..."
docker exec -it "$DOCKER_CONTAINER" \
  psql -U "$DOCKER_DB_USER" -d "$DOCKER_DB_NAME" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Schema reset"
echo ""


# ------------------------------
# RESTORE DATABASE
# ------------------------------

echo "Restoring dump inside Docker..."
docker exec -it "$DOCKER_CONTAINER" \
  pg_restore -U "$DOCKER_DB_USER" \
             -d "$DOCKER_DB_NAME" \
             --no-owner \
             --no-privileges \
             "/$DUMP_FILE"

echo "Restore completed successfully"
echo ""


# ------------------------------
# TEST RESTORED DB
# ------------------------------

echo "Testing restored database..."
docker exec -it "$DOCKER_CONTAINER" \
  psql -U "$DOCKER_DB_USER" -d "$DOCKER_DB_NAME" -c "\dt"

echo ""
echo "======================================"
echo "Migration COMPLETED SUCCESSFULLY!"
echo "======================================"
echo ""

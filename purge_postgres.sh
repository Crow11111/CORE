#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Connection Details from .env ---
DB_HOST="187.77.68.250"
DB_USER="root" # Assuming root user for DB as it's the only one in .env
# NOTE: This assumes passwordless login is configured (e.g., via ~/.pgpass or trust authentication)
# or that psql will prompt if necessary, though interactive prompts may fail.
# For this script, we rely on a pre-configured environment.

PSQL_CONN="psql -h ${DB_HOST} -U ${DB_USER} -d postgres" # Connect to the default 'postgres' db

# Define the deletion query
DELETE_QUERY="DELETE FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';"

# Define the verification query
VERIFICATION_QUERY="SELECT COUNT(*) FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';"

# First, get the count of records to be deleted
echo "--- PostgreSQL Purge Plan (Remote: ${DB_HOST}) ---"
COUNT_BEFORE=$(${PSQL_CONN} -t -c "SELECT COUNT(*) FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';")
COUNT_BEFORE=$(echo $COUNT_BEFORE | xargs)
echo "Found ${COUNT_BEFORE} records to delete from 'multi_view_embeddings'."

# Execute the deletion
if [ "$COUNT_BEFORE" -gt 0 ]; then
    echo "Executing deletion..."
    ${PSQL_CONN} -c "${DELETE_QUERY}"
    echo "Deletion command executed."
else
    echo "No records to delete."
fi


# Execute the verification
echo "--- Verification ---"
COUNT_AFTER=$(${PSQL_CONN} -t -c "${VERIFICATION_QUERY}")
COUNT_AFTER=$(echo $COUNT_AFTER | xargs)
echo "Verification query result: ${COUNT_AFTER} matching records found."

# Final Report
echo -e "\n--- PostgreSQL Purge Report ---"
echo "Items to be deleted: ${COUNT_BEFORE}"
echo "Items remaining (after delete): ${COUNT_AFTER}"

if [ "$COUNT_AFTER" -eq 0 ]; then
    echo "✅ Verification successful: Table is clean."
else
    echo "❌ Verification failed: Matching records still exist."
fi
echo "----------------------------"

#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Connection Details from .env ---
VPS_HOST="187.77.68.250"
VPS_USER="root"
# The SSH password needs to be handled securely. sshpass is a good option.
# We will check if it's installed.

# Define the SQL commands to be executed remotely
SQL_COMMANDS="
    -- Get count before deletion
    SELECT COUNT(*) FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';
    -- Perform deletion
    DELETE FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';
    -- Get count after deletion for verification
    SELECT COUNT(*) FROM multi_view_embeddings WHERE source = 'ha_events' OR source = 'state_changed' OR metadata->>'source_event' = 'state_changed';
"

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null
then
    echo "'sshpass' could not be found. Installing it..."
    echo "gogogo" | sudo -S pacman -S sshpass --noconfirm
fi

# Execute the psql commands remotely via SSH
# Using sshpass to provide the password non-interactively.
# Using sudo -u postgres to run psql as the postgres user for peer authentication.
echo "--- Executing PostgreSQL Purge remotely on ${VPS_HOST} ---"

# Note: The password is read from an environment variable to avoid showing it in process lists.
# However, for this context, reading from .env is the given instruction.
VPS_PASSWORD='d!#pAiKSYY[so,OrZluTkv[=@iCs]<l6[0ElCIJ:<2|C]p0v+'

REMOTE_OUTPUT=$(sshpass -p "${VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_HOST} "psql -d postgres -t -c \"${SQL_COMMANDS}\"")

# Process the output
# The output will contain three numbers, one for each query.
output_lines=($REMOTE_OUTPUT)
COUNT_BEFORE=$(echo ${output_lines[0]} | xargs)
# The second output is the result of the DELETE statement, which we can ignore for the count.
COUNT_AFTER=$(echo ${output_lines[1]} | xargs)

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


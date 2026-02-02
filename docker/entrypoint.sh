#!/bin/bash

# LinuxServer.io style user/group management
# This script adjusts the UID/GID of the appuser at runtime based on PUID/PGID environment variables

set -e

# Default values
PUID=${PUID:-1000}
PGID=${PGID:-1000}

echo "───────────────────────────────────────"
echo "User/Group Management"
echo "───────────────────────────────────────"

# Get current UID/GID of appuser
CURRENT_UID=$(id -u appuser)
CURRENT_GID=$(id -g appuser)

echo "User UID:    $PUID"
echo "User GID:    $PGID"

# Check if we need to modify the user/group
if [ "$PUID" != "$CURRENT_UID" ] || [ "$PGID" != "$CURRENT_GID" ]; then
    echo "Updating appuser UID:GID from $CURRENT_UID:$CURRENT_GID to $PUID:$PGID"

    # Change group ID if needed
    if [ "$PGID" != "$CURRENT_GID" ]; then
        groupmod -o -g "$PGID" appuser
        echo "✓ Group ID updated to $PGID"
    fi

    # Change user ID if needed
    if [ "$PUID" != "$CURRENT_UID" ]; then
        usermod -o -u "$PUID" appuser
        echo "✓ User ID updated to $PUID"
    fi

    # Fix ownership of application directories
    echo "Updating ownership of application directories..."
    chown -R appuser:appuser /app
    echo "✓ Ownership updated"
else
    echo "User/Group IDs are already correct"
fi

echo "───────────────────────────────────────"
echo ""

# Switch to appuser and execute the command
exec su-exec appuser "$@"

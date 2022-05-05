#!/bin/sh

# Abort on any error (including if wait-for-it fails).
set -e

# Wait for the backend to be up, if we know where it is.
if [ -n "$USER_API" ]; then
  /app/work/wait-for-it.sh "$USER_API:5000"
fi

# Run the main container command.
exec "$@"
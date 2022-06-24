#!/bin/sh

# Abort on any error (including if wait-for-it fails).
set -e

# Wait for the backend to be up, if we know where it is.
if [ -n "$NEO4J_API" ]; then
  /wait-for-it.sh -t 45 "$NEO4J_API"
fi

# Run the main container command.
exec "$@"

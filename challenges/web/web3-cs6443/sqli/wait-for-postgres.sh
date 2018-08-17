#!/bin/bash
# wait-for-postgres.sh

set -e

host="$1"
shift
cmd="$@"

# we sleep to wait for pgsql to start up lol
sleep 5

>&2 echo "Postgres is up - executing command"
exec $cmd

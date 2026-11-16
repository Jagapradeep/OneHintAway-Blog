#!/bin/sh
# Run by the postgres image once, the first time it starts on an empty data volume.
# Gives Umami its own database and its own user, so it cannot read the blog's tables.
# Changing UMAMI_DB_PASSWORD later does nothing here: change it with ALTER ROLE, or
# start again on a fresh volume (docker compose down -v).
set -eu

psql -v ON_ERROR_STOP=1 -v pw="$UMAMI_DB_PASSWORD" \
     --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
CREATE ROLE umami LOGIN PASSWORD :'pw';
CREATE DATABASE umami OWNER umami;
SQL

# One Hint Away API

Spring Boot 4.1 (Java 21) and PostgreSQL 16. What it does and why is in the
[root README](../README.md#-the-api-api); this page is how to run and change it.

## Run it

Needs a JDK (21 or newer) and Docker. Maven comes with the repo (`./mvnw`; `mvnw.cmd` in PowerShell).

```bash
cp .env.example .env            # fill in POSTGRES_PASSWORD, VISITOR_SALT, ADMIN_TOKEN
docker compose up -d --wait     # PostgreSQL 16 on 127.0.0.1:5432, data kept in a Docker volume
./mvnw spring-boot:run          # http://localhost:8080
```

Check it: `curl http://localhost:8080/actuator/health/readiness` answers `{"status":"UP"}`.
Fill the posts table from the site: `npm run sync-posts` in `site/`.
Stop the database with `docker compose stop`; `docker compose down -v` also deletes its data.

## Test it

```bash
./mvnw verify
```

Docker must be running: the tests start their own throwaway PostgreSQL 16 and never touch the
one from `compose.yaml`. The first run downloads the Postgres image.

## Settings

All come from environment variables. Locally they are read from `api/.env`, which is
git-ignored; real environment variables win over the file.

| Variable | For | Default |
| --- | --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | The database, shared with `compose.yaml` | `onehintaway`, `onehintaway`, none, `5432` |
| `DB_URL` | The whole JDBC address, when the database is not on localhost | built from the values above |
| `VISITOR_SALT` | Secret mixed into visitor hashes. **Required**: the API won't start without it | none |
| `ADMIN_TOKEN` | Secret for the posts sync. Blank switches the sync off (it answers 503) | blank |
| `CORS_ORIGINS` | Site addresses allowed to call from a browser, comma-separated | `http://localhost:3000` |
| `PUBLIC_URL` | The API's own public address, used in confirmation links | `http://localhost:8080` |
| `RESEND_API_KEY` | Sends confirmation emails through Resend. Blank writes the link to the log instead | blank |
| `MAIL_FROM` | The sender; its domain must be verified in Resend | `One Hint Away <hello@onehintaway.com>` |
| `FORWARD_HEADERS` | Set to `native` behind a proxy, or every reader shares the proxy's address and counts as one visitor | `none` |
| `MANAGEMENT_SERVER_PORT` | Moves `/actuator` to its own port, to keep metrics off the public address | same port |

Rate limits are `app.rate.*` in `application.properties`.

## Change the database

The schema is defined only by the SQL files in `src/main/resources/db/migration/`. Flyway runs
the ones a database hasn't seen yet, in order, when the API starts.

1. Add a new file, `V2__what_it_does.sql` (next number, two underscores).
2. Never edit a migration that has already run anywhere: Flyway compares checksums and the API
   will refuse to start. Fix a mistake with another migration.
3. Change the entity to match. Hibernate only checks (`ddl-auto=validate`), so a mismatch stops
   the app at start, and `./mvnw verify` catches it first.

## Not done yet

- Confirmation emails go through Resend once `RESEND_API_KEY` is set and `onehintaway.com` is
  verified there (SPF and DKIM records in Cloudflare DNS). The code is tested against a fake
  server only: no real email has been sent yet.
- The weekly newsletter is not part of this API. The plan is Listmonk on the cluster, sending
  through Amazon SES (Phase 6); confirmed subscribers are handed to it then, and it provides
  the unsubscribe link.
- Rate-limit buckets are in memory, so each replica keeps its own count.

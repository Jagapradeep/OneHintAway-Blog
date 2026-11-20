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

## Sign in locally

Accounts need no setup beyond the steps above. With `RESEND_API_KEY` blank, no email is
sent: the code is written to the API's log.

1. Start the site with accounts on, in `site/`: `cp .env.example .env.local` (once), then
   `npm run dev`. `.env.local` sets `NEXT_PUBLIC_API_URL=http://localhost:8080` and
   `NEXT_PUBLIC_ACCOUNTS=on`; restart the dev server after changing it.
2. Press **Sign in** in the header, enter any address, and send.
3. Find the line `Sign-in code for …: 123456` in the API's log (`docker compose logs api`
   when it runs in the compose stack) and type the code in the panel. Each code works once,
   for 15 minutes, and dies after five wrong tries.

The footer's newsletter form works the same way: without `RESEND_API_KEY` the confirmation
link (`Confirmation link for …`) or, for an address already subscribed, the unsubscribe link
(`Already subscribed: unsubscribe link for …`) is written to the log.

The same by hand. Every request that changes something needs the two headers, or it is
refused with 403:

```bash
H='-H Origin:http://localhost:3000 -H X-OHW-CSRF:1 -H Content-Type:application/json'
curl -i $H -d '{"email":"me@example.com"}' http://localhost:8080/api/v1/auth/code        # 202
curl -i $H -c jar -d '{"email":"me@example.com","code":"<code from the log>"}' http://localhost:8080/api/v1/auth/session
curl -b jar http://localhost:8080/api/v1/auth/me
curl -i $H -b jar -X PUT http://localhost:8080/api/v1/progress/kadane                    # 204
```

`CORS_ORIGINS` and `SITE_URL` must be the address the site is served from (the default is
`http://localhost:3000`). The cookie is marked `Secure`; Chrome, Edge and Firefox accept it
from `http://localhost` anyway. For a browser that does not, set `SESSION_COOKIE_SECURE=false`.

## Build and run the image

Needs only Docker. Why the image is built this way is in the
[root README](../README.md#-docker).

```bash
docker build -t onehintaway-api:local .     # from api/; about 1.5 min the first time, 20 s after a code change
docker image ls onehintaway-api             # 272 MB unpacked, 128 MB compressed
docker history onehintaway-api:local        # one line per layer: libraries 60 MB, our classes 53 kB
```

The image holds no settings. The easy way to run it is the whole stack, which also gives it
a database:

```bash
cd ../deploy/compose
cp .env.example .env                        # fill in the blanks
docker compose up -d --wait                 # API on 127.0.0.1:8080, Umami on 127.0.0.1:3001
docker compose logs -f api
```

To run the image alone against the database from `compose.yaml` here:

```bash
docker run --rm -p 127.0.0.1:8080:8080 --env-file .env \
  -e DB_URL=jdbc:postgresql://host.docker.internal:5432/onehintaway onehintaway-api:local
```

Inside a container `localhost` is the container itself, which is why `DB_URL` is needed.
The container runs as user 10001 (not root) and reports `healthy` once
`/actuator/health/readiness` answers. If you move `/actuator` with `MANAGEMENT_SERVER_PORT`,
the image's health check (port 8080) must change with it. The image build skips the tests;
run `./mvnw verify` first.

## Settings

All come from environment variables. Locally they are read from `api/.env`, which is
git-ignored; real environment variables win over the file.

| Variable | For | Default |
| --- | --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | The database, shared with `compose.yaml` | `onehintaway`, `onehintaway`, none, `5432` |
| `DB_URL` | The whole JDBC address, when the database is not on localhost | built from the values above |
| `VISITOR_SALT` | Secret mixed into visitor hashes. **Required**: the API won't start without it | none |
| `ADMIN_TOKEN` | Secret for the posts sync. Blank switches the sync off (it answers 503) | blank |
| `CORS_ORIGINS` | Site addresses allowed to call from a browser, comma-separated. Also the only `Origin` values accepted on account and progress changes (the CSRF check), so list exact origins, never a wildcard | `http://localhost:3000` |
| `PUBLIC_URL` | The API's own public address, used in confirmation links | `http://localhost:8080` |
| `SITE_URL` | The site's address. Opening a confirmation link redirects to `/subscribed/` there (or `/subscribed/expired/` for a bad link); the unsubscribe link opens `/unsubscribe/` there | `http://localhost:3000` |
| `RESEND_API_KEY` | Sends confirmation and sign-in emails through Resend. Blank writes the code or link to the log instead | blank |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret. With it, `POST /api/v1/auth/code` (sign-in) needs a `turnstile` token that Cloudflare confirms, or answers `403`; if Cloudflare can't be reached, `503`. Blank switches the check off | blank |
| `MAIL_FROM` | The sender; its domain must be verified in Resend | `One Hint Away <hello@onehintaway.com>` |
| `SESSION_COOKIE_SECURE` | `true` marks the session cookie HTTPS-only and names it `__Host-ohw_session`. `false` (name `ohw_session`) is only for local runs in a browser that refuses Secure cookies from `http://localhost` | `true` |
| `LINK_PER_HOUR` | Sign-in codes one caller address may ask for in an hour (in memory, per replica; the name dates from links) | `10` |
| `LINK_PER_EMAIL_PER_HOUR` | Sign-in codes one email address is sent in an hour (counted in the database) | `3` |
| `FORWARD_HEADERS` | Set to `native` behind a proxy, or every reader shares the proxy's address and counts as one visitor | `none` |
| `MANAGEMENT_SERVER_PORT` | Moves `/actuator` to its own port, to keep metrics off the public address | same port |

The other rate limits are `app.rate.*` in `application.properties`. Link lifetime (15 minutes), session lifetime (30 days
after the last use) and the "fresh" window for deleting an account (15 minutes) are constants in
`accounts/AccountService.java`.

## Preview the emails

`./mvnw -q test -Dtest=MailPreviewTests` writes every email, exactly as the API would send it, to
`target/mail-preview/` (sign-in code, delete code, confirmation, already subscribed). Open the
files in a browser; the logo is taken from `site/public/` so it shows before a deploy. No email
is sent. The header is one image, 180 px wide on purpose: Gmail's dark mode on Android inverts
any image up to 64 px.

## Change the database

The schema is defined only by the SQL files in `src/main/resources/db/migration/`. Flyway runs
the ones a database hasn't seen yet, in order, when the API starts.

1. Add a new file, `V5__what_it_does.sql` (next number, two underscores). `V2__accounts.sql`
   added `users`, `login_tokens`, `sessions` and `progress`; `V3__sign_in_codes.sql` added the
   wrong-try counter for codes; `V4__csp_reports.sql` added the CSP report counts.
2. Never edit a migration that has already run anywhere: Flyway compares checksums and the API
   will refuse to start. Fix a mistake with another migration.
3. Change the entity to match. Hibernate only checks (`ddl-auto=validate`), so a mismatch stops
   the app at start, and `./mvnw verify` catches it first.

## The API can't log in to the local database

`password authentication failed for user "onehintaway"` means `POSTGRES_PASSWORD` in `api/.env`
is not the password the database was created with. Postgres reads that variable **only once**,
when the volume `api_pgdata` is empty, and stores a one-way hash of it inside the volume. After
that, editing `.env` changes nothing, and the old password can't be read back from anywhere.

- **Keep the data:** set the database to the password now in `.env` (no old password needed:
  connections from inside the container are trusted):
  `docker exec -it api-postgres-1 psql -U onehintaway -d onehintaway -c "ALTER ROLE onehintaway PASSWORD '<value from api/.env>';"`
- **Start fresh:** `docker compose down -v && docker compose up -d --wait` in `api/` (deletes
  every local account, view and subscriber), start the API (Flyway recreates the tables), then
  `npm run sync-posts` in `site/`.

`VISITOR_SALT` and `ADMIN_TOKEN` are never stored in the database, so they can be changed at
any time: restart the API. The compose stack (`deploy/compose/`) has its own volume and its own
`.env`; the same rules apply there.

## Not done yet

- Nothing is sent to the subscriber list yet. Whether to run a newsletter (the plan was
  Listmonk on the cluster, sending through Amazon SES) is decided once there are subscriber
  numbers; subscribing, confirming and unsubscribing already work.
- Rate-limit buckets are in memory, so each replica keeps its own count (the per-email limit on
  sign-in codes is the exception: it is counted in the database).
- Accounts: no Google sign-in yet; a session has no hard end date as long as it is used at
  least once every 30 days; expired codes and sessions are cleared when someone next asks for
  a code, not on a timer.

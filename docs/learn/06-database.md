# 6 · The database

> ⏱ 75 min · 🧰 the database and the API running (chapter 5), Git Bash

## 📖 The story

On 19 November the API wouldn't start on the laptop: `password authentication failed for user
"onehintaway"`. The password in `api/.env` was right there. It was pasted in again. It was compared
with the Docker stack's file: identical. Still refused.

The answer: **Postgres never reads `.env` again after its first start.** On the very first
`docker compose up`, with an empty volume, the image's setup script created the user with
whatever `POSTGRES_PASSWORD` said *that day*, and stored only a one-way hash of it inside the
volume. That `.env` value had since been overwritten, and a hash can't be turned back into a
password. The fix was to reset it (`ALTER ROLE`, or a fresh volume). By the end of this chapter
you'll know exactly where everything in this database lives, and why.

## 💡 The idea in 2 minutes

Three rules run this database:

1. **Flyway owns the schema.** The tables are defined only by the numbered SQL files in
   `db/migration/`. On startup Flyway runs the ones this database hasn't seen, in order, and
   records each in `flyway_schema_history` with a checksum. Hibernate only *checks* that the Java
   entities match (`ddl-auto=validate`); it never changes a table.
2. **Let the database enforce the rules.** "One view per visitor per day" is a primary key.
   "Five wrong tries per code" is a row lock: `SELECT … FOR UPDATE` makes guesses for one address
   wait their turn, so each sees every try counted before it. "A deleted user
   takes their sessions with them" is `ON DELETE CASCADE`. Rules in the schema hold even when
   two requests arrive at the same instant.
3. **Store as little as possible.** No raw IP addresses (a daily hash instead), no sign-in codes
   or session tokens (only their SHA-256), no passwords at all.

## 🗂️ The tables

```text
posts            slug PK · number · title · pattern · section · tags[] · body_text
                 tsv  ← GENERATED ALWAYS AS (weighted to_tsvector of title, pattern, body) STORED
                 GIN index on tsv                         (replaced by every posts sync)

post_views       PK (slug, day, visitor_hash)             one row = one visitor, one post, one day
code_copies      PK (slug, lang, day) · count             a counter, upserted
subscribers      id · email UNIQUE · status · token UNIQUE · created_at · confirmed_at

users            id · email UNIQUE (lowercase) · created_at · last_sign_in_at
login_tokens     token_hash PK · email · purpose · expires_at · used_at · attempts
sessions         token_hash PK · user_id FK → users ON DELETE CASCADE · expires_at
progress         PK (user_id, slug) · user_id FK → users ON DELETE CASCADE · done_at
```

Two deliberate choices about foreign keys:

- **No FK from `post_views`, `code_copies` or `progress` to `posts`.** The sync replaces `posts`
  every time; a foreign key would make that delete everyone's history and progress.
- **FKs with `ON DELETE CASCADE` from `sessions` and `progress` to `users`.** Deleting an account
  is one `DELETE FROM users`, and the database removes the rest. Nothing can be forgotten.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `api/src/main/resources/db/migration/V1__init.sql` | posts with the generated `tsv` and GIN index; the counters; subscribers |
| `V2__accounts.sql` | users, login_tokens, sessions, progress; the comments explain every choice |
| `V3__sign_in_codes.sql` | one `ALTER TABLE`: the wrong-try counter |
| `api/.../stats/StatsController.java` | `ON CONFLICT DO NOTHING` and `ON CONFLICT … DO UPDATE SET count = count + 1` |
| `api/.../posts/SearchController.java` | `websearch_to_tsquery`, `ts_rank`, the `ILIKE` fallback |
| `api/.../accounts/AccountService.java` | `exchange`: `SELECT … FOR UPDATE` locks the address's live codes, then counts the try or spends the code |
| `api/compose.yaml` | the local database: `postgres:16-alpine`, volume `pgdata`, port on 127.0.0.1 only |

## 🛠 Try it (35 min)

A shortcut for the rest of the course (paste it into Git Bash; it uses the container's trusted
local socket, so it needs no password):

```bash
db() { docker exec -i api-postgres-1 psql -U onehintaway -d onehintaway -c "$1"; }
```

**1. Look around.**

```bash
db "\dt"                                     # the tables
db "\d posts"                                # columns, the generated tsv, the GIN index
db "select version, description, success from flyway_schema_history order by installed_rank"
```

**2. Counting without races.**

```bash
db "select * from post_views limit 3"        # no address anywhere, only a hash
db "select * from code_copies limit 3"
```

Read the two statements in `StatsController.java`. The view count is
`INSERT … ON CONFLICT DO NOTHING`: a second view from the same visitor on the same day hits the
primary key and does nothing. The copy count is
`INSERT … ON CONFLICT (slug, lang, day) DO UPDATE SET count = code_copies.count + 1`. Neither
reads first, so two requests at the same moment can't both see "0" and both write "1".

**3. Full-text search.**

```bash
db "select slug, tsv from posts where slug = 'kadane'" | head -5        # words → stems with positions and weights
db "select to_tsvector('english', 'Running sums of the numbers')"       # 'number':5 'run':1 'sum':2
db "select slug, round(ts_rank(tsv, q)::numeric, 3) as rank
    from posts, websearch_to_tsquery('english', 'running sum') q
    where tsv @@ q order by rank desc limit 5"
```

`to_tsvector` turns text into word stems ("running" → "run") and drops words like "the". Title
words get weight A, pattern B, body C, so a match in the title ranks higher. `@@` means
"matches". `websearch_to_tsquery` understands what people type into search boxes:
`"exact phrase"`, `-word`, `or`.

**4. Does the index get used?**

```bash
db "explain select slug from posts where tsv @@ websearch_to_tsquery('english','window')"
```

With 34 rows Postgres reads the whole table (`Seq Scan`), because that's faster than using an
index for so few rows. Make it show you the index anyway:

```bash
db "set enable_seqscan = off; explain select slug from posts where tsv @@ websearch_to_tsquery('english','window')"
# Bitmap Index Scan on posts_tsv_idx
```

The planner decides per query, from table statistics. Indexes matter once tables grow.

**5. Accounts, by hash only.** Sign in on http://localhost:3000 once, then:

```bash
db "select email, created_at from users"
db "select left(token_hash, 12) as hash, expires_at from sessions"
db "select purpose, attempts, used_at is not null as used from login_tokens"
```

Your browser's cookie holds the token; the table holds only its SHA-256. A stolen copy of this
table can't sign anyone in.

## 💥 Break it (25 min, local only)

**1. Never edit an applied migration.** Add a comment line to the end of
`V3__sign_in_codes.sql` and restart the API: it refuses with *checksum mismatch*. History is
history. Undo: `git checkout -- api/src/main/resources/db/migration/V3__sign_in_codes.sql`.

**2. Change the schema the right way.** Create `api/src/main/resources/db/migration/V4__learn.sql`:

```sql
alter table posts add column learn_note text;
```

Restart the API and look at `flyway_schema_history` again: version 4 is there. Clean up in this
order (if you only delete the file, Flyway refuses: an applied migration has gone missing):

```bash
rm api/src/main/resources/db/migration/V4__learn.sql
db "alter table posts drop column learn_note"
db "delete from flyway_schema_history where version = '4'"
```

Restart the API.

**3. Re-live the password story.** Change the database's password behind the API's back, then
put it back to the one in `.env`:

```bash
db "alter role onehintaway password 'oops'"
# restart the API: "password authentication failed for user onehintaway"
P=$(grep '^POSTGRES_PASSWORD=' api/.env | cut -d= -f2- | tr -d '\r')
db "alter role onehintaway password '$P'"; unset P
# restart the API: it starts
```

Notice `db` kept working the whole time: inside the container, local connections are trusted
(`pg_hba.conf`), and only network connections need the password. That's also why a lost password
can always be reset by someone who controls the container.

**4. Cascade.** Sign in on the site with a test address, mark a post as done, then:

```bash
db "select count(*) from progress"
db "delete from users where email = 'test@example.com'"     # the address you used
db "select count(*) from progress"                          # its rows went with it
```

## 🧠 Explain it

<details>
<summary>1. Why does changing POSTGRES_PASSWORD in .env do nothing to an existing database?</summary>

The image's setup script runs only when the data folder (the volume) is empty. It creates the
user then, and Postgres stores a SCRAM-SHA-256 hash in its own files. After that the variable is
ignored. Change the password with `ALTER ROLE`, or delete the volume (`down -v`) to start over.
</details>

<details>
<summary>2. Why must you never edit an applied migration? How do you fix a bad one in production?</summary>

Every database that ran it has already changed; editing the file would make databases disagree
about history, so Flyway refuses (checksum). Fix forward: add a new migration that corrects it.
</details>

<details>
<summary>3. How does the API count one view per visitor per day without storing who the visitor is?</summary>

The visitor id is SHA-256 of a secret salt, the date, the address and the browser name. It's
the same all day for one visitor, different tomorrow, and can't be reversed. The primary key
`(slug, day, visitor_hash)` plus `ON CONFLICT DO NOTHING` drops repeats.
</details>

<details>
<summary>4. Why is `tsv` a generated column and not filled in by the Java code?</summary>

Postgres computes it from the other columns on every insert and update, so it can never be stale
or forgotten. The GIN index on it makes `@@` fast on big tables.
</details>

<details>
<summary>5. What's wrong with "SELECT the count, add one, UPDATE it"?</summary>

Two requests can both read 5 and both write 6: one count is lost (a race). A single upsert
statement is atomic: the database serialises the two increments. When you truly must read
first and decide (the five-tries rule for codes), lock the rows with `SELECT … FOR UPDATE` so the
second request waits for the first to commit.
</details>

<details>
<summary>6. Why no foreign key from progress to posts, but one from progress to users?</summary>

Posts are replaced on every sync, and progress must survive that. Users are only deleted on
purpose, and then their progress *should* go: the cascade guarantees it.
</details>

## 🎤 Interview corner

> "How do you make a counter correct under concurrency?" Don't read then write. Use one atomic
> statement: a unique key plus `INSERT … ON CONFLICT DO NOTHING` for dedupe, or
> `ON CONFLICT DO UPDATE SET n = n + 1` for counting. When a rule needs a read before the write
> ("at most five wrong tries"), lock the rows first: `SELECT … FOR UPDATE` inside a transaction,
> so concurrent requests queue instead of all reading the same old count. This project learned
> that the hard way: 30 guesses sent at once used to get 13 checked instead of 5.

## ✅ You now know

- [ ] Every table, and why two of them have cascades and three have no foreign keys
- [ ] How Flyway applies, records and protects migrations
- [ ] How full-text search works, and how to see whether an index is used
- [ ] Where the database password really lives, and how to reset it
- [ ] Why atomic statements beat read-then-write

---

**Next →** [7 · Accounts and security](07-accounts-security.md)

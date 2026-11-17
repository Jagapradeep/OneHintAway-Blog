-- Accounts: sign-in by emailed link, sessions and reading progress. No passwords anywhere.

-- One account per email address. The email is stored lowercase.
-- A second sign-in method (such as Google) would add its own table that points at
-- users.id; this table and sessions would not change.
create table users (
    id              bigint generated always as identity primary key,
    email           text        not null unique,
    created_at      timestamptz not null,
    last_sign_in_at timestamptz not null
);

-- One row per emailed link. Only SHA-256 of the token is stored, so a copy of this table
-- can't be used to sign in. It is keyed on the email, not on a user, because the account
-- is only created when a first link is used.
create table login_tokens (
    token_hash text        primary key,
    email      text        not null,
    purpose    text        not null check (purpose in ('SIGN_IN', 'DELETE_ACCOUNT')),
    created_at timestamptz not null,
    expires_at timestamptz not null,
    used_at    timestamptz
);
create index login_tokens_email_idx on login_tokens (email, created_at);

-- One row per signed-in browser. The cookie holds the token; the table holds its hash.
-- Nothing here says how the reader signed in.
create table sessions (
    token_hash   text        primary key,
    user_id      bigint      not null references users (id) on delete cascade,
    created_at   timestamptz not null,
    last_used_at timestamptz not null,
    expires_at   timestamptz not null
);
create index sessions_user_idx on sessions (user_id);

-- Posts a reader has marked as done. No foreign key to posts: the posts sync replaces
-- that table, and it must not wipe anyone's progress.
create table progress (
    user_id bigint      not null references users (id) on delete cascade,
    slug    text        not null,
    done_at timestamptz not null,
    primary key (user_id, slug)
);

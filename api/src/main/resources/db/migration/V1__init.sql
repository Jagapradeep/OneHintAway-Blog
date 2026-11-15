-- Posts: a copy of the site's frontmatter and plain text, replaced on every sync.
-- tsv is worked out by Postgres from the other columns, so it can never be stale.
create table posts (
    slug      text primary key,
    number    integer not null,
    title     text    not null,
    pattern   text    not null,
    section   text    not null,
    tags      text[]  not null default '{}',
    body_text text    not null default '',
    tsv       tsvector generated always as (
                  setweight(to_tsvector('english', title), 'A') ||
                  setweight(to_tsvector('english', pattern), 'B') ||
                  setweight(to_tsvector('english', body_text), 'C')
              ) stored
);
create index posts_tsv_idx on posts using gin (tsv);

-- One row per post, day and visitor: the primary key is what makes a second view
-- from the same visitor on the same day a no-op.
create table post_views (
    slug         text not null,
    day          date not null,
    visitor_hash text not null,
    primary key (slug, day, visitor_hash)
);

-- A counter per post, language and day.
create table code_copies (
    slug  text   not null,
    lang  text   not null check (lang in ('java', 'python', 'cpp', 'javascript')),
    day   date   not null,
    count bigint not null default 0,
    primary key (slug, lang, day)
);

-- No foreign keys from the two tables above to posts: a sync that drops a post
-- must not delete its history.

create table subscribers (
    id           bigint generated always as identity primary key,
    email        text        not null unique,
    status       text        not null check (status in ('PENDING', 'CONFIRMED', 'UNSUBSCRIBED')),
    token        text        not null unique,
    created_at   timestamptz not null,
    confirmed_at timestamptz
);

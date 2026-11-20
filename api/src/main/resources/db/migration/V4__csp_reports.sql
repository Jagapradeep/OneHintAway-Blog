-- Content-Security-Policy violations that readers' browsers report (CspReportController).
-- Counted, not stored one by one: one row per (rule, blocked address, page), so a page
-- with a problem seen ten thousand times is still one row. No reader data: no address,
-- no browser details, no query strings.
create table csp_reports (
    directive   text        not null,  -- the rule that would block, e.g. script-src-elem
    blocked     text        not null,  -- what it would block: an address without its query, or inline / eval / data
    page        text        not null,  -- the site page it happened on, path only
    count       bigint      not null default 1,
    first_seen  timestamptz not null,
    last_seen   timestamptz not null,
    primary key (directive, blocked, page)
);

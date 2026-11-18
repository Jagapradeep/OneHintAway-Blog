-- Sign-in by a 6-digit code typed on the site, instead of a link (18 November 2026).
-- A code is short enough to guess, so each one counts wrong tries and dies after five.
-- token_hash is now SHA-256 of "<email>:<code>"; old link rows simply expire.
alter table login_tokens add column attempts int not null default 0;

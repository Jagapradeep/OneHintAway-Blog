# 7 · Accounts and security

> ⏱ 60 min · 🧰 the API running (the code appears in its log), Git Bash, the `db` shortcut from chapter 6

## 📖 The story

The first version of sign-in emailed a **magic link**: tap it and you're in. Clean, no
passwords. Then came the problem: many company mail filters **open every link** in an incoming
email to scan it, and some even run the page's script. A one-time link opened by a robot is a
used link. The reader taps it a minute later and gets "This link has expired".

On 18 November the link became a **6-digit code** the reader types on the site. A robot can open
a link, but it won't type a code into your website. But a 6-digit code can be *guessed*, which a
43-character link couldn't. This chapter is how the code was made safe, and everything else that
keeps an account an account.

## 💡 The idea in 2 minutes

**The flow:**

```text
reader types email ──► POST /api/v1/auth/code       202 always (known or not: no address-checking)
  (+ Turnstile token)   API asks Cloudflare: did a person's browser make this token? No → 403, no email
                       API makes a random 6-digit code, stores SHA-256("email:code"),
                       expires in 15 min, saves it, *then* emails it (Resend; on your laptop:
                       the log). Email failed? The code is deleted again and the answer is 503
reader types code  ──► POST /api/v1/auth/session    lock the address's live codes (FOR UPDATE), then:
                       {email, code}                right? spend it (used_at) ··· wrong? attempts + 1
                                                    on every live code (5 and it's dead)
                       creates the user on first sign-in, creates a session row (token hash only)
                  ◄──  Set-Cookie: __Host-ohw_session=<random token>; HttpOnly; Secure; SameSite=Lax;
                       Path=/; Max-Age=2592000 (30 days, renewed at most once a day while used)
every later call ──►   cookie + Origin + X-OHW-CSRF header → GET /me, PUT /progress/{slug}, …
```

**Why guessing a code is useless:** a million possible codes; five wrong tries kill every live
code for that address; at most three codes per address per hour (`LINK_PER_EMAIL_PER_HOUR`), and
ten per caller per hour (`LINK_PER_HOUR`). An attacker gets about 15 guesses an hour out of a
million: a 0.0015 % chance, and the reader sees codes they didn't ask for.

**What each cookie flag buys:**

| Flag | Stops |
| --- | --- |
| `HttpOnly` | page scripts reading the cookie, so an injected script can't steal the session |
| `Secure` | sending the cookie over plain HTTP, where anyone on the Wi-Fi could read it |
| `SameSite=Lax` | sending it on requests started by *other* sites (most CSRF) |
| `__Host-` prefix | the cookie being set by a subdomain or for another path; the browser enforces `Secure`, `Path=/` and no `Domain` |

**CSRF, belt and braces.** Every change on an account path needs the request's `Origin` to be in
`CORS_ORIGINS` **and** a custom header `X-OHW-CSRF`. A plain HTML form on another site can't add
custom headers, and a script on another site that tries triggers a CORS preflight, which the
API refuses for unknown origins.

**Deleting an account needs a fresh proof**: a code sent for that purpose, and a session younger
than 15 minutes. A borrowed laptop with an old session can't delete you.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `api/.../accounts/AccountService.java` | `sendCode` (limits counted in SQL; no transaction while emailing), `exchange` (lock, check, spend the code, upsert the user, new session), `find` (renew at most once a day), `signOutEverywhere` |
| `api/.../accounts/SessionCookie.java` | the cookie's name and flags; `Cache-Control: no-store` on every account answer |
| `api/.../accounts/CsrfInterceptor.java` | the Origin + header check, 403 otherwise |
| `api/.../accounts/AuthController.java` | `code`, `session`, `me`, `sign-out`, `sign-out-everywhere`, `DELETE account` |
| `api/.../config/WebConfig.java` | credentialed CORS only for the account paths, exact origins |
| `api/src/test/.../AccountIntegrationTests.java` | every rule above, as a test (chapter 8) |
| `api/.../accounts/TurnstileVerifier.java`, `HumanCheck.java` | the call to Cloudflare's `siteverify`; off when no secret is set; fails closed (503) when Cloudflare can't be reached |
| `site/lib/account.ts`, `site/components/SignInForm.tsx` | the site's side: two steps, `autocomplete="one-time-code"` |
| `site/components/HumanCheck.tsx` | loads Turnstile only while a sign-in form is open; one fresh token per request |
| `site/app/privacy/page.tsx` | what's stored, in plain words for readers |

## 🛠 Try it (30 min)

All in Git Bash. `H` holds the headers a real browser on the site would send:

```bash
H='-H Origin:http://localhost:3000 -H X-OHW-CSRF:1 -H Content-Type:application/json'
curl -si $H -d '{"email":"me@example.com"}' localhost:8080/api/v1/auth/code | head -1      # 202
```

Find the code in the API's log (`Sign-in code for me@example.com: 123456`), then:

```bash
R=$(curl -si $H -d '{"email":"me@example.com","code":"PUT-IT-HERE"}' localhost:8080/api/v1/auth/session)
echo "$R" | grep -i "HTTP/\|set-cookie"        # 200, and the cookie with every flag from the table
C=$(echo "$R" | grep -i '^set-cookie' | sed -E 's/^[^:]*: *([^;]*).*/\1/' | tr -d '\r')   # keep it, like a browser
```

Then:

```bash
echo "$C"                                                      # __Host-ohw_session=…
curl -s -H "Cookie: $C" localhost:8080/api/v1/auth/me; echo     # who am I
db "select left(token_hash, 12) as hash, expires_at from sessions"    # only the hash is stored
db "select purpose, attempts, used_at is not null as used from login_tokens where email = 'me@example.com'"
```

> **Why not `curl -c jar`?** curl refuses to store a `Secure` cookie that arrived over plain
> `http://`, even from localhost, so the jar stays empty. Browsers make an exception for
> `localhost`, which is why the site works on your laptop. With `SESSION_COOKIE_SECURE=false` in
> `api/.env` the cookie is called `ohw_session` with no `Secure` flag, and a jar would work.

Now the CSRF check, with the same cookie:

```bash
curl -si -H "Cookie: $C" -X POST localhost:8080/api/v1/auth/sign-out | head -1        # 403: no Origin, no header
curl -si -H "Cookie: $C" -X POST -H "Origin: https://evil.example" -H "X-OHW-CSRF: 1" \
     localhost:8080/api/v1/auth/sign-out | head -1                                    # 403: wrong Origin
```

## 💥 Break it (20 min)

1. **Guessing.** Ask for a new code, send a wrong code five times, then the right one: `410`
   every time. Five wrong tries killed it.
2. **Replay.** Ask for a code, use it once (200), use it again: `410`. One use only.
3. **A copied cookie dies on sign-out.** Keep a copy, `C2="$C"`, as if someone had stolen it.
   Sign out: `curl -s $H -H "Cookie: $C" -X POST localhost:8080/api/v1/auth/sign-out`. Now
   `curl -si -H "Cookie: $C2" localhost:8080/api/v1/auth/me | head -1`: `401`. Signing out
   deletes the session row, so every copy of the cookie stops working.
4. **No address-checking.** Ask for a code for an address that has never signed in: still `202`,
   same answer.

Clean up:

```bash
db "delete from users where email = 'me@example.com'"
db "delete from login_tokens where email = 'me@example.com'"
unset R C C2
```

## 🛡️ The threat model, honestly

| Threat | Protected? | How / why not |
| --- | --- | --- |
| Someone guesses a code | ✅ | 5 tries, 3 codes an hour, 15 minutes. Since 20 November also for guesses sent all at once: they wait their turn on a row lock (`FOR UPDATE`). Before that, a burst of 30 got 13 checked |
| A database backup leaks | ✅ mostly | only hashes of codes and sessions; emails *are* in it |
| Another site acts as the reader (CSRF) | ✅ | Origin allow-list + custom header + `SameSite=Lax` |
| A script injected into our own site (XSS) | ⚠️ partly | it can't read the cookie (`HttpOnly`), but it can call the API as the reader, because the CSRF header isn't a secret |
| Someone reads the reader's inbox | ❌ | they can sign in: email is the only factor |
| A stolen cookie | ⚠️ | works until sign-out, sign-out everywhere, or 30 idle days; no device binding |
| Telling known from unknown addresses | ✅ by answer, ❓ by timing | the answer is always 202; response timing wasn't measured |
| A script makes the API send thousands of emails (using up the Resend allowance, so real readers get no code) | ✅ | since 20 November every sign-in code request needs a Cloudflare Turnstile token the API verifies. The per-caller and per-address limits alone didn't stop a script that rotates addresses and IPs |
| A slow email provider stalls the whole API | ✅ | since 20 November the code is saved and committed *before* the email is sent, so no database connection waits on Resend. Before that, a burst of sign-ins during a Resend slowdown could hold every pooled connection |

Knowing the limits is part of the design. Say them out loud in an interview: it shows you
understand the system, not just the happy path.

## 🧠 Explain it

<details>
<summary>1. Why store SHA-256 of the code and session token instead of the values?</summary>

If the table leaks (a backup, a bug), hashes are useless: you can't send a hash as a cookie or
type it as a code. The server hashes what the reader sends and looks up the hash.
</details>

<details>
<summary>2. A code is only 6 digits. What makes guessing it useless?</summary>

Five wrong tries kill every live code for the address, and there are at most 3 codes an hour per
address. That's about 15 guesses an hour against a million possibilities, and the reader sees
codes arriving that they didn't ask for.
</details>

<details>
<summary>3. Why are sessions in Postgres and not in the API pod's memory?</summary>

Pods are replaced on every deploy, and there can be more than one (your laptop runs two;
production ran two until 20 November). Sessions in the database work on
any pod and survive restarts. It also makes "sign out everywhere" one `DELETE`.
</details>

<details>
<summary>4. What do HttpOnly, Secure, SameSite=Lax and __Host- each protect against?</summary>

Script theft; sniffing on plain HTTP; most cross-site requests carrying the cookie; a subdomain
or another path planting or scoping the cookie. See the table above.
</details>

<details>
<summary>5. Why does deleting an account need a new code if the reader is already signed in?</summary>

A signed-in session might be on a shared or stolen device. Deletion is irreversible, so it
requires fresh proof of the inbox, used within 15 minutes.
</details>

<details>
<summary>6. Why did the link become a code?</summary>

Mail filters open links (and sometimes run scripts) to scan them, which spent one-time links
before the reader got to them. A code must be typed into our site, which robots don't do.
</details>

<details>
<summary>7. The code checked "attempts < 5". How did 30 guesses sent at once get 13 checked?</summary>

Each request read the live codes, compared, *then* added one to `attempts`. Requests arriving
together read `attempts` before the others had written, so many passed the check. The fix:
`SELECT … FOR UPDATE` locks the rows, so the next request waits until the previous one has
committed its +1. A test (`aBurstOfGuessesSentAtOnceStillGetsOnlyFiveTries`) fires 30 threads
at once and requires exactly 5 checked; without the lock it fails with 13.
</details>

<details>
<summary>8. Why does the code request need a Turnstile token, and why does the API check it rather than the site?</summary>

Every code is a real email, and emails have a daily allowance. The rate limits count per caller
and per address, so a script that rotates both could still send thousands. Turnstile makes each
request prove a real browser made it. The site can't be trusted to check (a script just skips
the site and calls the API), so the browser gets a one-use token and the API confirms it with
Cloudflare using a secret key only the API has. If Cloudflare can't be reached the API says 503
rather than letting requests through, so an outage can't switch the protection off.
</details>

<details>
<summary>9. Why is sending the code email kept outside a database transaction?</summary>

A transaction holds one of the pool's few connections until it ends. If the email (a network
call that can take seconds) ran inside it, a burst of sign-ins during a slow moment at Resend
could take every connection and stall every other request, even page views. So the code is saved
first, the email is sent with no connection held, and if it fails the code is deleted again.
</details>

## 🎤 Interview corner

> "Design passwordless login." Email a short-lived, single-use code; store only its hash; limit
> wrong tries per code and codes per address; answer the same for known and unknown addresses.
> On success, create a random session token, store its hash server-side, and send it in an
> `HttpOnly; Secure; SameSite` cookie. Protect state-changing calls with an Origin check and a
> custom header. Then state the limits: the inbox is the only factor, and XSS can still act as
> the user.

## ✅ You now know

- [ ] The sign-in flow, request by request
- [ ] Why codes beat links here, and why guessing doesn't work
- [ ] What every cookie flag does
- [ ] How CSRF is stopped, and what isn't protected

---

**Next →** [8 · Testing and quality](08-testing.md)

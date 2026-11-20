# 12 · Production edges: server, DNS, HTTPS, email

> ⏱ 60 min · 🧰 the production kubeconfig (read-only commands), Gmail on a computer

## 📖 The story

The sign-in email looked perfect in every preview. Then it was opened in **Gmail on Android in
dark mode**, and the logo was inside out: the black tile turned white, the white lines black.
Gmail's dark mode (Chromium's "force dark") inverts every image up to **64 pixels** on a side,
whatever is in it. It was measured: 64 px inverted, 66 px kept. The fix: the logo and the name
"ONE HINT AWAY" became one 180-pixel-wide image, too big to be inverted.

That's the edge of a system: the parts you don't control (mail apps, DNS resolvers, certificate
authorities, the open internet) where things fail in ways no unit test predicts. This chapter is
everything between the internet and your pods.

## 💡 The idea in 2 minutes

| Edge | What it does here |
| --- | --- |
| **The server** | DigitalOcean, 2 vCPU / 4 GB, Ubuntu 24.04. Hardened by script: SSH keys only, firewall (only 22, 80, 443 and 6443 open), automatic security updates, fail2ban, 2 GB swap. Then k3s. |
| **DNS** | `onehintaway.com` → Cloudflare (the static site, proxied). `api.`, `stats.`, `grafana.` → an A record straight to the server's IP, **not proxied**. |
| **HTTPS** | Traefik terminates TLS on the server. **cert-manager** asks Let's Encrypt for certificates (HTTP-01 challenge) and renews them about a month before they expire. HTTP redirects to HTTPS. |
| **Security headers** | Rules the browser enforces for us: HTTPS only (HSTS), where scripts may come from and where a page may send data (CSP), no framing by other sites, no content-type guessing. The site's come from Cloudflare (`_headers`, written at build time); the API's and Umami's from Traefik middlewares. Added 21 November. |
| **Email** | The API → Resend → the reader. Three DNS records prove the mail is really from `onehintaway.com`: SPF, DKIM, DMARC. |

**SPF, DKIM and DMARC in one line each:**

- **SPF:** a DNS list of servers allowed to send mail for the domain.
- **DKIM:** each email is signed with a private key; the public key is in DNS, so the receiver
  can check the email wasn't forged or changed.
- **DMARC:** tells receivers what to do when SPF/DKIM don't line up with the From address. Here
  `p=reject`: throw it away. Nobody can send convincing fake mail "from" this domain.

**The headers, one line each:**

| Header | Tells the browser |
| --- | --- |
| `Strict-Transport-Security` | "For a year, only ever use HTTPS for this domain and its subdomains", so a network attacker can't downgrade the first request to plain HTTP |
| `Content-Security-Policy` | which origins may supply scripts, styles, images, frames, and which the page may `fetch` (the API, Umami). `frame-ancestors 'none'`: no other site may frame it |
| `X-Content-Type-Options: nosniff` | trust the Content-Type; never treat a text file as a script |
| `X-Frame-Options: DENY` | the old way of saying "don't frame me", for old browsers |
| `Referrer-Policy` | send only the origin, not the full address, to other sites |
| `Permissions-Policy` | camera, microphone, location, payment: off. Fullscreen: only for this site (the slide gallery) |

**The honest limit of this CSP:** it allows inline scripts (`'unsafe-inline'`). A static export has
no server to stamp a per-request nonce, and Next.js writes page-specific inline scripts, so a
strict policy would need a different header for every page. The CSP still decides *where* code
and data may come from and go to; the defence against injected inline script is that the site
never renders HTML a reader wrote.

**Report-only first.** A wrong CSP breaks things silently: the browser just refuses the script.
So it went live as `Content-Security-Policy-Report-Only`: browsers block nothing for it and post
a short report to `POST /api/v1/csp-report` for everything it *would* have blocked. The API
counts them in `csp_reports` (one row per rule, blocked address and page; extensions and other
sites ignored). After a week or two of real readers on real browsers, if the table shows nothing
the site needs, one line (`ENFORCE_CSP = true`) switches it to enforcing. The other headers were
enforced from day one: they can't break a page.

**How Let's Encrypt knows you own `api.onehintaway.com` (HTTP-01):** cert-manager asks for a
certificate; Let's Encrypt replies "put this token at
`http://api.onehintaway.com/.well-known/acme-challenge/<x>`"; cert-manager serves it through
Traefik; Let's Encrypt fetches it over the internet. Only whoever controls the server that name
points to can do that. This is why the API is **not** behind Cloudflare's proxy.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `deploy/server/01-harden.sh` | `ufw default deny incoming`, the four allowed ports, SSH settings, unattended-upgrades |
| `deploy/server/02-k3s.sh` | installs k3s with secrets encryption; generates `/root/onehintaway.env` and the Secret from it |
| `deploy/server/cluster.yaml` | the ClusterIssuer `letsencrypt` (HTTP-01), the deploy account |
| `deploy/helm/onehintaway/templates/ingress.yaml` | hosts, TLS, the middlewares (https-redirect, security-headers, api-headers); the API routes only `/api` and `/actuator/health` |
| `site/scripts/write-headers.mjs` | writes `out/_headers` after every build: the site's CSP, built from the same `NEXT_PUBLIC_*` addresses as the pages; `ENFORCE_CSP` (report-only until it's true) |
| `api/.../reports/CspReportController.java` | receives browsers' violation reports in both formats, drops noise, counts the rest in `csp_reports` |
| `api/src/main/resources/mail/*.html` | the emails: tables and inline styles, because mail apps ignore most CSS |
| `deploy/README.md` | "Rebuild the server from nothing": the whole edge, as commands |

## 🛠 Try it (40 min)

**1. The server (read-only).**

```bash
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml get nodes -o wide
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml top nodes
```

**2. DNS: two names, two destinations.**

```bash
nslookup onehintaway.com            # Cloudflare's addresses (the site)
nslookup api.onehintaway.com        # your server's address
```

**3. The certificate.**

```bash
echo | openssl s_client -connect api.onehintaway.com:443 -servername api.onehintaway.com 2>/dev/null \
  | openssl x509 -noout -issuer -enddate          # issuer=…Let's Encrypt…  notAfter=… (about 90 days out)
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml get certificate -A
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway describe certificate api-tls | tail -15
curl -sI http://api.onehintaway.com/actuator/health/readiness | head -3     # 308 Permanent Redirect → https
curl -s -o /dev/null -w "%{http_code}\n" https://api.onehintaway.com/actuator/prometheus   # 404: metrics stay inside
```

(Git Bash's `curl` on Windows uses Windows' own TLS library and doesn't print certificate
details, hence `openssl`.)

**4. Security headers.**

```bash
curl -sI https://onehintaway.com/ | grep -iE "strict-transport|content-security|x-frame|nosniff|permissions"
curl -sI https://api.onehintaway.com/actuator/health/readiness | grep -iE "strict-transport|content-security|x-frame|nosniff"
```

Then open the site in a browser, DevTools → Console, and click around. While the CSP is
report-only, a miss shows as `[Report Only] Refused to load …` and still loads; once enforced,
without `[Report Only]`, and it doesn't. And read what readers' browsers reported:

```bash
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway exec -i postgres-0 -- psql -U onehintaway \
  -d onehintaway -c "select directive, blocked, page, count from csp_reports order by count desc limit 20"
```
 Try
breaking it on your laptop: build the site, remove `https://challenges.cloudflare.com` from
`out/_headers`, serve it with `npx wrangler dev`, open `/sign-in/`, and watch Turnstile be refused.

**5. Email authentication.**

```bash
nslookup -type=TXT _dmarc.onehintaway.com              # p=reject
nslookup -type=TXT resend._domainkey.onehintaway.com   # DKIM public key (Resend signs with the private one)
nslookup -type=TXT send.onehintaway.com                # SPF: who may send
```

Then sign in on the live site, open the code email in Gmail on a computer, **⋮ → Show original**:
SPF, DKIM and DMARC all say `PASS`. That's why it lands in the inbox and not in spam.

**6. Preview every email locally** (no sending):

```bash
cd api && ./mvnw -q test -Dtest=MailPreviewTests && ls target/mail-preview/
```

## 🧠 Explain it

<details>
<summary>1. SPF, DKIM, DMARC in one sentence each. What does p=reject do to a forged email?</summary>

SPF lists who may send; DKIM signs each message so it can't be forged or changed; DMARC says
what to do when they fail to match the From domain. `p=reject` tells receivers to refuse it.
</details>

<details>
<summary>2. How does cert-manager prove ownership of api.onehintaway.com?</summary>

HTTP-01: it serves a token Let's Encrypt gave it at a well-known URL on that hostname, and Let's
Encrypt fetches it from the internet. Only the server the DNS name points to can answer.
</details>

<details>
<summary>3. Why is the API not behind Cloudflare's proxy while the site is?</summary>

The site *is* Cloudflare (static files at its edge). The API runs on our server, and the HTTP-01
challenge and our own certificate need the traffic to reach that server directly. (Proxying would
also put a second TLS hop and Cloudflare's rules in front of the API.)
</details>

<details>
<summary>4. Port 6443 (the Kubernetes API) is open to the internet. Why is that acceptable?</summary>

Every call needs a valid client credential (a certificate or a token in a kubeconfig); without
one it's refused. It's what lets CI deploy. Tighter options: allow only GitHub's IP ranges, or
put it behind a VPN.
</details>

<details>
<summary>5. The site's CSP allows inline scripts. Is it worth having, then?</summary>

Yes, for what it does control: scripts only from this site, Umami and Turnstile; `fetch` only to
the API and Umami (so an injected script can't send data to an attacker's server with `fetch`);
no plugins, no `<base>` hijack, no posting forms elsewhere, no framing. A nonce-based policy
would also block injected inline script, but needs a server per request, which a static site
doesn't have.
</details>

<details>
<summary>6. Why did the CSP start in report-only mode, and the other headers not?</summary>

A CSP that misses an address the site really uses breaks that feature for readers, silently,
and a test on one browser can't see every phone, browser version and extension. Report-only
lets real traffic check the list with nothing at risk. HSTS, nosniff, frame denial and the rest
can't break a page the site serves, so there was nothing to trial.
</details>

<details>
<summary>7. Why are the emails built from tables and inline styles?</summary>

Mail apps strip `<style>` blocks, external CSS and modern layout. Tables and inline styles are
what renders the same in Gmail, Outlook and Apple Mail. And any image under 65 px may be inverted
in dark mode, so the header is one wide image.
</details>

## 🎤 Interview corner

> "How do you get HTTPS on a self-hosted Kubernetes cluster?" An ingress controller (Traefik)
> terminates TLS; cert-manager with a Let's Encrypt ClusterIssuer issues and renews certificates
> automatically via HTTP-01, which requires DNS to point straight at the server. Then redirect
> HTTP to HTTPS (a 308 here) and expose only the routes the public needs, keeping metrics internal.
> Add security headers at the edge (HSTS, CSP, nosniff, frame denial) in one middleware for every
> route, and test the CSP by loading every page with it and collecting violations before shipping.

## ✅ You now know

- [ ] What the hardening script does and which ports are open
- [ ] Why the site and the API resolve to different places
- [ ] How a Let's Encrypt certificate is issued and renewed
- [ ] SPF, DKIM, DMARC, and why emails are built the old-fashioned way

---

**Next →** [13 · Operations](13-operations.md)

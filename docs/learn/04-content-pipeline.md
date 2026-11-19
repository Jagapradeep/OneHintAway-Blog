# 4 · How a post reaches the site

> ⏱ 30 min · 🧰 the API running, `site/` installed

## 📖 The story

On 31 October the first twenty posts were rewritten to a fixed shape, and one rule kept being
broken by hand: the last slide listed the worked example as a practice problem, so the page
showed the same problem twice. The fix wasn't "be more careful". It was a rule in a script:
`check-posts` now stops the build when a practice link equals the worked example. Every rule in
this pipeline exists because a person once got it wrong.

## 💡 The idea in 2 minutes

A post travels through four stops. Each stop **checks** what the previous one handed over:

```text
1. dsa-post skill (Claude)  ── writes the content: hook, walk, pseudocode, code, practice
         │
2. post-kit/render.py       ── draws slides (1080 × 1350 PNG) and the video (MP4), runs the code
         │                     in four languages against a brute force, writes NN-slug.mdx + a zip
         │
3. npm run add-post         ── copies the MDX to site/content/posts/, slides to site/public/posts/NN/,
         │                     shrinks the video, runs check-posts
         │
4. git push                 ── Workers Builds: check-posts + check-viz + next build → live
                               Actions "Sync posts": export the posts as text → PUT to the API → search
```

**The contract** is the agreement between stops 1 to 3: the exact frontmatter fields, the order
of the body's sections, the four code languages. It's written in the root README's "Anatomy of a
post" and enforced by `site/scripts/check-posts.mjs`. The rule: when a post fails, fix the post,
not the checker (unless the contract itself should change).

**Search** is the last stop. The site is static, so it can't search itself. `export-posts`
turns every post into plain text (`posts-index.json`), and the sync sends that list to the API,
which **replaces** its `posts` table with it. Postgres then builds the search index by itself
(chapter 6).

## 📂 Where it lives

| File | Role |
| --- | --- |
| `site/content/posts/NN-slug.mdx` | one post: YAML frontmatter, then the body |
| `site/public/posts/NN/` | `slide-01.png` … and `slide-NN.mp4` |
| `site/scripts/add-post.mjs` | adds a post from the kit (zip or folder) |
| `site/scripts/check-posts.mjs` | every rule of the contract, with an error that names the file and the rule |
| `site/scripts/export-posts.mjs` | posts → plain text; `--push` sends them to `PUT /api/v1/admin/posts` |
| `api/.../posts/PostSyncController.java` | checks the admin token, replaces the table |
| `.github/workflows/sync-posts.yml` | runs the sync when posts change, with the `ADMIN_TOKEN` secret |
| `post-kit/README.md` | the kit's own guide (needs WSL or Linux) |

## 🛠 Try it (15 min)

**1. Read one post as data.** Open `site/content/posts/12-kadane.mdx`. Match each frontmatter
field to what you see on http://localhost:3000/posts/kadane/: `summary` under the title,
`practice` at the bottom, `video: 2` on the second slide.

**2. See what search sees.**

```bash
cd site
npm run export-posts                    # writes posts-index.json (git-ignored)
head -c 600 posts-index.json            # slug, title, pattern, section, tags, bodyText
npm run sync-posts                      # PUT it to http://localhost:8080 with ADMIN_TOKEN from api/.env
curl -s "localhost:8080/api/v1/search?q=running%20sum" | head -c 300; echo
```

## 💥 Break it (10 min)

**1. The duplicate that started it all.** In `12-kadane.mdx`, copy the `worked:` line's URL into
the first `practice` entry's `url`. Run `npm run check-posts`:

```text
practice[0] is the worked example; leave it out of practice (the page shows it first)
```

Undo with `git checkout -- content/posts/12-kadane.mdx`.

**2. A wrong admin token.**

```bash
ADMIN_TOKEN=wrong npm run sync-posts
# sync-posts: http://localhost:8080 answered 401: {"status":401,"title":"Unauthorized"}
```

A value in your shell beats the one in `api/.env`. Open `PostSyncController.authorize()`: it
compares tokens with `MessageDigest.isEqual`, which takes the same time however much of the
guess was right, so response times leak nothing.

## 🧠 Explain it

<details>
<summary>1. Why does the API's posts table get replaced on every sync instead of updated?</summary>

The site's MDX files are the source of truth; the table is only a copy for search. Replacing it
means a deleted or renamed post can't linger. The sync refuses an empty list, so a broken export
can't wipe search.
</details>

<details>
<summary>2. If a post is deleted from the site, are its view counts lost?</summary>

No. `post_views` and `code_copies` deliberately have no foreign key to `posts`, so the sync
dropping a post doesn't delete its history (chapter 6).
</details>

<details>
<summary>3. Why is the check a build step and not a review habit?</summary>

A script checks all posts on every build, never gets tired, and runs in the cloud too, so a
broken post can't deploy even if nobody looked.
</details>

## 🎤 Interview corner

> "How do you keep content quality high with an AI in the loop?" Treat the AI's output like any
> untrusted input: a written contract for its shape, and automated checks at every hand-over. The
> code is run against a brute force in four languages, the post format is checked before every
> build, and the build refuses anything that breaks a rule.

## ✅ You now know

- [ ] The four stops a post goes through, and what each one checks
- [ ] Where the contract is written and where it's enforced
- [ ] How a static site gets search, and why the table is replaced

---

**Next →** [5 · The API with Spring Boot](05-api.md)

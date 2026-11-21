package com.onehintaway.api.posts;

import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
class SearchController {

	/** Body-only matches count when the words are in at most this share of the posts. */
	static final int RARE_DIVISOR = 4;

	/** ... but never fewer than this many posts (a small table would refuse everything). */
	static final int RARE_MIN = 3;

	/** A common word that names no post: show only the best few body matches. */
	static final int COMMON_FALLBACK = 5;

	/** Matches inside a word ("ort" in "sort") need at least this many characters typed. */
	static final int INSIDE_MIN = 3;

	private static final int MAX_WORDS = 8;

	private final JdbcClient jdbc;

	SearchController(JdbcClient jdbc) {
		this.jdbc = jdbc;
	}

	record Hit(String slug, int number, String title, String pattern, String section) {
	}

	/**
	 * Two kinds of match, strong first.
	 * <ul>
	 * <li>Strong: every typed word begins a word of the title, the pattern or a tag ("slid"
	 * finds "Sliding window" while the reader types; "ort" does not find "sort"). Titles
	 * that start with the whole query come first, then other title matches, then pattern
	 * and tag matches.</li>
	 * <li>Body: full-text search over the body (stemmed whole words, best rank first). A
	 * word most posts use ("start", "array", "java") says nothing about which post the
	 * reader wants, so body-only matches are shown only when they are rare: in at most a
	 * quarter of the posts. When the word is common and no post is named by it, the best
	 * five body matches are shown instead of nothing.</li>
	 * <li>Inside a word, last: only when no post is a strong match, the text anywhere in a
	 * title or pattern ("string" finds "Minimum Window Substring"), at least three
	 * characters, at most five posts, after any body matches.</li>
	 * </ul>
	 */
	@GetMapping("/api/v1/search")
	List<Hit> search(@RequestParam @NotBlank @Size(max = 100) String q) {
		String term = q.strip();
		String like = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + '%';
		// Letters and digits only, so each word is safe inside a regular expression.
		String words = Arrays.stream(term.toLowerCase(Locale.ROOT).split("[^\\p{L}\\p{N}]+"))
			.filter((w) -> !w.isEmpty())
			.limit(MAX_WORDS)
			.collect(Collectors.joining(" "));
		return this.jdbc.sql("""
				with q as (select websearch_to_tsquery('english', :q) as tq),
				hits as (
				  select p.slug, p.number, p.title, p.pattern, p.section,
				         p.title ilike :like as title_starts,
				         :words <> '' and p.title ~* all (
				           select '\\m' || w from unnest(string_to_array(:words, ' ')) w) as in_title,
				         :words <> '' and (p.title || ' ' || p.pattern || ' ' || array_to_string(p.tags, ' ')) ~* all (
				           select '\\m' || w from unnest(string_to_array(:words, ' ')) w) as strong,
				         p.tsv @@ q.tq as in_text,
				         ts_rank(p.tsv, q.tq) as rank,
				         :inside <> '' and (p.title ilike :inside or p.pattern ilike :inside) as inside,
				         :inside <> '' and p.title ilike :inside as inside_title
				  from posts p, q
				),
				counts as (
				  select count(*) filter (where strong) as strong_n,
				         count(*) filter (where in_text and not strong) as body_n,
				         count(*) as total
				  from hits
				),
				body as (
				  select h.*, row_number() over (order by h.rank desc, h.number) as body_rank
				  from hits h
				  where h.in_text and not h.strong
				),
				body_shown as (
				  select b.* from body b, counts c
				  where c.body_n <= greatest(:rareMin, c.total / :rareDivisor)
				     or (c.strong_n = 0 and b.body_rank <= :fallback)
				),
				inside as (
				  select h.*, row_number() over (order by h.inside_title desc, h.number) as inside_rank
				  from hits h, counts c
				  where c.strong_n = 0 and h.inside
				    and h.slug not in (select slug from body_shown)
				)
				select slug, number, title, pattern, section from (
				  select slug, number, title, pattern, section, 0 as tier, title_starts, in_title, rank
				  from hits where strong
				  union all
				  select slug, number, title, pattern, section, 1, false, false, rank
				  from body_shown
				  union all
				  select slug, number, title, pattern, section, 2, false, inside_title, 0
				  from inside where inside_rank <= :fallback
				) found
				order by tier, title_starts desc, in_title desc, rank desc, number
				limit 20
				""")
			.param("q", term)
			.param("like", like)
			.param("inside", term.length() >= INSIDE_MIN ? '%' + like : "")
			.param("words", words)
			.param("rareMin", RARE_MIN)
			.param("rareDivisor", RARE_DIVISOR)
			.param("fallback", COMMON_FALLBACK)
			.query(Hit.class)
			.list();
	}

}

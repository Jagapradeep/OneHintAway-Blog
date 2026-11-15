package com.onehintaway.api.stats;

import java.util.LinkedHashMap;
import java.util.Map;

import com.onehintaway.api.posts.PostRepository;
import com.onehintaway.api.visitor.VisitorHasher;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * View and copy counters for a post. Counting is done by the database in single
 * statements (insert-or-ignore, insert-or-add-one), so two requests at the same moment
 * can't lose a count and no row is read before it is written.
 */
@RestController
@RequestMapping("/api/v1/posts/{slug}")
class StatsController {

	private static final String SLUG = "[a-z0-9]+(-[a-z0-9]+)*";

	private final JdbcClient jdbc;

	private final PostRepository posts;

	private final VisitorHasher hasher;

	StatsController(JdbcClient jdbc, PostRepository posts, VisitorHasher hasher) {
		this.jdbc = jdbc;
		this.posts = posts;
		this.hasher = hasher;
	}

	record Stats(String slug, long views, long copies, Map<String, Long> copiesByLang) {
	}

	/** One view per visitor per day: a repeat hits the primary key and changes nothing. */
	@PostMapping("/views")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void view(@PathVariable @Pattern(regexp = SLUG) @Size(max = 80) String slug, HttpServletRequest request) {
		requirePost(slug);
		this.jdbc.sql("""
				insert into post_views (slug, day, visitor_hash) values (:slug, :day, :hash)
				on conflict do nothing
				""")
			.param("slug", slug)
			.param("day", this.hasher.today())
			.param("hash", this.hasher.visitor(request))
			.update();
	}

	@PostMapping("/copies")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void copy(@PathVariable @Pattern(regexp = SLUG) @Size(max = 80) String slug,
			@RequestParam @Pattern(regexp = "java|python|cpp|javascript") String lang) {
		requirePost(slug);
		this.jdbc.sql("""
				insert into code_copies (slug, lang, day, count) values (:slug, :lang, :day, 1)
				on conflict (slug, lang, day) do update set count = code_copies.count + 1
				""").param("slug", slug).param("lang", lang).param("day", this.hasher.today()).update();
	}

	@GetMapping("/stats")
	Stats stats(@PathVariable @Pattern(regexp = SLUG) @Size(max = 80) String slug) {
		requirePost(slug);
		long views = this.jdbc.sql("select count(*) from post_views where slug = :slug")
			.param("slug", slug)
			.query(Long.class)
			.single();
		Map<String, Long> byLang = new LinkedHashMap<>();
		this.jdbc.sql("select lang, sum(count) as total from code_copies where slug = :slug group by lang order by lang")
			.param("slug", slug)
			.query((rs, row) -> byLang.put(rs.getString("lang"), rs.getLong("total")))
			.list();
		long copies = byLang.values().stream().mapToLong(Long::longValue).sum();
		return new Stats(slug, views, copies, byLang);
	}

	/** Counts are kept only for posts the site has synced, so made-up slugs can't fill the tables. */
	private void requirePost(String slug) {
		if (!this.posts.existsById(slug)) {
			throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No such post");
		}
	}

}

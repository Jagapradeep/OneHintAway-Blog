package com.onehintaway.api.posts;

import java.util.List;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
class SearchController {

	private final JdbcClient jdbc;

	SearchController(JdbcClient jdbc) {
		this.jdbc = jdbc;
	}

	record Hit(String slug, int number, String title, String pattern, String section) {
	}

	/**
	 * Full-text search over title, pattern and body, best match first. Full-text search
	 * matches whole words only, so a half-typed word ("slid") would find nothing; the
	 * extra ILIKE on title and pattern covers search-as-you-type.
	 */
	@GetMapping("/api/v1/search")
	List<Hit> search(@RequestParam @NotBlank @Size(max = 100) String q) {
		String term = q.strip();
		String like = '%' + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + '%';
		return this.jdbc.sql("""
				select slug, number, title, pattern, section
				from posts
				where tsv @@ websearch_to_tsquery('english', :q)
				   or title ilike :like or pattern ilike :like
				order by ts_rank(tsv, websearch_to_tsquery('english', :q)) desc, number
				limit 20
				""").param("q", term).param("like", like).query(Hit.class).list();
	}

}

package com.onehintaway.api.accounts;

import java.sql.Timestamp;
import java.time.Clock;
import java.util.List;

import com.onehintaway.api.accounts.AccountService.Session;
import com.onehintaway.api.posts.PostRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** The posts a signed-in reader has marked as done. PUT and DELETE are safe to repeat. */
@RestController
@RequestMapping("/api/v1/progress")
class ProgressController {

	private static final String SLUG = "[a-z0-9]+(-[a-z0-9]+)*";

	private final JdbcClient jdbc;

	private final PostRepository posts;

	private final SessionCookie cookie;

	private final Clock clock;

	ProgressController(JdbcClient jdbc, PostRepository posts, SessionCookie cookie, Clock clock) {
		this.jdbc = jdbc;
		this.posts = posts;
		this.cookie = cookie;
		this.clock = clock;
	}

	record Progress(List<String> done) {
	}

	@GetMapping
	Progress list(HttpServletRequest request, HttpServletResponse response) {
		Session session = this.cookie.require(request, response);
		return new Progress(this.jdbc.sql("select slug from progress where user_id = :user order by done_at, slug")
			.param("user", session.userId())
			.query(String.class)
			.list());
	}

	/** Only for a post that exists, so the table can't be filled with made-up names. */
	@PutMapping("/{slug}")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void done(@PathVariable @Pattern(regexp = SLUG) @Size(max = 80) String slug, HttpServletRequest request,
			HttpServletResponse response) {
		Session session = this.cookie.require(request, response);
		if (!this.posts.existsById(slug)) {
			throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No such post");
		}
		this.jdbc.sql("""
				insert into progress (user_id, slug, done_at) values (:user, :slug, :now)
				on conflict do nothing
				""")
			.param("user", session.userId())
			.param("slug", slug)
			.param("now", Timestamp.from(this.clock.instant()))
			.update();
	}

	@DeleteMapping("/{slug}")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void notDone(@PathVariable @Pattern(regexp = SLUG) @Size(max = 80) String slug, HttpServletRequest request,
			HttpServletResponse response) {
		Session session = this.cookie.require(request, response);
		this.jdbc.sql("delete from progress where user_id = :user and slug = :slug")
			.param("user", session.userId())
			.param("slug", slug)
			.update();
	}

}

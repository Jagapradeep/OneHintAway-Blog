package com.onehintaway.api.posts;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

import com.onehintaway.api.config.AppProperties;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * Replaces the posts table with the list the site's export script sends at deploy time.
 * The caller proves itself with a shared secret in the Authorization header.
 */
@RestController
class PostSyncController {

	static final String SLUG = "[a-z0-9]+(-[a-z0-9]+)*";

	private final PostRepository posts;

	private final String adminToken;

	PostSyncController(PostRepository posts, AppProperties props) {
		this.posts = posts;
		this.adminToken = props.adminToken();
	}

	record PostPayload(
			@NotBlank @Pattern(regexp = SLUG) @Size(max = 80) String slug,
			@Min(0) int number,
			@NotBlank @Size(max = 200) String title,
			@NotBlank @Size(max = 100) String pattern,
			@NotBlank @Size(max = 100) String section,
			@Size(max = 30) List<@NotBlank @Size(max = 50) String> tags,
			@Size(max = 200_000) String bodyText) {
	}

	record SyncResult(int saved, int deleted) {
	}

	/**
	 * The whole list every time, in one transaction: posts in the list are inserted or
	 * updated, posts missing from it are deleted. An empty list is refused, so a broken
	 * export cannot wipe the table.
	 */
	@PutMapping("/api/v1/admin/posts")
	@Transactional
	SyncResult sync(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization,
			@RequestBody @NotEmpty @Size(max = 2000) List<@Valid PostPayload> payload) {
		authorize(authorization);
		List<Post> incoming = payload.stream()
			.map(p -> new Post(p.slug(), p.number(), p.title(), p.pattern(), p.section(),
					p.tags() == null ? new String[0] : p.tags().toArray(String[]::new),
					p.bodyText() == null ? "" : p.bodyText()))
			.toList();
		this.posts.saveAll(incoming);
		this.posts.flush();
		int deleted = this.posts.deleteAllExcept(incoming.stream().map(Post::getSlug).toList());
		return new SyncResult(incoming.size(), deleted);
	}

	private void authorize(String authorization) {
		if (this.adminToken == null || this.adminToken.isBlank()) {
			throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Posts sync is switched off");
		}
		byte[] expected = ("Bearer " + this.adminToken).getBytes(StandardCharsets.UTF_8);
		byte[] given = (authorization == null ? "" : authorization).getBytes(StandardCharsets.UTF_8);
		// isEqual takes the same time whether the first or the last byte differs,
		// so response times don't leak how much of a guess was right.
		if (!MessageDigest.isEqual(expected, given)) {
			throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
		}
	}

}

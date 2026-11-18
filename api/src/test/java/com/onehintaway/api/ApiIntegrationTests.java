package com.onehintaway.api;

import java.util.concurrent.atomic.AtomicInteger;

import com.onehintaway.api.subscribers.MailSender;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.request.RequestPostProcessor;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Every endpoint against a real PostgreSQL 16 in Docker (Testcontainers), with the real
 * Flyway migration. Only the email sender is replaced, to read the confirmation link.
 */
@SpringBootTest(properties = { "app.visitor-salt=test-salt", "app.admin-token=test-token",
		"app.cors-origins=https://onehintaway.com", "app.public-url=https://api.test",
		"app.site-url=https://onehintaway.com/",
		"app.rate.subscribe-per-hour=3", "app.rate.admin-per-minute=1000" })
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration.class)
class ApiIntegrationTests {

	private static final String SITE = "https://onehintaway.com";

	private static final String TWO_POSTS = """
			[
			  {"slug": "sliding-window", "number": 8, "title": "Sliding window", "pattern": "Sliding window",
			   "section": "Arrays and hashing", "tags": ["sliding-window", "arrays"],
			   "bodyText": "Grow the window to the right and shrink it from the left while the budget is broken."},
			  {"slug": "kadane", "number": 12, "title": "Kadane's algorithm", "pattern": "Kadane's algorithm",
			   "section": "Arrays and hashing",
			   "bodyText": "Drop the running sum as soon as it goes below zero. Largest subarray sum."}
			]
			""";

	/** Rate limits are per address and live for the whole test run, so every test gets its own address. */
	private static final AtomicInteger nextAddress = new AtomicInteger(1);

	@Autowired
	private MockMvc mvc;

	@Autowired
	private JdbcClient jdbc;

	@MockitoBean
	private MailSender mail;

	private String address;

	@BeforeEach
	void cleanDatabaseAndSyncPosts() throws Exception {
		this.address = "203.0.113." + nextAddress.getAndIncrement();
		for (String table : new String[] { "post_views", "code_copies", "subscribers", "posts" }) {
			this.jdbc.sql("truncate table " + table).update();
		}
		sync("Bearer test-token", TWO_POSTS).andExpect(status().isOk()).andExpect(jsonPath("$.saved").value(2));
	}

	@Test
	void aViewCountsOncePerVisitorPerDay() throws Exception {
		view("sliding-window", this.address, "Firefox").andExpect(status().isNoContent());
		view("sliding-window", this.address, "Firefox").andExpect(status().isNoContent());
		stats("sliding-window").andExpect(jsonPath("$.views").value(1));

		view("sliding-window", this.address, "Safari").andExpect(status().isNoContent());
		view("sliding-window", "198.51.100.7", "Firefox").andExpect(status().isNoContent());
		stats("sliding-window").andExpect(jsonPath("$.views").value(3));
		stats("kadane").andExpect(jsonPath("$.views").value(0));
	}

	@Test
	void theDatabaseNeverHoldsTheVisitorsAddress() throws Exception {
		view("kadane", this.address, "Firefox");
		String stored = this.jdbc.sql("select visitor_hash from post_views").query(String.class).single();
		assertThat(stored).matches("[0-9a-f]{64}").doesNotContain(this.address);
	}

	@Test
	void unknownOrMalformedSlugsAreRefused() throws Exception {
		view("no-such-post", this.address, "Firefox").andExpect(status().isNotFound());
		view("Not_A_Slug", this.address, "Firefox").andExpect(status().isBadRequest());
		stats("no-such-post").andExpect(status().isNotFound());
		assertThat(count("post_views")).isZero();
	}

	@Test
	void copiesAreCountedPerLanguage() throws Exception {
		copy("kadane", "java").andExpect(status().isNoContent());
		copy("kadane", "java").andExpect(status().isNoContent());
		copy("kadane", "python").andExpect(status().isNoContent());
		copy("kadane", "ruby").andExpect(status().isBadRequest());
		stats("kadane").andExpect(jsonPath("$.copies").value(3))
			.andExpect(jsonPath("$.copiesByLang.java").value(2))
			.andExpect(jsonPath("$.copiesByLang.python").value(1));
	}

	@Test
	void searchFindsWholeWordsHalfTypedTitlesAndRanksTitlesFirst() throws Exception {
		search("budget").andExpect(jsonPath("$", hasSize(1))).andExpect(jsonPath("$[0].slug").value("sliding-window"));
		search("slid").andExpect(jsonPath("$[0].slug").value("sliding-window"));
		search("sum").andExpect(jsonPath("$[0].slug").value("kadane")).andExpect(jsonPath("$[0].number").value(12));
		search("quicksort").andExpect(status().isOk()).andExpect(jsonPath("$", hasSize(0)));
		search("100%_'; drop table posts").andExpect(status().isOk()).andExpect(jsonPath("$", hasSize(0)));
		search(" ").andExpect(status().isBadRequest());
		search("x".repeat(101)).andExpect(status().isBadRequest());
	}

	@Test
	void theSyncNeedsTheTokenAndRefusesAnEmptyList() throws Exception {
		sync(null, TWO_POSTS).andExpect(status().isUnauthorized());
		sync("Bearer wrong", TWO_POSTS).andExpect(status().isUnauthorized());
		sync("Bearer test-token", "[]").andExpect(status().isBadRequest());
		sync("Bearer test-token", "[{\"slug\": \"Bad Slug\", \"number\": 1, \"title\": \"t\", \"pattern\": \"p\", \"section\": \"s\"}]")
			.andExpect(status().isBadRequest());
		assertThat(count("posts")).isEqualTo(2);
	}

	@Test
	void theSyncUpdatesAndDeletesPostsButKeepsTheirCounts() throws Exception {
		view("kadane", this.address, "Firefox");
		String onlyOne = """
				[{"slug": "sliding-window", "number": 8, "title": "Variable window", "pattern": "Sliding window",
				  "section": "Arrays and hashing", "bodyText": "New text."}]
				""";
		sync("Bearer test-token", onlyOne).andExpect(status().isOk())
			.andExpect(jsonPath("$.saved").value(1))
			.andExpect(jsonPath("$.deleted").value(1));
		search("variable").andExpect(jsonPath("$[0].slug").value("sliding-window"));
		search("kadane").andExpect(jsonPath("$", hasSize(0)));
		assertThat(count("post_views")).isEqualTo(1);
	}

	@Test
	void aSubscriptionOnlyCountsAfterTheEmailLinkIsOpened() throws Exception {
		subscribe("Reader@Example.com", this.address).andExpect(status().isAccepted());
		assertThat(subscriberStatus()).isEqualTo("PENDING");

		// Signing up again sends the same link again and makes no second row.
		subscribe("reader@example.com", this.address).andExpect(status().isAccepted());
		ArgumentCaptor<String> link = ArgumentCaptor.forClass(String.class);
		verify(this.mail, times(2)).sendConfirmation(eq("reader@example.com"), link.capture());
		assertThat(link.getAllValues().get(0)).isEqualTo(link.getAllValues().get(1))
			.startsWith("https://api.test/api/v1/subscribers/confirm?token=");
		assertThat(count("subscribers")).isEqualTo(1);

		String path = link.getValue().substring("https://api.test".length());
		// The reader is sent to the welcome page on the site; opening the link twice is fine.
		this.mvc.perform(get(path)).andExpect(status().isSeeOther()).andExpect(redirectedUrl(SITE + "/subscribed/"));
		this.mvc.perform(get(path)).andExpect(status().isSeeOther()).andExpect(redirectedUrl(SITE + "/subscribed/"));
		assertThat(subscriberStatus()).isEqualTo("CONFIRMED");
		assertThat(this.jdbc.sql("select confirmed_at is not null from subscribers").query(Boolean.class).single()).isTrue();

		// Already confirmed: same answer to the caller; no third confirmation, but a note to
		// the address's owner with a way to unsubscribe (the page on the site posts the token).
		subscribe("reader@example.com", this.address).andExpect(status().isAccepted());
		verify(this.mail, times(2)).sendConfirmation(any(), any());
		ArgumentCaptor<String> out = ArgumentCaptor.forClass(String.class);
		verify(this.mail).sendAlreadySubscribed(eq("reader@example.com"), out.capture());
		String token = link.getValue().substring(link.getValue().indexOf("token=") + 6);
		assertThat(out.getValue()).isEqualTo(SITE + "/unsubscribe/#token=" + token);

		// The unsubscribe page posts the token: the address leaves the list. Twice is fine.
		for (int i = 0; i < 2; i++) {
			this.mvc.perform(post("/api/v1/subscribers/unsubscribe").with(from("203.0.113.200", "Firefox"))
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"token\": \"" + token + "\"}")).andExpect(status().isNoContent());
		}
		assertThat(count("subscribers")).isZero();
		// Opening the link with GET does nothing.
		this.mvc.perform(get("/api/v1/subscribers/unsubscribe").param("token", token)).andExpect(status().is4xxClientError());
	}

	@Test
	void badAddressesAndBadTokensAreRefused() throws Exception {
		subscribe("not-an-email", this.address).andExpect(status().isBadRequest());
		subscribe("", this.address).andExpect(status().isBadRequest());
		this.mvc.perform(get("/api/v1/subscribers/confirm").param("token", "made-up"))
			.andExpect(status().isSeeOther())
			.andExpect(redirectedUrl(SITE + "/subscribed/expired/"));
		assertThat(count("subscribers")).isZero();
	}

	@Test
	void theFourthSignUpInAnHourFromOneAddressIsRefused() throws Exception {
		for (int i = 0; i < 3; i++) {
			subscribe("reader" + i + "@example.com", this.address).andExpect(status().isAccepted());
		}
		// A different browser name does not get a fresh allowance; a different address does.
		this.mvc
			.perform(post("/api/v1/subscribers").with(from(this.address, "Another browser"))
				.header(HttpHeaders.ORIGIN, SITE)
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"email\": \"reader9@example.com\"}"))
			.andExpect(status().isTooManyRequests())
			.andExpect(header().exists(HttpHeaders.RETRY_AFTER))
			.andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, SITE));
		subscribe("reader9@example.com", "198.51.100.99").andExpect(status().isAccepted());
		assertThat(count("subscribers")).isEqualTo(4);
	}

	@Test
	void onlyTheSiteMayCallFromABrowser() throws Exception {
		this.mvc.perform(get("/api/v1/search").param("q", "sum").header(HttpHeaders.ORIGIN, SITE))
			.andExpect(status().isOk())
			.andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, SITE));
		this.mvc.perform(get("/api/v1/search").param("q", "sum").header(HttpHeaders.ORIGIN, "https://evil.example"))
			.andExpect(status().isForbidden());
	}

	@Test
	void theKubernetesProbesAnswer() throws Exception {
		this.mvc.perform(get("/actuator/health/liveness")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
		this.mvc.perform(get("/actuator/health/readiness")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
	}

	private org.springframework.test.web.servlet.ResultActions view(String slug, String address, String browser)
			throws Exception {
		return this.mvc.perform(post("/api/v1/posts/{slug}/views", slug).with(from(address, browser)));
	}

	private org.springframework.test.web.servlet.ResultActions copy(String slug, String lang) throws Exception {
		return this.mvc
			.perform(post("/api/v1/posts/{slug}/copies", slug).param("lang", lang).with(from(this.address, "Firefox")));
	}

	private org.springframework.test.web.servlet.ResultActions stats(String slug) throws Exception {
		return this.mvc.perform(get("/api/v1/posts/{slug}/stats", slug));
	}

	private org.springframework.test.web.servlet.ResultActions search(String q) throws Exception {
		return this.mvc.perform(get("/api/v1/search").param("q", q));
	}

	private org.springframework.test.web.servlet.ResultActions subscribe(String email, String address) throws Exception {
		return this.mvc.perform(post("/api/v1/subscribers").with(from(address, "Firefox"))
			.contentType(MediaType.APPLICATION_JSON)
			.content("{\"email\": \"" + email + "\"}"));
	}

	private org.springframework.test.web.servlet.ResultActions sync(String authorization, String json) throws Exception {
		MockHttpServletRequestBuilder request = put("/api/v1/admin/posts").with(from("192.0.2.1", "sync"))
			.contentType(MediaType.APPLICATION_JSON)
			.content(json);
		if (authorization != null) {
			request.header(HttpHeaders.AUTHORIZATION, authorization);
		}
		return this.mvc.perform(request);
	}

	private static RequestPostProcessor from(String address, String browser) {
		return request -> {
			request.setRemoteAddr(address);
			request.addHeader("User-Agent", browser);
			return request;
		};
	}

	private long count(String table) {
		return this.jdbc.sql("select count(*) from " + table).query(Long.class).single();
	}

	private String subscriberStatus() {
		return this.jdbc.sql("select status from subscribers").query(String.class).single();
	}

}

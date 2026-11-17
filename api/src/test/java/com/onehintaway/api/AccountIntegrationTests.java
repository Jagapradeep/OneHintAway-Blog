package com.onehintaway.api;

import java.util.concurrent.atomic.AtomicInteger;

import com.onehintaway.api.subscribers.MailSender;
import jakarta.servlet.http.Cookie;
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
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.options;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Accounts, sessions, CSRF and progress against a real PostgreSQL 16 (Testcontainers) with
 * the real migrations. Only the email sender is replaced, to read the emailed link.
 */
@SpringBootTest(properties = { "app.visitor-salt=test-salt", "app.admin-token=test-token",
		"app.cors-origins=https://onehintaway.com", "app.public-url=https://api.test",
		"app.site-url=https://onehintaway.com/", "app.rate.admin-per-minute=1000", "app.rate.link-per-hour=6",
		"app.rate.link-per-email-per-hour=3" })
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration.class)
class AccountIntegrationTests {

	private static final String SITE = "https://onehintaway.com";

	private static final String COOKIE = "__Host-ohw_session";

	private static final String LINK_START = SITE + "/sign-in/#token=";

	private static final AtomicInteger nextAddress = new AtomicInteger(1);

	@Autowired
	private MockMvc mvc;

	@Autowired
	private JdbcClient jdbc;

	@MockitoBean
	private MailSender mail;

	private String address;

	@BeforeEach
	void cleanDatabase() throws Exception {
		this.address = "198.51.100." + nextAddress.getAndIncrement();
		this.jdbc.sql("truncate table users, login_tokens, sessions, progress, posts").update();
		this.mvc
			.perform(put("/api/v1/admin/posts").header(HttpHeaders.AUTHORIZATION, "Bearer test-token")
				.contentType(MediaType.APPLICATION_JSON)
				.content("""
						[{"slug": "kadane", "number": 12, "title": "Kadane's algorithm", "pattern": "Kadane's algorithm",
						  "section": "Arrays and hashing", "bodyText": "x"},
						 {"slug": "two-pointers", "number": 6, "title": "Two pointers", "pattern": "Two pointers",
						  "section": "Arrays and hashing", "bodyText": "x"}]
						"""))
			.andExpect(status().isOk());
	}

	// --- the emailed link ---

	@Test
	void aFirstLinkCreatesTheAccountAndSetsALockedDownCookie() throws Exception {
		String token = requestLink("  Reader@Example.com ".strip());
		assertThat(count("users")).isZero();
		// Only the hash is stored.
		String stored = this.jdbc.sql("select token_hash from login_tokens").query(String.class).single();
		assertThat(stored).matches("[0-9a-f]{64}").isNotEqualTo(token);

		MvcResult result = exchange(token).andExpect(status().isOk())
			.andExpect(jsonPath("$.email").value("reader@example.com"))
			.andExpect(jsonPath("$.purpose").value("sign-in"))
			.andExpect(header().string(HttpHeaders.CACHE_CONTROL, "no-store"))
			.andReturn();
		String setCookie = result.getResponse().getHeader(HttpHeaders.SET_COOKIE);
		assertThat(setCookie).startsWith(COOKIE + "=")
			.contains("HttpOnly")
			.contains("Secure")
			.contains("SameSite=Lax")
			.contains("Path=/")
			.contains("Max-Age=2592000")
			.doesNotContain("Domain");
		String session = result.getResponse().getCookie(COOKIE).getValue();
		assertThat(this.jdbc.sql("select token_hash from sessions").query(String.class).single())
			.matches("[0-9a-f]{64}")
			.isNotEqualTo(session);
		assertThat(this.jdbc.sql("select email from users").query(String.class).single()).isEqualTo("reader@example.com");

		me(session).andExpect(status().isOk()).andExpect(jsonPath("$.email").value("reader@example.com"));
		// A second sign-in with the same address is the same account.
		signIn("reader@example.com");
		assertThat(count("users")).isEqualTo(1);
		assertThat(count("sessions")).isEqualTo(2);
	}

	@Test
	void openingTheLinkWithGetNeitherSignsInNorUsesItUp() throws Exception {
		String token = requestLink("reader@example.com");
		// What a mail scanner does: GET, with every guess at where the token might go.
		this.mvc.perform(get("/api/v1/auth/session").param("token", token)).andExpect(status().isMethodNotAllowed());
		this.mvc.perform(get("/api/v1/auth/session/" + token)).andExpect(status().isNotFound());
		this.mvc.perform(get("/api/v1/auth/link").param("token", token)).andExpect(status().isMethodNotAllowed());
		this.mvc.perform(get("/api/v1/auth/me").param("token", token)).andExpect(status().isUnauthorized());
		assertThat(count("sessions")).isZero();
		assertThat(count("users")).isZero();
		// The reader's own click still works afterwards.
		exchange(token).andExpect(status().isOk());
	}

	@Test
	void aUsedExpiredOrForgedLinkIsRefusedTheSameWay() throws Exception {
		String used = requestLink("reader@example.com");
		exchange(used).andExpect(status().isOk());
		exchange(used).andExpect(status().isGone()).andExpect(header().doesNotExist(HttpHeaders.SET_COOKIE));

		String expired = requestLink("reader@example.com");
		this.jdbc.sql("update login_tokens set expires_at = now() - interval '1 second' where used_at is null").update();
		exchange(expired).andExpect(status().isGone()).andExpect(header().doesNotExist(HttpHeaders.SET_COOKIE));

		exchange("A".repeat(43)).andExpect(status().isGone());
		exchange(used.substring(0, 42) + (used.endsWith("A") ? "B" : "A")).andExpect(status().isGone());
		exchange("short").andExpect(status().isBadRequest());
		exchange("x".repeat(500)).andExpect(status().isBadRequest());
		assertThat(count("sessions")).isEqualTo(1);
	}

	@Test
	void theLinkLastsFifteenMinutes() throws Exception {
		requestLink("reader@example.com");
		long seconds = this.jdbc.sql("select extract(epoch from (expires_at - created_at)) from login_tokens")
			.query(Long.class)
			.single();
		assertThat(seconds).isEqualTo(900);
	}

	@Test
	void theAnswerIsTheSameForKnownAndUnknownAddresses() throws Exception {
		signIn("known@example.com");
		String known = link("known@example.com", this.address).andExpect(status().isAccepted())
			.andReturn()
			.getResponse()
			.getContentAsString();
		String unknown = link("stranger@example.com", this.address).andExpect(status().isAccepted())
			.andReturn()
			.getResponse()
			.getContentAsString();
		assertThat(known).isEqualTo(unknown).isEmpty();
		verify(this.mail, times(2)).sendSignInLink(eq("known@example.com"), any(), eq(false));
		verify(this.mail).sendSignInLink(eq("stranger@example.com"), any(), eq(false));
		link("not-an-email", this.address).andExpect(status().isBadRequest());
		link("", this.address).andExpect(status().isBadRequest());
	}

	@Test
	void oneEmailAddressGetsAtMostThreeLinksAnHourWhoeverAsks() throws Exception {
		for (int i = 0; i < 5; i++) {
			// A different caller each time, so only the per-email limit is in play.
			link("reader@example.com", "192.0.2." + (100 + i)).andExpect(status().isAccepted());
		}
		verify(this.mail, times(3)).sendSignInLink(eq("reader@example.com"), any(), anyBoolean());
		assertThat(count("login_tokens")).isEqualTo(3);
	}

	@Test
	void oneCallerGetsAtMostSixLinkRequestsAnHour() throws Exception {
		for (int i = 0; i < 6; i++) {
			link("reader" + i + "@example.com", this.address).andExpect(status().isAccepted());
		}
		link("reader7@example.com", this.address).andExpect(status().isTooManyRequests())
			.andExpect(header().exists(HttpHeaders.RETRY_AFTER));
	}

	// --- sessions ---

	@Test
	void aCookieStolenBeforeSignOutIsUselessAfterIt() throws Exception {
		String stolen = signIn("reader@example.com");
		String other = signIn("reader@example.com");
		this.mvc.perform(site(post("/api/v1/auth/sign-out")).cookie(new Cookie(COOKIE, stolen)))
			.andExpect(status().isNoContent())
			.andExpect(header().string(HttpHeaders.SET_COOKIE, org.hamcrest.Matchers.containsString("Max-Age=0")));
		me(stolen).andExpect(status().isUnauthorized());
		this.mvc.perform(site(put("/api/v1/progress/kadane")).cookie(new Cookie(COOKIE, stolen)))
			.andExpect(status().isUnauthorized());
		// The other device stays signed in.
		me(other).andExpect(status().isOk());
	}

	@Test
	void signOutEverywhereEndsEverySessionOfThatReaderOnly() throws Exception {
		String phone = signIn("reader@example.com");
		String laptop = signIn("reader@example.com");
		String someoneElse = signIn("other@example.com");
		this.mvc.perform(site(post("/api/v1/auth/sign-out-everywhere")).cookie(new Cookie(COOKIE, laptop)))
			.andExpect(status().isNoContent());
		me(phone).andExpect(status().isUnauthorized());
		me(laptop).andExpect(status().isUnauthorized());
		me(someoneElse).andExpect(status().isOk());
		this.mvc.perform(site(post("/api/v1/auth/sign-out-everywhere"))).andExpect(status().isUnauthorized());
	}

	@Test
	void aSessionIsRenewedOnUseAndEndsWhenLeftAlone() throws Exception {
		String session = signIn("reader@example.com");
		// Used today already: no new cookie.
		me(session).andExpect(header().doesNotExist(HttpHeaders.SET_COOKIE));

		this.jdbc.sql("update sessions set last_used_at = now() - interval '2 days', expires_at = now() + interval '28 days'")
			.update();
		me(session).andExpect(status().isOk())
			.andExpect(header().string(HttpHeaders.SET_COOKIE, org.hamcrest.Matchers.containsString("Max-Age=2592000")));
		long daysLeft = this.jdbc.sql("select extract(epoch from (expires_at - now())) / 86400 from sessions")
			.query(Double.class)
			.single()
			.longValue();
		assertThat(daysLeft).isBetween(29L, 30L);

		this.jdbc.sql("update sessions set expires_at = now() - interval '1 second'").update();
		me(session).andExpect(status().isUnauthorized());
		me("B".repeat(43)).andExpect(status().isUnauthorized());
		this.mvc.perform(get("/api/v1/auth/me")).andExpect(status().isUnauthorized());
	}

	// --- CSRF and CORS ---

	@Test
	void aChangeWithoutTheSitesOriginAndTheCustomHeaderIsRefused() throws Exception {
		String session = signIn("reader@example.com");
		Cookie cookie = new Cookie(COOKIE, session);
		String[] badOrigins = { null, "https://evil.example", "https://stats.onehintaway.com", "http://onehintaway.com",
				"https://onehintaway.com.evil.example", "null" };
		for (String origin : badOrigins) {
			for (MockHttpServletRequestBuilder request : new MockHttpServletRequestBuilder[] {
					put("/api/v1/progress/kadane"), delete("/api/v1/progress/kadane"), post("/api/v1/auth/sign-out"),
					post("/api/v1/auth/sign-out-everywhere"), delete("/api/v1/auth/account"),
					post("/api/v1/auth/link").contentType(MediaType.APPLICATION_JSON).content("{\"purpose\":\"delete\"}"),
					post("/api/v1/auth/session").contentType(MediaType.APPLICATION_JSON)
						.content("{\"token\":\"" + "A".repeat(43) + "\"}") }) {
				request.cookie(cookie).header("X-OHW-CSRF", "1");
				if (origin != null) {
					request.header(HttpHeaders.ORIGIN, origin);
				}
				this.mvc.perform(request).andExpect(status().isForbidden());
			}
		}
		// The right Origin but no custom header: what a cross-site form could at best send.
		this.mvc.perform(put("/api/v1/progress/kadane").cookie(cookie).header(HttpHeaders.ORIGIN, SITE))
			.andExpect(status().isForbidden());
		this.mvc.perform(delete("/api/v1/auth/account").cookie(cookie).header(HttpHeaders.ORIGIN, SITE))
			.andExpect(status().isForbidden());
		this.mvc
			.perform(post("/api/v1/auth/link").header(HttpHeaders.ORIGIN, SITE)
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"email\":\"a@example.com\"}"))
			.andExpect(status().isForbidden());

		// Nothing changed, and the session still works.
		assertThat(count("progress")).isZero();
		assertThat(count("users")).isEqualTo(1);
		me(session).andExpect(status().isOk());
		verify(this.mail, times(1)).sendSignInLink(any(), any(), anyBoolean());
	}

	@Test
	void onlyTheSiteMaySendTheCookieFromABrowser() throws Exception {
		for (String path : new String[] { "/api/v1/auth/session", "/api/v1/progress/kadane" }) {
			this.mvc
				.perform(options(path).header(HttpHeaders.ORIGIN, SITE)
					.header(HttpHeaders.ACCESS_CONTROL_REQUEST_METHOD, path.contains("progress") ? "PUT" : "POST")
					.header(HttpHeaders.ACCESS_CONTROL_REQUEST_HEADERS, "content-type, x-ohw-csrf"))
				.andExpect(status().isOk())
				.andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, SITE))
				.andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
			this.mvc
				.perform(options(path).header(HttpHeaders.ORIGIN, "https://evil.example")
					.header(HttpHeaders.ACCESS_CONTROL_REQUEST_METHOD, "POST"))
				.andExpect(status().isForbidden())
				.andExpect(header().doesNotExist(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN));
		}
		this.mvc.perform(get("/api/v1/auth/me").header(HttpHeaders.ORIGIN, "https://evil.example"))
			.andExpect(status().isForbidden());
		// The rest of the API never allows credentials.
		this.mvc.perform(get("/api/v1/search").param("q", "sum").header(HttpHeaders.ORIGIN, SITE))
			.andExpect(status().isOk())
			.andExpect(header().doesNotExist(HttpHeaders.ACCESS_CONTROL_ALLOW_CREDENTIALS));
	}

	// --- progress ---

	@Test
	void progressIsKeptPerReaderAndOnlyForRealPosts() throws Exception {
		Cookie reader = new Cookie(COOKIE, signIn("reader@example.com"));
		Cookie other = new Cookie(COOKIE, signIn("other@example.com"));

		this.mvc.perform(site(put("/api/v1/progress/kadane")).cookie(reader)).andExpect(status().isNoContent());
		this.mvc.perform(site(put("/api/v1/progress/kadane")).cookie(reader)).andExpect(status().isNoContent());
		this.mvc.perform(site(put("/api/v1/progress/two-pointers")).cookie(reader)).andExpect(status().isNoContent());
		this.mvc.perform(site(put("/api/v1/progress/no-such-post")).cookie(reader)).andExpect(status().isNotFound());
		this.mvc.perform(site(put("/api/v1/progress/Not_A_Slug")).cookie(reader)).andExpect(status().isBadRequest());

		this.mvc.perform(get("/api/v1/progress").cookie(reader))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.done", contains("kadane", "two-pointers")))
			.andExpect(header().string(HttpHeaders.CACHE_CONTROL, "no-store"));
		this.mvc.perform(get("/api/v1/progress").cookie(other)).andExpect(jsonPath("$.done", hasSize(0)));

		this.mvc.perform(site(delete("/api/v1/progress/kadane")).cookie(reader)).andExpect(status().isNoContent());
		this.mvc.perform(site(delete("/api/v1/progress/kadane")).cookie(reader)).andExpect(status().isNoContent());
		this.mvc.perform(get("/api/v1/progress").cookie(reader)).andExpect(jsonPath("$.done", contains("two-pointers")));

		// Signed out: nothing to read, nothing to write.
		this.mvc.perform(get("/api/v1/progress")).andExpect(status().isUnauthorized());
		this.mvc.perform(site(put("/api/v1/progress/kadane"))).andExpect(status().isUnauthorized());
		this.mvc.perform(site(delete("/api/v1/progress/kadane"))).andExpect(status().isUnauthorized());
	}

	// --- delete my account ---

	@Test
	void deletingTheAccountNeedsAFreshLinkAndRemovesEverything() throws Exception {
		String old = signIn("reader@example.com");
		Cookie oldCookie = new Cookie(COOKIE, old);
		Cookie other = new Cookie(COOKIE, signIn("other@example.com"));
		this.mvc.perform(site(put("/api/v1/progress/kadane")).cookie(oldCookie)).andExpect(status().isNoContent());
		this.mvc.perform(site(put("/api/v1/progress/kadane")).cookie(other)).andExpect(status().isNoContent());
		this.jdbc.sql("update sessions set created_at = now() - interval '16 minutes'").update();

		// Signed out: no. Signed in a while ago: not yet.
		this.mvc.perform(site(delete("/api/v1/auth/account"))).andExpect(status().isUnauthorized());
		this.mvc.perform(site(delete("/api/v1/auth/account")).cookie(oldCookie)).andExpect(status().isForbidden());
		assertThat(count("users")).isEqualTo(2);

		// The delete link can't be sent to anyone but the signed-in reader.
		this.mvc
			.perform(site(post("/api/v1/auth/link")).contentType(MediaType.APPLICATION_JSON)
				.content("{\"email\":\"victim@example.com\",\"purpose\":\"delete\"}"))
			.andExpect(status().isUnauthorized());
		this.mvc
			.perform(site(post("/api/v1/auth/link")).cookie(oldCookie)
				.contentType(MediaType.APPLICATION_JSON)
				.content("{\"email\":\"victim@example.com\",\"purpose\":\"delete\"}"))
			.andExpect(status().isAccepted());
		verify(this.mail, never()).sendSignInLink(eq("victim@example.com"), any(), anyBoolean());
		ArgumentCaptor<String> url = ArgumentCaptor.forClass(String.class);
		verify(this.mail).sendSignInLink(eq("reader@example.com"), url.capture(), eq(true));
		assertThat(url.getValue()).startsWith(LINK_START).endsWith("&for=delete");
		String token = url.getValue().substring(LINK_START.length(), LINK_START.length() + 43);

		MvcResult result = exchange(token).andExpect(status().isOk())
			.andExpect(jsonPath("$.purpose").value("delete"))
			.andReturn();
		// Opening the link deletes nothing by itself.
		assertThat(count("users")).isEqualTo(2);
		Cookie fresh = new Cookie(COOKIE, result.getResponse().getCookie(COOKIE).getValue());

		this.mvc.perform(site(delete("/api/v1/auth/account")).cookie(fresh))
			.andExpect(status().isNoContent())
			.andExpect(header().string(HttpHeaders.SET_COOKIE, org.hamcrest.Matchers.containsString("Max-Age=0")));
		assertThat(this.jdbc.sql("select email from users").query(String.class).list()).containsExactly("other@example.com");
		assertThat(count("sessions")).isEqualTo(1);
		assertThat(count("progress")).isEqualTo(1);
		assertThat(this.jdbc.sql("select count(*) from login_tokens where email = 'reader@example.com'")
			.query(Long.class)
			.single()).isZero();
		me(old).andExpect(status().isUnauthorized());
		me(fresh.getValue()).andExpect(status().isUnauthorized());
		this.mvc.perform(get("/api/v1/progress").cookie(other)).andExpect(jsonPath("$.done", contains("kadane")));
	}

	// --- helpers ---

	/** Every state-changing call the site makes carries these two headers. */
	private MockHttpServletRequestBuilder site(MockHttpServletRequestBuilder request) {
		String from = this.address;
		return request.header(HttpHeaders.ORIGIN, SITE).header("X-OHW-CSRF", "1").with(r -> {
			r.setRemoteAddr(from);
			return r;
		});
	}

	private ResultActions link(String email, String from) throws Exception {
		return this.mvc.perform(post("/api/v1/auth/link").header(HttpHeaders.ORIGIN, SITE)
			.header("X-OHW-CSRF", "1")
			.with(r -> {
				r.setRemoteAddr(from);
				return r;
			})
			.contentType(MediaType.APPLICATION_JSON)
			.content("{\"email\": \"" + email + "\"}"));
	}

	/** Asks for a link and returns the token from the email that went out last. */
	private String requestLink(String email) throws Exception {
		link(email, "192.0.2." + nextAddress.getAndIncrement()).andExpect(status().isAccepted());
		ArgumentCaptor<String> url = ArgumentCaptor.forClass(String.class);
		verify(this.mail, atLeastOnce()).sendSignInLink(eq(email.toLowerCase()), url.capture(), eq(false));
		assertThat(url.getValue()).startsWith(LINK_START).hasSize(LINK_START.length() + 43);
		return url.getValue().substring(LINK_START.length());
	}

	private ResultActions exchange(String token) throws Exception {
		return this.mvc.perform(site(post("/api/v1/auth/session")).contentType(MediaType.APPLICATION_JSON)
			.content("{\"token\": \"" + token + "\"}"));
	}

	/** The whole flow; returns the session cookie's value. */
	private String signIn(String email) throws Exception {
		// Each sign-in uses up one of the address's three links an hour.
		this.jdbc.sql("update login_tokens set created_at = created_at - interval '2 hours'").update();
		return exchange(requestLink(email)).andExpect(status().isOk()).andReturn().getResponse().getCookie(COOKIE).getValue();
	}

	private ResultActions me(String session) throws Exception {
		return this.mvc.perform(get("/api/v1/auth/me").cookie(new Cookie(COOKIE, session)));
	}

	private long count(String table) {
		return this.jdbc.sql("select count(*) from " + table).query(Long.class).single();
	}

}

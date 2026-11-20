package com.onehintaway.api;

import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.options;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** CSP violation reports from readers' browsers, in both formats browsers send, counted in Postgres. */
@SpringBootTest(properties = { "app.visitor-salt=test-salt", "app.admin-token=test-token",
		"app.cors-origins=https://onehintaway.com", "app.public-url=https://api.test",
		"app.site-url=https://onehintaway.com/" })
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration.class)
class CspReportTests {

	private static final AtomicInteger nextAddress = new AtomicInteger(1);

	/** The Reporting API's format (Chrome, Edge): a list, possibly several reports at once. */
	private static final String REPORTS_JSON = """
			[{"type": "csp-violation", "url": "https://onehintaway.com/posts/kadane/?ref=ig",
			  "body": {"documentURL": "https://onehintaway.com/posts/kadane/?ref=ig",
			           "blockedURL": "https://cdn.example.net/widget.js?v=3", "effectiveDirective": "script-src-elem",
			           "disposition": "report", "sourceFile": "https://onehintaway.com/posts/kadane/"}},
			 {"type": "csp-violation",
			  "body": {"documentURL": "https://onehintaway.com/", "blockedURL": "inline",
			           "effectiveDirective": "style-src-attr", "disposition": "report"}},
			 {"type": "deprecation", "body": {"id": "something-else"}}]
			""";

	/** The older report-uri format (Firefox, Safari). */
	private static final String CSP_REPORT = """
			{"csp-report": {"document-uri": "https://onehintaway.com/sign-in/", "blocked-uri": "https://challenges.example.org/x.js",
			                "violated-directive": "script-src-elem", "effective-directive": "script-src-elem",
			                "original-policy": "default-src 'self'"}}
			""";

	@Autowired
	private MockMvc mvc;

	@Autowired
	private JdbcClient jdbc;

	private String address;

	@BeforeEach
	void clean() {
		this.address = "203.0.113." + nextAddress.getAndIncrement();
		this.jdbc.sql("truncate table csp_reports").update();
	}

	@Test
	void reportsInTheReportingApiFormatAreCountedAndRepeatsAddUp() throws Exception {
		send("application/reports+json", REPORTS_JSON).andExpect(status().isNoContent());
		send("application/reports+json", REPORTS_JSON).andExpect(status().isNoContent());

		assertThat(rows()).containsExactlyInAnyOrder(
				Map.of("directive", "script-src-elem", "blocked", "https://cdn.example.net/widget.js", "page",
						"/posts/kadane/", "count", 2L),
				Map.of("directive", "style-src-attr", "blocked", "inline", "page", "/", "count", 2L));
	}

	@Test
	void reportsInTheOlderFormatAreCountedToo() throws Exception {
		send("application/csp-report", CSP_REPORT).andExpect(status().isNoContent());

		assertThat(rows()).containsExactly(Map.of("directive", "script-src-elem", "blocked",
				"https://challenges.example.org/x.js", "page", "/sign-in/", "count", 1L));
	}

	@Test
	void extensionsOtherSitesAndJunkAreIgnored() throws Exception {
		String extension = """
				[{"type": "csp-violation", "body": {"documentURL": "https://onehintaway.com/",
				  "blockedURL": "chrome-extension://abcdef/content.js", "effectiveDirective": "script-src-elem"}},
				 {"type": "csp-violation", "body": {"documentURL": "https://onehintaway.com/", "blockedURL": "inline",
				  "effectiveDirective": "script-src-elem", "sourceFile": "moz-extension://1234/inject.js"}}]
				""";
		String otherSite = """
				{"csp-report": {"document-uri": "https://evil.example/", "blocked-uri": "inline",
				                "effective-directive": "script-src-elem"}}
				""";
		send("application/reports+json", extension).andExpect(status().isNoContent());
		send("application/csp-report", otherSite).andExpect(status().isNoContent());
		send("application/json", "not json at all").andExpect(status().isNoContent());
		send("application/json", "{\"csp-report\": {\"document-uri\": \"https://onehintaway.com/\","
				+ " \"effective-directive\": \"<script>\"}}").andExpect(status().isNoContent());

		assertThat(rows()).isEmpty();
	}

	@Test
	void anyOriginMaySendAReportEvenNull() throws Exception {
		send("application/csp-report", CSP_REPORT, "null").andExpect(status().isNoContent());
		this.mvc
			.perform(options("/api/v1/csp-report").header(HttpHeaders.ORIGIN, "https://onehintaway.com")
				.header(HttpHeaders.ACCESS_CONTROL_REQUEST_METHOD, "POST")
				.header(HttpHeaders.ACCESS_CONTROL_REQUEST_HEADERS, "content-type"))
			.andExpect(status().isOk())
			.andExpect(header().exists(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN));
		assertThat(rows()).hasSize(1);
	}

	@Test
	void oneAddressCanSendTwentyReportsAMinute() throws Exception {
		for (int i = 0; i < 20; i++) {
			send("application/csp-report", CSP_REPORT).andExpect(status().isNoContent());
		}
		send("application/csp-report", CSP_REPORT).andExpect(status().isTooManyRequests());
		assertThat(rows().get(0).get("count")).isEqualTo(20L);
	}

	private ResultActions send(String type, String body) throws Exception {
		return send(type, body, "https://onehintaway.com");
	}

	private ResultActions send(String type, String body, String origin) throws Exception {
		String from = this.address;
		return this.mvc.perform(post("/api/v1/csp-report").header(HttpHeaders.ORIGIN, origin)
			.header(HttpHeaders.CONTENT_TYPE, type)
			.content(body)
			.with((r) -> {
				r.setRemoteAddr(from);
				return r;
			}));
	}

	private List<Map<String, Object>> rows() {
		return this.jdbc.sql("select directive, blocked, page, count from csp_reports")
			.query((rs, n) -> Map.<String, Object>of("directive", rs.getString(1), "blocked", rs.getString(2), "page",
					rs.getString(3), "count", rs.getLong(4)))
			.list();
	}

}

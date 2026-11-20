package com.onehintaway.api.reports;

import java.net.URI;
import java.sql.Timestamp;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

import com.onehintaway.api.config.AppProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * Where readers' browsers report Content-Security-Policy violations.
 *
 * <p>The site's policy first runs in report-only mode: browsers block nothing, they only send
 * a note here for everything the policy would have blocked. Once the counts show the policy
 * is right, it is switched to enforcing (site/scripts/write-headers.mjs) and keeps reporting.
 *
 * <p>Browsers send two formats: the older {@code report-uri} one ({@code application/csp-report},
 * one {@code {"csp-report": {...}}}) and the Reporting API's ({@code application/reports+json},
 * a list of {@code {"type": "csp-violation", "body": {...}}}). Both end up as counted rows in
 * {@code csp_reports}. Always 204: a browser does nothing with the answer.
 *
 * <p>Noise is dropped: reports about pages that aren't the site's, and reports caused by
 * browser extensions (their scripts and styles trip every site's policy).
 */
@RestController
class CspReportController {

	private static final Logger log = LoggerFactory.getLogger(CspReportController.class);

	/** Bigger bodies are not reports. */
	private static final int MAX_BODY = 64 * 1024;

	/** At most this many distinct rows; after that, only existing rows are counted. */
	private static final int MAX_ROWS = 2000;

	private static final Pattern DIRECTIVE = Pattern.compile("[a-z-]{3,40}");

	private static final Set<String> KEYWORDS = Set.of("inline", "eval", "data", "blob", "self", "wasm-eval",
			"trusted-types-policy", "trusted-types-sink");

	private static final List<String> EXTENSIONS = List.of("chrome-extension", "moz-extension",
			"safari-web-extension", "safari-extension", "ms-browser-extension");

	private final JdbcClient jdbc;

	private final JsonMapper json;

	private final Clock clock;

	private final List<String> siteOrigins;

	CspReportController(JdbcClient jdbc, JsonMapper json, Clock clock, AppProperties props) {
		this.jdbc = jdbc;
		this.json = json;
		this.clock = clock;
		this.siteOrigins = props.corsOrigins().stream().map((o) -> o.replaceAll("/+$", "")).toList();
	}

	@PostMapping(path = "/api/v1/csp-report")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void report(@RequestBody(required = false) String body) {
		if (body == null || body.length() > MAX_BODY) {
			return;
		}
		for (Violation v : parse(body)) {
			save(v);
		}
	}

	record Violation(String directive, String blocked, String page) {
	}

	/** Both formats, leniently: anything that doesn't look like a report is skipped. */
	List<Violation> parse(String body) {
		List<Violation> found = new ArrayList<>();
		JsonNode root;
		try {
			root = this.json.readTree(body);
		}
		catch (JacksonException ex) {
			return found;
		}
		if (root.isArray()) {
			for (JsonNode report : root) {
				if ("csp-violation".equals(report.path("type").asString(""))) {
					JsonNode b = report.path("body");
					add(found, b.path("effectiveDirective").asString(""), b.path("blockedURL").asString(""),
							b.path("documentURL").asString(""), b.path("sourceFile").asString(""));
				}
			}
		}
		else if (root.has("csp-report")) {
			JsonNode b = root.path("csp-report");
			String directive = b.path("effective-directive").asString("");
			if (directive.isEmpty()) {
				directive = b.path("violated-directive").asString("").split(" ")[0];
			}
			add(found, directive, b.path("blocked-uri").asString(""), b.path("document-uri").asString(""),
					b.path("source-file").asString(""));
		}
		return found;
	}

	private void add(List<Violation> found, String directive, String blocked, String document, String source) {
		String page = sitePath(document);
		if (page == null || !DIRECTIVE.matcher(directive).matches() || fromExtension(blocked)
				|| fromExtension(source)) {
			return;
		}
		found.add(new Violation(directive, cleanBlocked(blocked), page));
	}

	private static boolean fromExtension(String url) {
		String lower = url.toLowerCase(Locale.ROOT);
		return EXTENSIONS.stream().anyMatch(lower::startsWith);
	}

	/** The page's path, only when the page is on the site; null for anything else. */
	private String sitePath(String document) {
		try {
			URI uri = URI.create(document);
			String origin = uri.getScheme() + "://" + uri.getRawAuthority();
			if (!this.siteOrigins.contains(origin)) {
				return null;
			}
			String path = uri.getRawPath() == null || uri.getRawPath().isEmpty() ? "/" : uri.getRawPath();
			return truncate(path, 200);
		}
		catch (RuntimeException ex) {
			return null;
		}
	}

	/** An address without its query or fragment, or a keyword such as inline. */
	private static String cleanBlocked(String blocked) {
		String value = blocked.strip();
		if (value.isEmpty()) {
			return "inline";
		}
		if (KEYWORDS.contains(value)) {
			return value;
		}
		int cut = value.length();
		for (char c : new char[] { '?', '#' }) {
			int at = value.indexOf(c);
			if (at >= 0) {
				cut = Math.min(cut, at);
			}
		}
		return truncate(value.substring(0, cut), 300);
	}

	private static String truncate(String value, int max) {
		return value.length() <= max ? value : value.substring(0, max);
	}

	/** Counts one more of a known row, or adds the row while there is room. */
	private void save(Violation v) {
		Timestamp now = Timestamp.from(this.clock.instant());
		int updated = this.jdbc.sql("""
				update csp_reports set count = count + 1, last_seen = :now
				where directive = :directive and blocked = :blocked and page = :page
				""")
			.param("now", now)
			.param("directive", v.directive())
			.param("blocked", v.blocked())
			.param("page", v.page())
			.update();
		if (updated > 0) {
			return;
		}
		int inserted = this.jdbc.sql("""
				insert into csp_reports (directive, blocked, page, first_seen, last_seen)
				select :directive, :blocked, :page, :now, :now
				where (select count(*) from csp_reports) < :max
				on conflict (directive, blocked, page) do update
				  set count = csp_reports.count + 1, last_seen = excluded.last_seen
				""")
			.param("directive", v.directive())
			.param("blocked", v.blocked())
			.param("page", v.page())
			.param("now", now)
			.param("max", MAX_ROWS)
			.update();
		if (inserted > 0) {
			// A new kind of violation: worth a log line. Repeats are only counted.
			log.info("CSP report: {} would block {} on {}", v.directive(), v.blocked(), v.page());
		}
	}

}

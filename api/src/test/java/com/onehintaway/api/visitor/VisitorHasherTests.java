package com.onehintaway.api.visitor;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import com.onehintaway.api.config.AppProperties;
import org.junit.jupiter.api.Test;

import org.springframework.mock.web.MockHttpServletRequest;

import static org.assertj.core.api.Assertions.assertThat;

class VisitorHasherTests {

	private static VisitorHasher hasher(String salt, String instant) {
		AppProperties props = new AppProperties(List.of("https://onehintaway.com"), salt, "", "https://api.test", "https://onehintaway.com",
				new AppProperties.Rate(60, 5, 10, 10, 3), new AppProperties.Auth(true, ""), new AppProperties.Mail("", "test@example.com"));
		return new VisitorHasher(props, Clock.fixed(Instant.parse(instant), ZoneOffset.UTC));
	}

	private static MockHttpServletRequest request(String address, String browser) {
		MockHttpServletRequest request = new MockHttpServletRequest();
		request.setRemoteAddr(address);
		request.addHeader("User-Agent", browser);
		return request;
	}

	@Test
	void theSameVisitorOnTheSameDayGetsTheSameId() {
		VisitorHasher morning = hasher("salt", "2026-11-15T01:00:00Z");
		VisitorHasher evening = hasher("salt", "2026-11-15T23:00:00Z");
		String id = morning.visitor(request("203.0.113.5", "Firefox"));
		assertThat(id).matches("[0-9a-f]{64}").doesNotContain("203.0.113.5");
		assertThat(evening.visitor(request("203.0.113.5", "Firefox"))).isEqualTo(id);
	}

	@Test
	void theIdChangesWithTheDayTheAddressTheBrowserAndTheSalt() {
		String id = hasher("salt", "2026-11-15T12:00:00Z").visitor(request("203.0.113.5", "Firefox"));
		assertThat(hasher("salt", "2026-11-16T12:00:00Z").visitor(request("203.0.113.5", "Firefox"))).isNotEqualTo(id);
		assertThat(hasher("salt", "2026-11-15T12:00:00Z").visitor(request("203.0.113.6", "Firefox"))).isNotEqualTo(id);
		assertThat(hasher("salt", "2026-11-15T12:00:00Z").visitor(request("203.0.113.5", "Safari"))).isNotEqualTo(id);
		assertThat(hasher("other", "2026-11-15T12:00:00Z").visitor(request("203.0.113.5", "Firefox"))).isNotEqualTo(id);
	}

	@Test
	void theRateLimitKeyIgnoresTheBrowser() {
		VisitorHasher hasher = hasher("salt", "2026-11-15T12:00:00Z");
		assertThat(hasher.address(request("203.0.113.5", "Firefox")))
			.isEqualTo(hasher.address(request("203.0.113.5", "Safari")))
			.isNotEqualTo(hasher.address(request("203.0.113.6", "Firefox")));
	}

}

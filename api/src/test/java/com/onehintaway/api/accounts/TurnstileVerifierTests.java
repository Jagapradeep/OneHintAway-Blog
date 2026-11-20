package com.onehintaway.api.accounts;

import org.junit.jupiter.api.Test;

import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/** Checks the request Cloudflare would receive, against a fake server. */
class TurnstileVerifierTests {

	private static final String SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

	private final RestClient.Builder builder = RestClient.builder();

	private final MockRestServiceServer cloudflare = MockRestServiceServer.bindTo(this.builder).build();

	private final TurnstileVerifier verifier = new TurnstileVerifier(this.builder, "test-secret");

	@Test
	void aGenuineTokenPassesAndTheSecretTokenAndAddressAreSent() {
		this.cloudflare.expect(requestTo(SITEVERIFY))
			.andExpect(method(HttpMethod.POST))
			.andExpect(content().formDataContains(
					java.util.Map.of("secret", "test-secret", "response", "tok-1", "remoteip", "203.0.113.7")))
			.andRespond(withSuccess("{\"success\": true, \"error-codes\": []}", MediaType.APPLICATION_JSON));

		assertThat(this.verifier.passed("tok-1", "203.0.113.7")).isTrue();
		this.cloudflare.verify();
	}

	@Test
	void aTokenCloudflareRefusesFails() {
		this.cloudflare.expect(requestTo(SITEVERIFY))
			.andRespond(withSuccess("{\"success\": false, \"error-codes\": [\"timeout-or-duplicate\"]}",
					MediaType.APPLICATION_JSON));

		assertThat(this.verifier.passed("used-token", "203.0.113.7")).isFalse();
		this.cloudflare.verify();
	}

	@Test
	void aMissingOrOversizedTokenFailsWithoutAskingCloudflare() {
		assertThat(this.verifier.passed(null, "203.0.113.7")).isFalse();
		assertThat(this.verifier.passed("  ", "203.0.113.7")).isFalse();
		assertThat(this.verifier.passed("x".repeat(2049), "203.0.113.7")).isFalse();
		this.cloudflare.verify(); // no request was expected, and none was made
	}

	@Test
	void whenCloudflareCantBeAskedNoCodeIsSent() {
		this.cloudflare.expect(requestTo(SITEVERIFY)).andRespond(withStatus(HttpStatus.BAD_GATEWAY));

		assertThatThrownBy(() -> this.verifier.passed("tok-1", "203.0.113.7"))
			.isInstanceOfSatisfying(ResponseStatusException.class,
					(ex) -> assertThat(ex.getStatusCode()).isEqualTo(HttpStatus.SERVICE_UNAVAILABLE));
	}

}

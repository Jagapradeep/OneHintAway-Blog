package com.onehintaway.api.accounts;

import java.time.Duration;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

/**
 * Asks Cloudflare whether a Turnstile token is genuine (the "siteverify" call).
 *
 * <p>A token is made by the widget in the reader's browser, works once and for five
 * minutes. Only the server can check it, with the secret key, which never leaves the API.
 * Which domains may use the widget is set on the widget in Cloudflare's dashboard.
 *
 * <p>If Cloudflare can't be reached, the answer is 503 and no code is sent (fail closed):
 * otherwise a Cloudflare outage would switch the protection off.
 */
class TurnstileVerifier implements HumanCheck {

	private static final Logger log = LoggerFactory.getLogger(TurnstileVerifier.class);

	/** Cloudflare's limit for a token. Anything longer isn't one, so Cloudflare isn't asked. */
	private static final int MAX_TOKEN = 2048;

	private final RestClient client;

	private final String secret;

	TurnstileVerifier(RestClient.Builder builder, String secret) {
		this.client = builder.baseUrl("https://challenges.cloudflare.com").build();
		this.secret = secret;
	}

	/** Short timeouts: a slow check must not hold a reader's request for long. */
	static RestClient.Builder defaultBuilder() {
		SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
		factory.setConnectTimeout(Duration.ofSeconds(3));
		factory.setReadTimeout(Duration.ofSeconds(5));
		return RestClient.builder().requestFactory(factory);
	}

	@Override
	public boolean passed(String token, String ip) {
		if (token == null || token.isBlank() || token.length() > MAX_TOKEN) {
			return false;
		}
		MultiValueMap<String, String> form = new LinkedMultiValueMap<>();
		form.add("secret", this.secret);
		form.add("response", token);
		if (ip != null && !ip.isBlank()) {
			form.add("remoteip", ip);
		}
		Answer answer;
		try {
			answer = this.client.post()
				.uri("/turnstile/v0/siteverify")
				.contentType(MediaType.APPLICATION_FORM_URLENCODED)
				.body(form)
				.retrieve()
				.body(Answer.class);
		}
		catch (RestClientException ex) {
			// The message names the address and the status, never the secret.
			log.warn("Turnstile check failed: {}", ex.getMessage());
			throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Sign-in is not available right now");
		}
		if (answer == null || !answer.success()) {
			log.info("Turnstile refused a token: {}", answer == null ? "no answer" : answer.errorCodes());
			return false;
		}
		return true;
	}

	/** The part of Cloudflare's answer that is used. */
	record Answer(boolean success, @JsonProperty("error-codes") List<String> errorCodes) {
	}

}

package com.onehintaway.api.subscribers;

import java.time.Duration;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

/**
 * Sends the confirmation email through Resend's HTTP API (one POST per email).
 *
 * <p>If Resend can't be reached or refuses the email, the sign-up fails with 503 and its
 * database row is rolled back, so a reader is never left "pending" with no email on the
 * way; they can simply try again. The API key is sent as a header and never logged.
 */
class ResendMailSender implements MailSender {

	private static final Logger log = LoggerFactory.getLogger(ResendMailSender.class);

	private final RestClient client;

	private final String from;

	ResendMailSender(RestClient.Builder builder, String apiKey, String from) {
		this.client = builder.baseUrl("https://api.resend.com")
			.defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + apiKey)
			.build();
		this.from = from;
	}

	/** Short timeouts: a slow email provider must not hold a request, and its database connection, for long. */
	static RestClient.Builder defaultBuilder() {
		SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
		factory.setConnectTimeout(Duration.ofSeconds(3));
		factory.setReadTimeout(Duration.ofSeconds(5));
		return RestClient.builder().requestFactory(factory);
	}

	@Override
	public void sendConfirmation(String email, String confirmUrl) {
		String text = """
				Thanks for signing up to One Hint Away.

				Open this link to confirm your address:
				%s

				If you didn't ask for this, ignore this email and you won't hear from us again.
				""".formatted(confirmUrl);
		try {
			this.client.post()
				.uri("/emails")
				.contentType(MediaType.APPLICATION_JSON)
				.body(Map.of("from", this.from, "to", List.of(email), "subject",
						"Confirm your One Hint Away subscription", "text", text))
				.retrieve()
				.toBodilessEntity();
		}
		catch (RestClientException ex) {
			log.warn("Resend did not accept a confirmation email: {}", ex.getMessage());
			throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Could not send the confirmation email");
		}
	}

}

package com.onehintaway.api.subscribers;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.util.HtmlUtils;

/**
 * Sends the confirmation and sign-in emails through Resend's HTTP API (one POST per email).
 *
 * <p>If Resend can't be reached or refuses the email, the sign-up fails with 503 and its
 * database row is rolled back, so a reader is never left "pending" with no email on the
 * way; they can simply try again. The API key is sent as a header and never logged.
 */
class ResendMailSender implements MailSender {

	private static final Logger log = LoggerFactory.getLogger(ResendMailSender.class);

	/** The HTML email, read once. {{confirmUrl}} is the only placeholder. */
	private static final String HTML_TEMPLATE = readTemplate("mail/confirmation.html");

	/** The sign-in email; see the comment at the top of the file for its placeholders. */
	private static final String SIGN_IN_TEMPLATE = readTemplate("mail/sign-in.html");

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
		// The link goes into attributes and text, so it is HTML-escaped. Mail apps that
		// don't show HTML use the plain text above.
		String html = HTML_TEMPLATE.replace("{{confirmUrl}}", HtmlUtils.htmlEscape(confirmUrl));
		send(email, "You're one click away", html, text, "a confirmation email");
	}

	@Override
	public void sendSignInLink(String email, String url, boolean forDelete) {
		String heading = forDelete ? "Delete your account?" : "Your sign-in link";
		String lead = forDelete
				? "You asked to delete your One Hint Away account. Open the link below to continue. Nothing is deleted until you confirm on the page that opens."
				: "Open the link below to sign in to One Hint Away. If this is your first time, it also creates your account. There is no password.";
		String button = forDelete ? "Continue" : "Sign in";
		String note = forDelete
				? "Didn't ask for this? Ignore this email: your account stays as it is."
				: "You got this because someone entered this address at onehintaway.com. Not you? Ignore this email: nobody can sign in without the link.";
		String text = """
				%s

				%s

				%s

				The link works once and for 15 minutes.

				%s
				""".formatted(heading, lead, url, note);
		String html = SIGN_IN_TEMPLATE.replace("{{url}}", HtmlUtils.htmlEscape(url))
			.replace("{{preheader}}", forDelete ? "Continue to delete your account." : "Your link to sign in. It works for 15 minutes.")
			.replace("{{eyebrow}}", forDelete ? "ACCOUNT" : "SIGN IN")
			.replace("{{heading}}", heading)
			.replace("{{lead}}", HtmlUtils.htmlEscape(lead))
			.replace("{{button}}", button)
			.replace("{{note}}", HtmlUtils.htmlEscape(note));
		send(email, forDelete ? "Delete your One Hint Away account" : "Your One Hint Away sign-in link", html, text,
				"a sign-in email");
	}

	private void send(String email, String subject, String html, String text, String what) {
		try {
			this.client.post()
				.uri("/emails")
				.contentType(MediaType.APPLICATION_JSON)
				.body(Map.of("from", this.from, "to", List.of(email), "subject", subject, "html", html, "text", text))
				.retrieve()
				.toBodilessEntity();
		}
		catch (RestClientException ex) {
			log.warn("Resend did not accept {}: {}", what, ex.getMessage());
			throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Could not send the email");
		}
	}

	private static String readTemplate(String path) {
		try {
			return new ClassPathResource(path).getContentAsString(StandardCharsets.UTF_8);
		}
		catch (IOException ex) {
			throw new UncheckedIOException(path + " is missing from the jar", ex);
		}
	}

}

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
	private static final String CODE_TEMPLATE = readTemplate("mail/code.html");

	private static final String NOTICE_TEMPLATE = readTemplate("mail/notice.html");

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
				Get new patterns by email?

				Open this link to get one email each time a new pattern is posted on One Hint Away. Nothing else.
				%s

				Didn't ask for this? Ignore this email and you won't be added.
				""".formatted(confirmUrl);
		// The link goes into attributes and text, so it is HTML-escaped. Mail apps that
		// don't show HTML use the plain text above.
		String html = HTML_TEMPLATE.replace("{{confirmUrl}}", HtmlUtils.htmlEscape(confirmUrl));
		send(email, "Confirm your One Hint Away subscription", html, text, "a confirmation email");
	}

	@Override
	public void sendSignInCode(String email, String code, boolean forDelete) {
		String heading = forDelete ? "Your code to delete your account" : "Your sign-in code";
		String lead = forDelete
				? "Type this code on One Hint Away to continue. Nothing is deleted until you confirm on the next screen."
				: "Type this code on One Hint Away to sign in. If this is your first time, it also creates your account.";
		String note = forDelete
				? "Didn't ask for this? Ignore this email: your account stays as it is."
				: "You got this because someone entered this address at onehintaway.com. Not you? Ignore this email: nobody can sign in without the code.";
		String text = """
				%s

				%s

				%s

				It works once and for 15 minutes.

				%s
				""".formatted(heading, lead, code, note);
		String html = CODE_TEMPLATE.replace("{{code}}", code)
			.replace("{{preheader}}", code + " is your code. It works for 15 minutes.")
			.replace("{{eyebrow}}", forDelete ? "ACCOUNT" : "SIGN IN")
			.replace("{{heading}}", heading)
			.replace("{{lead}}", HtmlUtils.htmlEscape(lead))
			.replace("{{small}}", "It works once and for 15 minutes.")
			.replace("{{note}}", HtmlUtils.htmlEscape(note));
		send(email, forDelete ? code + " is your code to delete your account" : code + " is your One Hint Away sign-in code", html,
				text, "a sign-in email");
	}

	@Override
	public void sendAlreadySubscribed(String email, String unsubscribeUrl) {
		String heading = "You're already subscribed";
		String lead = "Someone, probably you, asked to get new patterns at this address. It already gets them: there is nothing to do. Want to stop? Tap Unsubscribe.";
		String note = "Want to keep getting them? Ignore this email: nothing changes.";
		String text = """
				%s

				%s

				Unsubscribe: %s

				%s
				""".formatted(heading, lead, unsubscribeUrl, note);
		String html = NOTICE_TEMPLATE.replace("{{url}}", HtmlUtils.htmlEscape(unsubscribeUrl))
			.replace("{{preheader}}", "This address already gets new patterns. Nothing to do.")
			.replace("{{eyebrow}}", "NEW PATTERNS BY EMAIL")
			.replace("{{heading}}", heading)
			.replace("{{lead}}", HtmlUtils.htmlEscape(lead))
			.replace("{{button}}", "Unsubscribe")
			.replace("{{small}}", "One tap takes this address off the list.")
			.replace("{{note}}", HtmlUtils.htmlEscape(note));
		send(email, "You're already subscribed to One Hint Away", html, text, "an already-subscribed email");
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

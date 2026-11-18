package com.onehintaway.api.subscribers;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.Test;

import org.springframework.http.MediaType;
import org.springframework.mock.http.client.MockClientHttpRequest;
import org.springframework.test.web.client.ExpectedCount;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Writes every email exactly as the API would send it to {@code target/mail-preview/}, with the
 * logo pointed at {@code site/public/} so it shows before the site is deployed. Open the files in
 * a browser: {@code ./mvnw -q test -Dtest=MailPreviewTests}. No email is sent.
 */
class MailPreviewTests {

	private static final String LIVE_LOGO = "https://onehintaway.com/email-brand.png";

	@Test
	void writesEveryEmailForPreview() throws IOException {
		RestClient.Builder builder = RestClient.builder();
		MockRestServiceServer resend = MockRestServiceServer.bindTo(builder).build();
		List<String> bodies = new ArrayList<>();
		resend.expect(ExpectedCount.manyTimes(), request -> bodies.add(((MockClientHttpRequest) request).getBodyAsString()))
			.andRespond(withSuccess("{\"id\": \"1\"}", MediaType.APPLICATION_JSON));
		ResendMailSender sender = new ResendMailSender(builder, "preview", "One Hint Away <hello@onehintaway.com>");

		sender.sendSignInCode("reader@example.com", "042917", false);
		sender.sendSignInCode("reader@example.com", "042917", true);
		sender.sendConfirmation("reader@example.com", "https://api.onehintaway.com/api/v1/subscribers/confirm?token=preview");
		sender.sendAlreadySubscribed("reader@example.com", "https://onehintaway.com/unsubscribe/#token=preview");

		Path dir = Path.of("target", "mail-preview");
		Files.createDirectories(dir);
		String logo = Path.of("..", "site", "public", "email-brand.png").toAbsolutePath().normalize().toUri().toString();
		String[] names = { "sign-in-code", "delete-code", "confirmation", "already-subscribed" };
		assertThat(bodies).hasSize(names.length);
		for (int i = 0; i < names.length; i++) {
			String html = JsonPath.read(bodies.get(i), "$.html");
			assertThat(html).contains(LIVE_LOGO).doesNotContain("{{");
			Files.writeString(dir.resolve(names[i] + ".html"), html.replace(LIVE_LOGO, logo));
		}
	}

}

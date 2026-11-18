package com.onehintaway.api.subscribers;

import org.junit.jupiter.api.Test;

import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.jsonPath;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/** Checks the request Resend would receive, against a fake server: no email is sent. */
class ResendMailSenderTests {

	private final RestClient.Builder builder = RestClient.builder();

	private final MockRestServiceServer resend = MockRestServiceServer.bindTo(this.builder).build();

	private final ResendMailSender sender = new ResendMailSender(this.builder, "test-key",
			"One Hint Away <hello@onehintaway.com>");

	@Test
	void sendsOneEmailWithTheLinkAndTheKeyInTheHeader() {
		this.resend.expect(requestTo("https://api.resend.com/emails"))
			.andExpect(method(HttpMethod.POST))
			.andExpect(header("Authorization", "Bearer test-key"))
			.andExpect(jsonPath("$.from").value("One Hint Away <hello@onehintaway.com>"))
			.andExpect(jsonPath("$.to[0]").value("reader@example.com"))
			.andExpect(jsonPath("$.text", containsString("https://api.test/confirm?token=abc")))
			.andExpect(jsonPath("$.subject").value("Confirm your One Hint Away subscription"))
			.andExpect(jsonPath("$.html", containsString("Yes, subscribe me")))
			.andExpect(jsonPath("$.html", containsString("href=\"https://api.test/confirm?token=abc\"")))
			.andExpect(jsonPath("$.html", not(containsString("{{confirmUrl}}"))))
			.andRespond(withSuccess("{\"id\": \"1\"}", MediaType.APPLICATION_JSON));

		this.sender.sendConfirmation("reader@example.com", "https://api.test/confirm?token=abc");
		this.resend.verify();
	}

	@Test
	void theSignInEmailCarriesTheLinkAndPlainWords() {
		String url = "https://onehintaway.com/sign-in/#token=abc&for=delete";
		this.resend.expect(requestTo("https://api.resend.com/emails"))
			.andExpect(jsonPath("$.to[0]").value("reader@example.com"))
			.andExpect(jsonPath("$.subject").value("Delete your One Hint Away account"))
			.andExpect(jsonPath("$.text", containsString(url)))
			.andExpect(jsonPath("$.html", containsString("href=\"https://onehintaway.com/sign-in/#token=abc&amp;for=delete\"")))
			.andExpect(jsonPath("$.html", not(containsString("{{"))))
			.andRespond(withSuccess("{\"id\": \"1\"}", MediaType.APPLICATION_JSON));
		this.resend.expect(requestTo("https://api.resend.com/emails"))
			.andExpect(jsonPath("$.subject").value("Your One Hint Away sign-in link"))
			.andExpect(jsonPath("$.html", containsString("There is no password.")))
			.andExpect(jsonPath("$.html", not(containsString("{{"))))
			.andRespond(withSuccess("{\"id\": \"2\"}", MediaType.APPLICATION_JSON));

		this.sender.sendSignInLink("reader@example.com", url, true);
		this.sender.sendSignInLink("reader@example.com", "https://onehintaway.com/sign-in/#token=abc", false);
		this.resend.verify();
	}

	@Test
	void aRefusalFromResendBecomesA503() {
		this.resend.expect(requestTo("https://api.resend.com/emails")).andRespond(withStatus(HttpStatus.FORBIDDEN));

		assertThatThrownBy(() -> this.sender.sendConfirmation("reader@example.com", "https://api.test/x"))
			.isInstanceOf(ResponseStatusException.class)
			.hasMessageContaining("503");
	}

}

package com.onehintaway.api.config;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

/**
 * Everything under {@code app.} in application.properties. The app refuses to start
 * when a required value is missing, so a missing salt is caught at boot, not at the first request.
 *
 * @param corsOrigins the site addresses whose pages may call the API from a browser
 * @param visitorSalt secret mixed into visitor hashes; without it hashes could be reversed by guessing addresses
 * @param adminToken secret for the posts sync; blank switches the sync off
 * @param publicUrl the API's own public address, used in confirmation links
 * @param siteUrl the site's address; a reader who opens a confirmation link is sent to a page there
 * @param auth sign-in settings
 * @param mail who emails come from, and the Resend key; a blank key means emails go to the log
 */
@ConfigurationProperties("app")
@Validated
public record AppProperties(
		@NotEmpty List<String> corsOrigins,
		@NotBlank String visitorSalt,
		String adminToken,
		@NotBlank String publicUrl,
		@NotBlank String siteUrl,
		@NotNull @Valid Rate rate,
		@NotNull @Valid Auth auth,
		@NotNull @Valid Mail mail) {

	public record Mail(String resendApiKey, @NotBlank String from) {
	}

	/**
	 * @param cookieSecure false only for plain-http local runs in browsers that refuse Secure cookies there
	 * @param turnstileSecret Cloudflare Turnstile secret key; blank switches the human check off (laptop, tests)
	 */
	public record Auth(boolean cookieSecure, String turnstileSecret) {
	}

	/**
	 * @param linkPerHour sign-in links one address (IP) may ask for in an hour
	 * @param linkPerEmailPerHour sign-in links one email address is sent in an hour
	 */
	public record Rate(@Min(1) int countPerMinute, @Min(1) int subscribePerHour, @Min(1) int adminPerMinute,
			@Min(1) int linkPerHour, @Min(1) int linkPerEmailPerHour) {
	}

}

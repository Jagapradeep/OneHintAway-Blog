package com.onehintaway.api.subscribers;

import java.net.URI;

import com.onehintaway.api.accounts.SessionCookie;
import com.onehintaway.api.config.AppProperties;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/subscribers")
class SubscriberController {

	private final SubscriberService service;

	private final String siteUrl;

	private final SessionCookie cookie;

	SubscriberController(SubscriberService service, SessionCookie cookie, AppProperties props) {
		this.service = service;
		this.cookie = cookie;
		this.siteUrl = props.siteUrl().replaceAll("/+$", "");
	}

	record SignUp(@NotBlank @Email @Size(max = 254) String email) {
	}

	record Status(boolean subscribed) {
	}

	record Unsubscribe(@NotBlank @Pattern(regexp = "[A-Za-z0-9_-]{43}") String token) {
	}

	/** 202: the request is taken, but the subscription only exists once the email link is opened. */
	@PostMapping
	@ResponseStatus(HttpStatus.ACCEPTED)
	void subscribe(@RequestBody @Valid SignUp signUp) {
		this.service.subscribe(signUp.email());
	}

	/**
	 * The link in the confirmation email. A GET, because it is opened from an email client.
	 * A person is looking at the answer, so it is a redirect to a page on the site: the
	 * welcome page when the token is good, a "that link didn't work" page when it is not.
	 */
	@GetMapping("/confirm")
	ResponseEntity<Void> confirm(@RequestParam @NotBlank @Size(max = 100) String token) {
		String page = this.service.confirm(token) ? "/subscribed/" : "/subscribed/expired/";
		return ResponseEntity.status(HttpStatus.SEE_OTHER).location(URI.create(this.siteUrl + page)).build();
	}

	// A signed-in reader manages their own address in one click: it was proven by the
	// sign-in link, so there is no confirmation email. Account paths: cookie + CSRF check.

	@GetMapping("/me")
	Status mine(HttpServletRequest request, HttpServletResponse response) {
		return new Status(this.service.isSubscribed(this.cookie.require(request, response).email()));
	}

	@PutMapping("/me")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void subscribeMe(HttpServletRequest request, HttpServletResponse response) {
		this.service.subscribeVerified(this.cookie.require(request, response).email());
	}

	@DeleteMapping("/me")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void unsubscribeMe(HttpServletRequest request, HttpServletResponse response) {
		this.service.unsubscribe(this.cookie.require(request, response).email());
	}

	/**
	 * The unsubscribe link in an email opens a page on the site, which posts the token here
	 * (a POST, so a mail scanner opening the link does not unsubscribe anyone). Always 204:
	 * an unknown or already used token means the address is not on the list either way.
	 */
	@PostMapping("/unsubscribe")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void unsubscribe(@RequestBody @Valid Unsubscribe body) {
		this.service.unsubscribeByToken(body.token());
	}

}

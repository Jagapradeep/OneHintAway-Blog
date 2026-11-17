package com.onehintaway.api.subscribers;

import java.net.URI;

import com.onehintaway.api.config.AppProperties;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
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

	SubscriberController(SubscriberService service, AppProperties props) {
		this.service = service;
		this.siteUrl = props.siteUrl().replaceAll("/+$", "");
	}

	record SignUp(@NotBlank @Email @Size(max = 254) String email) {
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

}

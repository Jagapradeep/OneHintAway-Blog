package com.onehintaway.api.subscribers;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/v1/subscribers")
class SubscriberController {

	private final SubscriberService service;

	SubscriberController(SubscriberService service) {
		this.service = service;
	}

	record SignUp(@NotBlank @Email @Size(max = 254) String email) {
	}

	/** 202: the request is taken, but the subscription only exists once the email link is opened. */
	@PostMapping
	@ResponseStatus(HttpStatus.ACCEPTED)
	void subscribe(@RequestBody @Valid SignUp signUp) {
		this.service.subscribe(signUp.email());
	}

	/** The link in the confirmation email. A GET, because it is opened from an email client. */
	@GetMapping(value = "/confirm", produces = MediaType.TEXT_PLAIN_VALUE)
	String confirm(@RequestParam @NotBlank @Size(max = 100) String token) {
		if (!this.service.confirm(token)) {
			throw new ResponseStatusException(HttpStatus.NOT_FOUND, "This link is not valid");
		}
		return "You're subscribed to One Hint Away.";
	}

}

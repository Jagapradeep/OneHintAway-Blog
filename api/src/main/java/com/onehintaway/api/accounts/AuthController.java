package com.onehintaway.api.accounts;

import com.onehintaway.api.accounts.AccountService.Purpose;
import com.onehintaway.api.accounts.AccountService.Session;
import com.onehintaway.api.accounts.AccountService.SignedIn;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * Register and sign in (one flow), sign out, and delete the account.
 *
 * <p>There is no GET that signs anyone in. The emailed link opens a page on the site;
 * only that page's button POSTs the token here. Mail scanners and link previewers open
 * links with GET, so they can neither use the link up nor sign anyone in.
 */
@RestController
@RequestMapping("/api/v1/auth")
class AuthController {

	private final AccountService accounts;

	private final SessionCookie cookie;

	AuthController(AccountService accounts, SessionCookie cookie) {
		this.accounts = accounts;
		this.cookie = cookie;
	}

	/** {@code purpose} is "delete" when a signed-in reader asks for the code that allows deleting the account. */
	record CodeRequest(@Email @Size(max = 254) String email, @Pattern(regexp = "delete") String purpose) {
	}

	record CodeAnswer(@NotBlank @Email @Size(max = 254) String email, @NotBlank @Pattern(regexp = "[0-9]{6}") String code) {
	}

	record Me(String email) {
	}

	record SignedInAnswer(String email, String purpose) {
	}

	/**
	 * Always 202 for a well-formed address, known or not. The delete code goes only to the
	 * signed-in reader's own address, so it can't be used to send alarming email to others.
	 */
	@PostMapping("/code")
	@ResponseStatus(HttpStatus.ACCEPTED)
	void code(@RequestBody @Valid CodeRequest body, HttpServletRequest request, HttpServletResponse response) {
		if (body.purpose() != null) {
			this.accounts.sendCode(this.cookie.require(request, response).email(), Purpose.DELETE_ACCOUNT);
			return;
		}
		if (body.email() == null || body.email().isBlank()) {
			throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "An email address is needed");
		}
		this.accounts.sendCode(body.email(), Purpose.SIGN_IN);
	}

	/** Trades an emailed code for a session cookie. One answer for wrong, expired, used and dead codes. */
	@PostMapping("/session")
	SignedInAnswer exchange(@RequestBody @Valid CodeAnswer body, HttpServletResponse response) {
		response.setHeader("Cache-Control", "no-store");
		SignedIn signedIn = this.accounts.exchange(body.email(), body.code()).signedIn();
		if (signedIn == null) {
			throw new ResponseStatusException(HttpStatus.GONE, "This code is wrong, expired or already used");
		}
		this.cookie.set(response, signedIn.sessionToken());
		return new SignedInAnswer(signedIn.email(), signedIn.purpose() == Purpose.DELETE_ACCOUNT ? "delete" : "sign-in");
	}

	@GetMapping("/me")
	Me me(HttpServletRequest request, HttpServletResponse response) {
		return new Me(this.cookie.require(request, response).email());
	}

	/** 204 even when nobody was signed in: the result is the same. */
	@PostMapping("/sign-out")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void signOut(HttpServletRequest request, HttpServletResponse response) {
		this.cookie.current(request, response).ifPresent(this.accounts::signOut);
		this.cookie.clear(response);
	}

	@PostMapping("/sign-out-everywhere")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void signOutEverywhere(HttpServletRequest request, HttpServletResponse response) {
		this.accounts.signOutEverywhere(this.cookie.require(request, response));
		this.cookie.clear(response);
	}

	/**
	 * Removes the user, every session and all progress. Only for a session that began in
	 * the last few minutes, that is, right after a fresh emailed link: a browser left
	 * signed in on a shared computer can't be used to delete the account.
	 */
	@DeleteMapping("/account")
	@ResponseStatus(HttpStatus.NO_CONTENT)
	void deleteAccount(HttpServletRequest request, HttpServletResponse response) {
		Session session = this.cookie.require(request, response);
		if (!this.accounts.isFresh(session)) {
			throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Open a fresh sign-in link first");
		}
		this.accounts.deleteAccount(session);
		this.cookie.clear(response);
	}

}

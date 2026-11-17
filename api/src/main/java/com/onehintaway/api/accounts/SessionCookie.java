package com.onehintaway.api.accounts;

import java.time.Duration;
import java.util.Optional;

import com.onehintaway.api.accounts.AccountService.Session;
import com.onehintaway.api.config.AppProperties;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;

/**
 * The session cookie: reading it, setting it and clearing it.
 *
 * <p>HttpOnly (page scripts can't read it), Secure (HTTPS only), SameSite=Lax (other
 * sites' requests don't carry it, except a plain link click, which changes nothing here).
 * With Secure on, the name starts with {@code __Host-}: the browser then refuses any
 * cookie of that name that a sister address (such as stats.onehintaway.com) tries to set.
 */
@Component
public class SessionCookie {

	private final AccountService accounts;

	private final boolean secure;

	private final String name;

	SessionCookie(AccountService accounts, AppProperties props) {
		this.accounts = accounts;
		this.secure = props.auth().cookieSecure();
		this.name = this.secure ? "__Host-ohw_session" : "ohw_session";
	}

	/** The signed-in reader, if any. Sends the cookie again when the session's end date moved. */
	public Optional<Session> current(HttpServletRequest request, HttpServletResponse response) {
		response.setHeader(HttpHeaders.CACHE_CONTROL, "no-store");
		Cookie[] cookies = request.getCookies();
		if (cookies == null) {
			return Optional.empty();
		}
		for (Cookie cookie : cookies) {
			if (cookie.getName().equals(this.name)) {
				Optional<Session> session = this.accounts.find(cookie.getValue());
				if (session.isPresent() && session.get().renewed()) {
					set(response, cookie.getValue());
				}
				return session;
			}
		}
		return Optional.empty();
	}

	/** The signed-in reader, or 401. */
	public Session require(HttpServletRequest request, HttpServletResponse response) {
		return current(request, response)
			.orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not signed in"));
	}

	void set(HttpServletResponse response, String token) {
		write(response, token, AccountService.SESSION_LIFE);
	}

	void clear(HttpServletResponse response) {
		write(response, "", Duration.ZERO);
	}

	private void write(HttpServletResponse response, String value, Duration maxAge) {
		response.addHeader(HttpHeaders.SET_COOKIE,
				ResponseCookie.from(this.name, value)
					.httpOnly(true)
					.secure(this.secure)
					.sameSite("Lax")
					.path("/")
					.maxAge(maxAge)
					.build()
					.toString());
	}

}

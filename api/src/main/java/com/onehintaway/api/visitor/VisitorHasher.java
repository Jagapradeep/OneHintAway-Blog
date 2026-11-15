package com.onehintaway.api.visitor;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.time.LocalDate;
import java.util.HexFormat;

import com.onehintaway.api.config.AppProperties;
import jakarta.servlet.http.HttpServletRequest;

import org.springframework.stereotype.Component;

/**
 * Turns a request into an id that cannot be traced back to a person. The raw address is
 * never stored or logged: only SHA-256 of (secret salt, today's date, address, browser).
 * The date is part of the hash, so the same reader gets a new id every day and visits
 * cannot be linked across days.
 */
@Component
public class VisitorHasher {

	private final String salt;

	private final Clock clock;

	public VisitorHasher(AppProperties props, Clock clock) {
		this.salt = props.visitorSalt();
		this.clock = clock;
	}

	public LocalDate today() {
		return LocalDate.now(this.clock);
	}

	/** Address plus browser: used to count one view per visitor per day. */
	public String visitor(HttpServletRequest request) {
		String agent = request.getHeader("User-Agent");
		return sha256(request.getRemoteAddr(), agent == null ? "" : agent);
	}

	/**
	 * Address only: used for rate limits. The browser name is left out because the
	 * caller chooses it, so a limit keyed on it could be dodged by changing it.
	 */
	public String address(HttpServletRequest request) {
		return sha256(request.getRemoteAddr(), "");
	}

	private String sha256(String address, String agent) {
		try {
			MessageDigest digest = MessageDigest.getInstance("SHA-256");
			String input = this.salt + '\n' + today() + '\n' + address + '\n' + agent;
			return HexFormat.of().formatHex(digest.digest(input.getBytes(StandardCharsets.UTF_8)));
		}
		catch (NoSuchAlgorithmException ex) {
			throw new IllegalStateException(ex);
		}
	}

}

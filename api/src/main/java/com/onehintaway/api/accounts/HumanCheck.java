package com.onehintaway.api.accounts;

/**
 * "Is a person asking, or a script?" Asked before a sign-in code is emailed, because every
 * code costs a real email: a script sending thousands would use up the email allowance and
 * stop real readers from getting codes.
 *
 * <p>In production this is Cloudflare Turnstile ({@link TurnstileVerifier}). With no secret
 * configured (your laptop, the tests) it is {@link #OFF}, which lets everything through.
 */
public interface HumanCheck {

	/** Lets every request through: used when no Turnstile secret is configured. */
	HumanCheck OFF = (token, ip) -> true;

	/**
	 * @param token what the Turnstile widget in the reader's browser produced; may be null
	 * @param ip the reader's address, passed on to Cloudflare as a hint
	 * @return true when the check passed
	 * @throws org.springframework.web.server.ResponseStatusException 503 when Cloudflare can't be asked
	 */
	boolean passed(String token, String ip);

}

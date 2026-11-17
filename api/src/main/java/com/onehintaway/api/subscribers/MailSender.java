package com.onehintaway.api.subscribers;

/**
 * Sends the "confirm your address" email and the sign-in link: through Resend when a key is set, to the log
 * otherwise (see MailConfig). The rest of the code only knows this interface.
 */
public interface MailSender {

	void sendConfirmation(String email, String confirmUrl);

	/** The sign-in link; {@code forDelete} is the one a reader asks for before deleting their account. */
	void sendSignInLink(String email, String url, boolean forDelete);

}

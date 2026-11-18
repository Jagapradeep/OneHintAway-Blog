package com.onehintaway.api.subscribers;

/**
 * Sends the "confirm your address" email and the sign-in code: through Resend when a key is set, to the log
 * otherwise (see MailConfig). The rest of the code only knows this interface.
 */
public interface MailSender {

	void sendConfirmation(String email, String confirmUrl);

	/** The sign-in code; {@code forDelete} is the one a reader asks for before deleting their account. */
	void sendSignInCode(String email, String code, boolean forDelete);

	/** Someone asked to subscribe an address that already is: tell its owner, with a way out. */
	void sendAlreadySubscribed(String email, String unsubscribeUrl);

}

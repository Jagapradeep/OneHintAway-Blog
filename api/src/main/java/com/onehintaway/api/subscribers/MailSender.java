package com.onehintaway.api.subscribers;

/**
 * Sends the "confirm your address" email: through Resend when a key is set, to the log
 * otherwise (see MailConfig). The rest of the code only knows this interface.
 */
public interface MailSender {

	void sendConfirmation(String email, String confirmUrl);

}

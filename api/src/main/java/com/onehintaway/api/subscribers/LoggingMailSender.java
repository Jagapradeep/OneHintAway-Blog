package com.onehintaway.api.subscribers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Used when no Resend key is set (local runs): prints the confirmation link instead of
 * sending it. It writes an email address to the log, so production must always have a key.
 */
class LoggingMailSender implements MailSender {

	private static final Logger log = LoggerFactory.getLogger(LoggingMailSender.class);

	@Override
	public void sendConfirmation(String email, String confirmUrl) {
		log.info("No RESEND_API_KEY set. Confirmation link for {}: {}", email, confirmUrl);
	}

}

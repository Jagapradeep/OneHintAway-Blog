package com.onehintaway.api.subscribers;

import com.onehintaway.api.config.AppProperties;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class MailConfig {

	/** With a Resend key, real email; without one (local runs), the link goes to the log. */
	@Bean
	MailSender mailSender(AppProperties props) {
		String key = props.mail().resendApiKey();
		if (key == null || key.isBlank()) {
			return new LoggingMailSender();
		}
		return new ResendMailSender(ResendMailSender.defaultBuilder(), key, props.mail().from());
	}

}

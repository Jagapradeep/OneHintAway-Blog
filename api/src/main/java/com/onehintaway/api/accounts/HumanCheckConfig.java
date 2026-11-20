package com.onehintaway.api.accounts;

import com.onehintaway.api.config.AppProperties;
import org.slf4j.LoggerFactory;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class HumanCheckConfig {

	/** With a Turnstile secret, Cloudflare checks every sign-in code request; without one, nothing does. */
	@Bean
	HumanCheck humanCheck(AppProperties props) {
		String secret = props.auth().turnstileSecret();
		if (secret == null || secret.isBlank()) {
			LoggerFactory.getLogger(HumanCheckConfig.class)
				.info("No TURNSTILE_SECRET_KEY: sign-in code requests are not checked for a person");
			return HumanCheck.OFF;
		}
		return new TurnstileVerifier(TurnstileVerifier.defaultBuilder(), secret.strip());
	}

}

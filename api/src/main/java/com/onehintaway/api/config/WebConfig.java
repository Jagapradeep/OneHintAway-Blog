package com.onehintaway.api.config;

import com.onehintaway.api.accounts.CsrfInterceptor;
import com.onehintaway.api.visitor.RateLimitInterceptor;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
class WebConfig implements WebMvcConfigurer {

	private static final String[] ACCOUNT_PATHS = { "/api/v1/auth/**", "/api/v1/progress/**" };

	private final AppProperties props;

	private final RateLimitInterceptor rateLimit;

	private final CsrfInterceptor csrf;

	WebConfig(AppProperties props, RateLimitInterceptor rateLimit, CsrfInterceptor csrf) {
		this.props = props;
		this.rateLimit = rateLimit;
		this.csrf = csrf;
	}

	/**
	 * Only the site's own pages may call the API from a browser. PUT is left out on purpose:
	 * the posts sync is called by a script, never by a page.
	 *
	 * <p>Accounts and progress are the only paths where the browser may send the session
	 * cookie (allowCredentials), and only to the exact site origins: never a wildcard. They
	 * are registered first, because the first matching pattern wins.
	 */
	@Override
	public void addCorsMappings(CorsRegistry registry) {
		String[] origins = this.props.corsOrigins().toArray(String[]::new);
		for (String path : ACCOUNT_PATHS) {
			registry.addMapping(path)
				.allowedOrigins(origins)
				.allowedMethods("GET", "POST", "PUT", "DELETE")
				.allowedHeaders("Content-Type", CsrfInterceptor.HEADER)
				.allowCredentials(true)
				.maxAge(3600);
		}
		registry.addMapping("/api/**")
			.allowedOrigins(this.props.corsOrigins().toArray(String[]::new))
			.allowedMethods("GET", "POST")
			.maxAge(3600);
	}

	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		// CSRF first: a refused request should not use up the caller's rate limit.
		registry.addInterceptor(this.csrf).addPathPatterns(ACCOUNT_PATHS);
		registry.addInterceptor(this.rateLimit).addPathPatterns("/api/v1/**");
	}

}

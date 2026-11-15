package com.onehintaway.api.config;

import com.onehintaway.api.visitor.RateLimitInterceptor;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
class WebConfig implements WebMvcConfigurer {

	private final AppProperties props;

	private final RateLimitInterceptor rateLimit;

	WebConfig(AppProperties props, RateLimitInterceptor rateLimit) {
		this.props = props;
		this.rateLimit = rateLimit;
	}

	/**
	 * Only the site's own pages may call the API from a browser. PUT is left out on purpose:
	 * the posts sync is called by a script, never by a page.
	 */
	@Override
	public void addCorsMappings(CorsRegistry registry) {
		registry.addMapping("/api/**")
			.allowedOrigins(this.props.corsOrigins().toArray(String[]::new))
			.allowedMethods("GET", "POST")
			.maxAge(3600);
	}

	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(this.rateLimit).addPathPatterns("/api/v1/**");
	}

}

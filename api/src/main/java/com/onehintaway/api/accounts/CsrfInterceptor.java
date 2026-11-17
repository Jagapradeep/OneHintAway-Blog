package com.onehintaway.api.accounts;

import java.util.List;

import com.onehintaway.api.config.AppProperties;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * Guards every request that changes something on the cookie-using endpoints (accounts and
 * progress). Such a request must carry the site's own Origin and the header
 * {@code X-OHW-CSRF}; anything else gets 403 before it reaches a controller.
 *
 * <p>Why that is enough: browsers set Origin themselves and page scripts can't change it,
 * so a request from any other site (or from another onehintaway.com address) is seen for
 * what it is. An HTML form can't add a custom header at all, and a script that tries
 * triggers a CORS preflight, which only the site's origin passes. On top of that the
 * cookie is SameSite=Lax, so other sites' POSTs arrive without it anyway.
 */
@Component
public class CsrfInterceptor implements HandlerInterceptor {

	public static final String HEADER = "X-OHW-CSRF";

	private final List<String> origins;

	CsrfInterceptor(AppProperties props) {
		this.origins = props.corsOrigins();
	}

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
		String method = request.getMethod();
		if (method.equals("GET") || method.equals("HEAD") || method.equals("OPTIONS")) {
			return true;
		}
		String origin = request.getHeader(HttpHeaders.ORIGIN);
		if (origin != null && this.origins.contains(origin) && request.getHeader(HEADER) != null) {
			return true;
		}
		response.setStatus(HttpStatus.FORBIDDEN.value());
		return false;
	}

}

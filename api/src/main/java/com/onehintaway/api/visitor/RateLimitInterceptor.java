package com.onehintaway.api.visitor;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.onehintaway.api.config.AppProperties;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.ConsumptionProbe;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * Limits every request that writes (POST and PUT), per hashed address. Each address has
 * one token bucket per group of endpoints; a request with no token left gets 429 and a
 * Retry-After header.
 *
 * <p>Buckets live in this process's memory. That is right for one API instance; with two
 * replicas each keeps its own count, so the real limit doubles. Move the buckets to
 * Postgres or Redis if that ever matters.
 *
 * <p>It is an interceptor, not a servlet filter, so that Spring's CORS handling runs first
 * and a 429 still carries the CORS headers the browser needs to read it.
 */
@Component
public class RateLimitInterceptor implements HandlerInterceptor {

	private final VisitorHasher hasher;

	private final AppProperties.Rate rate;

	/** Idle buckets are dropped after two hours; the cap keeps a flood of addresses from filling memory. */
	private final Cache<String, Bucket> buckets = Caffeine.newBuilder()
		.expireAfterAccess(Duration.ofHours(2))
		.maximumSize(200_000)
		.build();

	public RateLimitInterceptor(VisitorHasher hasher, AppProperties props) {
		this.hasher = hasher;
		this.rate = props.rate();
	}

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
		String method = request.getMethod();
		if (!method.equals("POST") && !method.equals("PUT")) {
			return true;
		}
		String group = group(request.getRequestURI());
		Bucket bucket = this.buckets.get(group + ':' + this.hasher.address(request), key -> newBucket(group));
		ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);
		if (probe.isConsumed()) {
			return true;
		}
		long seconds = Math.max(1, TimeUnit.NANOSECONDS.toSeconds(probe.getNanosToWaitForRefill()));
		response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
		response.setHeader(HttpHeaders.RETRY_AFTER, Long.toString(seconds));
		return false;
	}

	private static String group(String path) {
		if (path.startsWith("/api/v1/admin/")) {
			return "admin";
		}
		return path.startsWith("/api/v1/subscribers") ? "subscribe" : "count";
	}

	private Bucket newBucket(String group) {
		return switch (group) {
			case "admin" -> bucket(this.rate.adminPerMinute(), Duration.ofMinutes(1));
			case "subscribe" -> bucket(this.rate.subscribePerHour(), Duration.ofHours(1));
			default -> bucket(this.rate.countPerMinute(), Duration.ofMinutes(1));
		};
	}

	private static Bucket bucket(int capacity, Duration period) {
		return Bucket.builder().addLimit(limit -> limit.capacity(capacity).refillGreedy(capacity, period)).build();
	}

}

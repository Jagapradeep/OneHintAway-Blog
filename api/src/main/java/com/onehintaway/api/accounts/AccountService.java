package com.onehintaway.api.accounts;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Locale;
import java.util.Optional;

import com.onehintaway.api.config.AppProperties;
import com.onehintaway.api.subscribers.MailSender;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Sign-in by emailed link, and the sessions that follow.
 *
 * <p>There are no passwords. A reader proves an email address is theirs by opening a link
 * sent to it; the first time, that also creates the account. Both the link token and the
 * session token are 32 random bytes, and only their SHA-256 is stored, so a copy of the
 * database can't be used to sign in. Everything lives in Postgres, so it works the same
 * on every API replica.
 */
@Service
public class AccountService {

	/** How long an emailed link works. */
	static final Duration LINK_LIFE = Duration.ofMinutes(15);

	/** How long a session lasts after it was last used. */
	static final Duration SESSION_LIFE = Duration.ofDays(30);

	/** A session's end date is pushed out at most once in this time, to save writes. */
	private static final Duration RENEW_AFTER = Duration.ofDays(1);

	/** Deleting the account needs a session that began this recently (a fresh emailed link). */
	static final Duration FRESH = Duration.ofMinutes(15);

	public enum Purpose {

		SIGN_IN, DELETE_ACCOUNT

	}

	/** A signed-in reader. {@code renewed} tells the caller to send the cookie again with a new end date. */
	public record Session(String tokenHash, long userId, String email, Instant createdAt, boolean renewed) {
	}

	/** What a used link gives back: the new session's cookie value, and what the link was for. */
	public record SignedIn(String sessionToken, String email, Purpose purpose) {
	}

	private final JdbcClient jdbc;

	private final MailSender mail;

	private final Clock clock;

	private final String siteUrl;

	private final int linksPerEmailPerHour;

	private final SecureRandom random = new SecureRandom();

	AccountService(JdbcClient jdbc, MailSender mail, Clock clock, AppProperties props) {
		this.jdbc = jdbc;
		this.mail = mail;
		this.clock = clock;
		this.siteUrl = props.siteUrl().replaceAll("/+$", "");
		this.linksPerEmailPerHour = props.rate().linkPerEmailPerHour();
	}

	/**
	 * Emails a link. It does the same thing whether or not the address has an account, so
	 * the caller learns nothing about who is registered. Past the hourly limit for one
	 * address it sends nothing and still returns normally, for the same reason. The count
	 * is read from the table, so it is exact across replicas.
	 */
	@Transactional
	public void sendLink(String rawEmail, Purpose purpose) {
		String email = normalise(rawEmail);
		Instant now = this.clock.instant();
		// Housekeeping: links and sessions that ended more than a day ago.
		Timestamp dayAgo = Timestamp.from(now.minus(Duration.ofDays(1)));
		this.jdbc.sql("delete from login_tokens where expires_at < :t").param("t", dayAgo).update();
		this.jdbc.sql("delete from sessions where expires_at < :t").param("t", dayAgo).update();

		int recent = this.jdbc.sql("select count(*) from login_tokens where email = :email and created_at > :since")
			.param("email", email)
			.param("since", Timestamp.from(now.minus(Duration.ofHours(1))))
			.query(Integer.class)
			.single();
		if (recent >= this.linksPerEmailPerHour) {
			return;
		}
		String token = newToken();
		this.jdbc.sql("""
				insert into login_tokens (token_hash, email, purpose, created_at, expires_at)
				values (:hash, :email, :purpose, :now, :expires)
				""")
			.param("hash", sha256(token))
			.param("email", email)
			.param("purpose", purpose.name())
			.param("now", Timestamp.from(now))
			.param("expires", Timestamp.from(now.plus(LINK_LIFE)))
			.update();
		// The token is in the part after "#": browsers never send that part to any server,
		// so it stays out of access logs, analytics and Referer headers.
		String url = this.siteUrl + "/sign-in/#token=" + token + (purpose == Purpose.DELETE_ACCOUNT ? "&for=delete" : "");
		this.mail.sendSignInLink(email, url, purpose == Purpose.DELETE_ACCOUNT);
	}

	/**
	 * Uses a link token once. The single UPDATE both checks and spends it, so two requests
	 * with the same token can't both win. A wrong, expired or used token all give empty:
	 * the caller can't tell which.
	 */
	@Transactional
	public Optional<SignedIn> exchange(String token) {
		Instant now = this.clock.instant();
		Timestamp ts = Timestamp.from(now);
		Optional<LinkRow> link = this.jdbc.sql("""
				update login_tokens set used_at = :now
				where token_hash = :hash and used_at is null and expires_at > :now
				returning email, purpose
				""")
			.param("now", ts)
			.param("hash", sha256(token))
			.query((rs, n) -> new LinkRow(rs.getString("email"), Purpose.valueOf(rs.getString("purpose"))))
			.optional();
		if (link.isEmpty()) {
			return Optional.empty();
		}
		String email = link.get().email();
		// First sign-in creates the account; later ones only note the time.
		long userId = this.jdbc.sql("""
				insert into users (email, created_at, last_sign_in_at) values (:email, :now, :now)
				on conflict (email) do update set last_sign_in_at = excluded.last_sign_in_at
				returning id
				""").param("email", email).param("now", ts).query(Long.class).single();
		String sessionToken = newToken();
		this.jdbc.sql("""
				insert into sessions (token_hash, user_id, created_at, last_used_at, expires_at)
				values (:hash, :user, :now, :now, :expires)
				""")
			.param("hash", sha256(sessionToken))
			.param("user", userId)
			.param("now", ts)
			.param("expires", Timestamp.from(now.plus(SESSION_LIFE)))
			.update();
		return Optional.of(new SignedIn(sessionToken, email, link.get().purpose()));
	}

	/** Finds the session for a cookie value, and pushes its end date out when it is due. */
	@Transactional
	public Optional<Session> find(String sessionToken) {
		if (sessionToken == null || sessionToken.length() != 43) {
			return Optional.empty();
		}
		Instant now = this.clock.instant();
		String hash = sha256(sessionToken);
		Optional<Session> found = this.jdbc.sql("""
				select s.user_id, u.email, s.created_at, s.last_used_at
				from sessions s join users u on u.id = s.user_id
				where s.token_hash = :hash and s.expires_at > :now
				""")
			.param("hash", hash)
			.param("now", Timestamp.from(now))
			.query((rs, n) -> new Session(hash, rs.getLong("user_id"), rs.getString("email"),
					rs.getTimestamp("created_at").toInstant(),
					rs.getTimestamp("last_used_at").toInstant().isBefore(now.minus(RENEW_AFTER))))
			.optional();
		if (found.isPresent() && found.get().renewed()) {
			this.jdbc.sql("update sessions set last_used_at = :now, expires_at = :expires where token_hash = :hash")
				.param("now", Timestamp.from(now))
				.param("expires", Timestamp.from(now.plus(SESSION_LIFE)))
				.param("hash", hash)
				.update();
		}
		return found;
	}

	/** Signs this browser out. */
	public void signOut(Session session) {
		this.jdbc.sql("delete from sessions where token_hash = :hash").param("hash", session.tokenHash()).update();
	}

	/** Signs every browser out, this one included. */
	public void signOutEverywhere(Session session) {
		this.jdbc.sql("delete from sessions where user_id = :user").param("user", session.userId()).update();
	}

	/** True when the session began with a link used in the last few minutes. */
	public boolean isFresh(Session session) {
		return session.createdAt().isAfter(this.clock.instant().minus(FRESH));
	}

	/** Removes the user; sessions and progress go with it (foreign keys), and so do unused links. */
	@Transactional
	public void deleteAccount(Session session) {
		this.jdbc.sql("delete from login_tokens where email = :email").param("email", session.email()).update();
		this.jdbc.sql("delete from users where id = :user").param("user", session.userId()).update();
	}

	private record LinkRow(String email, Purpose purpose) {
	}

	static String normalise(String email) {
		return email.strip().toLowerCase(Locale.ROOT);
	}

	/** 32 random bytes as 43 URL-safe characters. */
	private String newToken() {
		byte[] bytes = new byte[32];
		this.random.nextBytes(bytes);
		return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
	}

	/** Plain SHA-256 is enough here: the input is 256 random bits, so there is nothing to guess. */
	static String sha256(String token) {
		try {
			return HexFormat.of()
				.formatHex(MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8)));
		}
		catch (NoSuchAlgorithmException ex) {
			throw new IllegalStateException(ex);
		}
	}

}

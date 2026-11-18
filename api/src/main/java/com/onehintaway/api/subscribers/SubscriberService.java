package com.onehintaway.api.subscribers;

import java.security.SecureRandom;
import java.time.Clock;
import java.util.Base64;
import java.util.Locale;

import com.onehintaway.api.config.AppProperties;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Double opt-in: signing up only stores the address as PENDING and emails a link holding
 * a random token; the address counts as subscribed once that link is opened. So nobody
 * can subscribe someone else's address, and the list only holds addresses that work.
 */
@Service
public class SubscriberService {

	private final SubscriberRepository subscribers;

	private final MailSender mail;

	private final Clock clock;

	private final String publicUrl;

	private final String siteUrl;

	private final SecureRandom random = new SecureRandom();

	SubscriberService(SubscriberRepository subscribers, MailSender mail, Clock clock, AppProperties props) {
		this.subscribers = subscribers;
		this.mail = mail;
		this.clock = clock;
		this.publicUrl = props.publicUrl().replaceAll("/+$", "");
		this.siteUrl = props.siteUrl().replaceAll("/+$", "");
	}

	/**
	 * Says nothing about whether the address was already known (the caller always gets
	 * the same answer), so the form can't be used to test who is subscribed. Every address
	 * gets an email: a new or pending one the confirmation link, a confirmed one a note that
	 * it is already subscribed, with an unsubscribe link (only the inbox's owner sees it).
	 */
	@Transactional
	public void subscribe(String rawEmail) {
		String email = rawEmail.strip().toLowerCase(Locale.ROOT);
		Subscriber subscriber = this.subscribers.findByEmail(email).orElse(null);
		if (subscriber == null) {
			subscriber = this.subscribers.save(new Subscriber(email, newToken(), this.clock.instant()));
		}
		else if (subscriber.getStatus() == Subscriber.Status.CONFIRMED) {
			this.mail.sendAlreadySubscribed(email, this.siteUrl + "/unsubscribe/#token=" + subscriber.getToken());
			return;
		}
		else {
			subscriber.pending();
		}
		this.mail.sendConfirmation(email, this.publicUrl + "/api/v1/subscribers/confirm?token=" + subscriber.getToken());
	}

	/**
	 * A signed-in reader: the sign-in link already proved the address is theirs, so it is
	 * confirmed straight away, with no email.
	 */
	@Transactional
	public void subscribeVerified(String email) {
		Subscriber subscriber = this.subscribers.findByEmail(email)
			.orElseGet(() -> this.subscribers.save(new Subscriber(email, newToken(), this.clock.instant())));
		if (subscriber.getStatus() != Subscriber.Status.CONFIRMED) {
			subscriber.confirm(this.clock.instant());
		}
	}

	public boolean isSubscribed(String email) {
		return this.subscribers.findByEmail(email).map((s) -> s.getStatus() == Subscriber.Status.CONFIRMED).orElse(false);
	}

	/** Unsubscribing removes the address altogether. Doing it twice is fine. */
	@Transactional
	public void unsubscribe(String email) {
		this.subscribers.findByEmail(email).ifPresent(this.subscribers::delete);
	}

	/** The unsubscribe link in an email: the token it carries is the subscriber's own. */
	@Transactional
	public void unsubscribeByToken(String token) {
		this.subscribers.findByToken(token).ifPresent(this.subscribers::delete);
	}

	/** Returns false for an unknown token. Opening the link twice is fine. */
	@Transactional
	public boolean confirm(String token) {
		Subscriber subscriber = this.subscribers.findByToken(token).orElse(null);
		if (subscriber == null) {
			return false;
		}
		if (subscriber.getStatus() != Subscriber.Status.CONFIRMED) {
			subscriber.confirm(this.clock.instant());
		}
		return true;
	}

	/** 32 random bytes: unguessable, and safe to put in a link. */
	private String newToken() {
		byte[] bytes = new byte[32];
		this.random.nextBytes(bytes);
		return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
	}

}

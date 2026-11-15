package com.onehintaway.api.subscribers;

import java.time.Instant;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "subscribers")
public class Subscriber {

	public enum Status {

		PENDING, CONFIRMED, UNSUBSCRIBED

	}

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	private String email;

	@Enumerated(EnumType.STRING)
	private Status status;

	private String token;

	private Instant createdAt;

	private Instant confirmedAt;

	protected Subscriber() {
	}

	Subscriber(String email, String token, Instant createdAt) {
		this.email = email;
		this.token = token;
		this.createdAt = createdAt;
		this.status = Status.PENDING;
	}

	public String getEmail() {
		return this.email;
	}

	public Status getStatus() {
		return this.status;
	}

	public String getToken() {
		return this.token;
	}

	public Instant getConfirmedAt() {
		return this.confirmedAt;
	}

	void pending() {
		this.status = Status.PENDING;
		this.confirmedAt = null;
	}

	void confirm(Instant when) {
		this.status = Status.CONFIRMED;
		this.confirmedAt = when;
	}

}

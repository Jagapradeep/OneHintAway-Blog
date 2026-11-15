package com.onehintaway.api.subscribers;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface SubscriberRepository extends JpaRepository<Subscriber, Long> {

	Optional<Subscriber> findByEmail(String email);

	Optional<Subscriber> findByToken(String token);

}

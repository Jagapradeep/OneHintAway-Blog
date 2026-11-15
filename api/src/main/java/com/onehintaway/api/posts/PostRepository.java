package com.onehintaway.api.posts;

import java.util.Collection;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

public interface PostRepository extends JpaRepository<Post, String> {

	@Modifying
	@Query("delete from Post p where p.slug not in :slugs")
	int deleteAllExcept(Collection<String> slugs);

}

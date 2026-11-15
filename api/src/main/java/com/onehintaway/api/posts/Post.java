package com.onehintaway.api.posts;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * A post as the API knows it: the site's frontmatter plus the page's plain text, for search.
 * The site's MDX files stay the source of truth; this table is rebuilt from them.
 * The search column {@code tsv} is not mapped: Postgres fills it in.
 */
@Entity
@Table(name = "posts")
public class Post {

	@Id
	private String slug;

	private int number;

	private String title;

	private String pattern;

	private String section;

	@Column(columnDefinition = "text[]")
	private String[] tags;

	private String bodyText;

	protected Post() {
	}

	public Post(String slug, int number, String title, String pattern, String section, String[] tags,
			String bodyText) {
		this.slug = slug;
		this.number = number;
		this.title = title;
		this.pattern = pattern;
		this.section = section;
		this.tags = tags;
		this.bodyText = bodyText;
	}

	public String getSlug() {
		return this.slug;
	}

}

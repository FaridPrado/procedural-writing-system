---
layout: default
title: Inicio
---

<section class="intro-block">
  <p>
    <strong>Ecos del Alma</strong> es un cuaderno digital de escritos breves sobre memoria,
    vínculos, despedidas y regreso a uno mismo.
  </p>
  <p>
    Cada pieza nace de una guía de estilo propia y se publica como una pequeña entrada
    acompañada por una imagen editorial.
  </p>
</section>

<section class="posts-list">
  {% for post in site.posts %}
    <article class="post-card">
      <div class="post-card-content">
        <p class="post-date">{{ post.date | date: "%d · %m · %Y" }}</p>

        <h2 class="post-card-title">
          <a href="{{ post.url | relative_url }}">
            {% if post.title %}
              {{ post.title }}
            {% elsif post.tema %}
              {{ post.tema }}
            {% else %}
              Escrito
            {% endif %}
          </a>
        </h2>

        {% if post.excerpt %}
          <p class="post-excerpt">
            {{ post.excerpt | strip_html | truncate: 180 }}
          </p>
        {% endif %}

        {% if post.image %}
          <a href="{{ post.url | relative_url }}" class="post-image-link" aria-label="Leer {{ post.title }}">
            <img
              src="{{ post.image | relative_url }}"
              alt="{{ post.title | default: post.tema }}"
              class="post-card-image"
              loading="lazy"
            >
          </a>
        {% endif %}

        <a class="read-more" href="{{ post.url | relative_url }}">Leer completo →</a>
      </div>
    </article>
  {% endfor %}
</section>
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

{% if site.posts.size > 0 %}
  <section class="post-list">
    {% for post in site.posts %}
      <article class="post-card">
        {% if post.image %}
          <a href="{{ post.url | relative_url }}" class="post-card-image-link" aria-label="Leer {{ post.title | default: post.tema | default: 'escrito' }}">
            <img
              src="{{ post.image | relative_url }}"
              alt="{{ post.title | default: post.tema | default: 'Ecos del Alma' }}"
              class="card-image"
              loading="lazy"
            >
          </a>
        {% else %}
          <a href="{{ post.url | relative_url }}" class="post-card-image-link" aria-label="Leer {{ post.title | default: post.tema | default: 'escrito' }}">
            <div class="missing-image-card small">
              {{ post.title | default: post.tema | default: 'Ecos del Alma' }}
            </div>
          </a>
        {% endif %}

        <div class="post-card-copy">
          <p class="post-date">{{ post.date | date: "%d · %m · %Y" }}</p>

          <h2>
            <a href="{{ post.url | relative_url }}">
              {{ post.title | default: post.tema | default: 'Escrito' }}
            </a>
          </h2>

          <p class="post-excerpt">
            {{ post.excerpt | strip_html | normalize_whitespace | truncate: 210 }}
          </p>

          <a class="read-link" href="{{ post.url | relative_url }}">Leer completo</a>
        </div>
      </article>
    {% endfor %}
  </section>
{% else %}
  <section class="empty-state">
    <p>Todavía no hay escritos publicados.</p>
  </section>
{% endif %}

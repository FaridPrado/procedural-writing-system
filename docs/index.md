---
layout: default
title: Inicio
---

<section class="intro-card">
  <p><strong>Ecos del Alma</strong> es un cuaderno digital de escritos breves sobre memoria, vínculos, despedidas y regreso a uno mismo.</p>
  <p>Cada pieza nace de una guía de estilo propia y se publica como una pequeña entrada acompañada por una imagen editorial.</p>
</section>

<section class="post-list">
{% for post in site.posts %}
  <article class="post-card">
    <div class="post-card-body">
      <div class="post-date">{{ post.date | date: "%d · %m · %Y" }}</div>
      <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
      <div class="post-excerpt">{{ post.excerpt | strip_html | truncatewords: 34 }}</div>
      <a href="{{ post.url | relative_url }}" class="read-link">Leer completo</a>
    </div>

    {% if post.image %}
      <a href="{{ post.url | relative_url }}" class="card-image-wrap" aria-label="Abrir {{ post.title }}">
        {% if post.image contains '://' %}
          <img src="{{ post.image }}" alt="{{ post.title }}" class="card-image" loading="lazy">
        {% else %}
          <img src="{{ post.image | relative_url }}" alt="{{ post.title }}" class="card-image" loading="lazy">
        {% endif %}
      </a>
    {% endif %}
  </article>
{% else %}
  <section class="post-card">
    <div class="post-card-body">
      <p>Los primeros escritos están por publicarse.</p>
    </div>
  </section>
{% endfor %}
</section>

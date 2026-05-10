---
layout: default
title: Inicio
---

<section class="intro-card">
  <p><strong>Ecos del Alma</strong> es una colección de escritos breves generados a partir de una guía de estilo propia. Cada publicación pasa por un flujo sencillo: escritura, revisión editorial, dirección visual y publicación web.</p>
  <p>No busca reemplazar la voz humana. Es un experimento para dirigir una herramienta creativa con reglas, memoria y criterio.</p>
</section>

{% for post in site.posts %}
  <article class="post-card">
    <div class="post-date">{{ post.date | date: "%d · %m · %Y" }}</div>
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <div class="post-excerpt">{{ post.excerpt | strip_html | truncatewords: 42 }}</div>

    {% if post.image %}
      {% if post.image contains '://' %}
        <img src="{{ post.image }}" alt="Ilustración" class="card-image" loading="lazy">
      {% else %}
        <img src="{{ post.image | relative_url }}" alt="Ilustración" class="card-image" loading="lazy">
      {% endif %}
    {% endif %}

    <a href="{{ post.url | relative_url }}" class="read-link">Leer completo →</a>
  </article>
{% else %}
  <section class="post-card">
    <p>Los primeros escritos están por publicarse.</p>
  </section>
{% endfor %}

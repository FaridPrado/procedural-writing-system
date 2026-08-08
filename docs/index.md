---
layout: default
title: Inicio
---

<section class="intro-block">
<p>
<strong>Ecos del Alma</strong> es un cuaderno digital de escritos breves sobre memoria,
vínculos, cansancio, límites y regreso a uno mismo.
</p>
<p>
Cada pieza pasa por una guía de estilo, una revisión cuidadosa y una tarjeta visual
con el texto completo.
</p>
</section>

{% if site.posts.size > 0 %}
{% assign posts_per_page = 10 %}
{% assign total_posts = site.posts | size %}
{% assign total_pages = total_posts | plus: posts_per_page | minus: 1 | divided_by: posts_per_page %}

<section class="post-list" data-post-list>
{% for post in site.posts %}
{% assign page_number = forloop.index0 | divided_by: posts_per_page | plus: 1 %}
<article class="post-card" data-post-card data-page="{{ page_number }}">
{% if post.image %}
<a href="{{ post.url | relative_url }}" class="post-card-image-link" aria-label="Leer {{ post.title | default: post.tema | default: 'escrito' }}">
<img src="{{ post.image | relative_url }}" alt="{{ post.title | default: post.tema | default: 'Ecos del Alma' }}" class="card-image" loading="lazy">
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
<a href="{{ post.url | relative_url }}">{{ post.title | default: post.tema | default: 'Escrito' }}</a>
</h2>
<p class="post-excerpt">{{ post.excerpt | strip_html | normalize_whitespace | truncate: 210 }}</p>
<a class="read-link" href="{{ post.url | relative_url }}">Leer completo</a>
</div>
</article>
{% endfor %}
</section>

{% if total_pages > 1 %}
<nav class="pagination-controls" data-pagination data-page-size="{{ posts_per_page }}" aria-label="Paginación de escritos" hidden>
<button class="pagination-button" type="button" data-page-prev>Página anterior</button>
<ol class="pagination-pages" data-page-numbers></ol>
<button class="pagination-button" type="button" data-page-next>Página siguiente</button>
</nav>
<script src="{{ '/assets/js/pagination.js' | relative_url }}" defer></script>
{% endif %}
{% else %}
<section class="empty-state">
<p>Todavía no hay escritos publicados.</p>
</section>
{% endif %}

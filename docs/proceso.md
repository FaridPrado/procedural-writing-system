---
layout: default
title: Proceso
permalink: /proceso/
---

<section class="content-card">

# Proceso

Este proyecto funciona como una pequeña cadena editorial automatizada. La idea no fue escribir textos sueltos, sino crear un flujo que pudiera repetirse sin perder dirección.

## 1. Guía de estilo

La base está en `biblia/guia_estilo.json`. Ahí definí el tono, los temas, la longitud, los recursos permitidos y lo que el sistema debe evitar.

## 2. Escritura

El primer agente, **El Poeta**, toma un tema y genera un texto breve. La intención es que el resultado se sienta cercano, visual y menos genérico.

## 3. Revisión

El segundo agente, **El Guardián de la Emoción**, revisa el texto antes de publicarlo. Si detecta clichés, falta de imágenes concretas o un tono demasiado artificial, el sistema intenta de nuevo.

## 4. Dirección visual

El tercer agente, **El Visualizador**, crea una dirección visual para la pieza. Después se genera una imagen base y se compone una tarjeta cuadrada lista para web o redes.

## 5. Publicación

El sistema crea un archivo Markdown dentro de `docs/_posts/`. GitHub Pages se encarga de convertirlo en una publicación visible en la web.

</section>

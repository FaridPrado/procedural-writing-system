# Ecos del Alma

Sistema de escritura generativa que crea, revisa, ilustra y publica escritos breves de forma automática.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange)
![GitHub Actions](https://img.shields.io/badge/Automation-GitHub_Actions-black)
![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub_Pages-2ea44f)
![Status](https://img.shields.io/badge/status-en_desarrollo-brightgreen)

## Demo

- **Web:** https://faridSprado.github.io/ecos-del-alma/
- **Repositorio:** https://github.com/faridSprado/ecos-del-alma.git

## Sobre el proyecto

**Ecos del Alma** nació como un experimento personal para crear contenido poético con una estructura más cuidada que un prompt aislado.

La idea es dirigir un sistema creativo completo: definir una voz, generar textos, revisarlos, crear una pieza visual y publicarlos en una web sin repetir todo el proceso manualmente.

El proyecto combina escritura, dirección editorial, generación visual, automatización y publicación web.

## Qué hace

Cada ejecución sigue este flujo:

1. Carga una guía de estilo propia.
2. Revisa los temas usados recientemente.
3. Elige un nuevo tema.
4. Genera un escrito breve.
5. Revisa si el texto cumple el tono y evita clichés.
6. Si no pasa la revisión, vuelve a intentarlo.
7. Genera una dirección visual.
8. Crea una tarjeta cuadrada lista para web o redes.
9. Publica el texto en `docs/_posts/`.
10. Actualiza la memoria del sistema.

## Agentes

El sistema trabaja con tres agentes:

### El Poeta

Genera el texto principal a partir del tema seleccionado y de la guía de estilo.

### El Guardián de la Emoción

Revisa el texto antes de publicarlo. Evalúa si suena natural, si usa imágenes concretas y si evita frases demasiado genéricas.

### El Visualizador

Convierte el texto aprobado en una dirección visual. Luego el sistema genera una tarjeta cuadrada de 1080x1080 px para acompañar la publicación.

## Arquitectura

```mermaid
flowchart TD
    A[GitHub Actions o ejecución manual] --> B[main.py]
    B --> C[Cargar guía de estilo]
    B --> D[Cargar memoria]
    C --> E[El Poeta]
    D --> E
    E --> F[Texto generado]
    F --> G[El Guardián de la Emoción]
    G --> H{¿Texto aprobado?}
    H -- No --> E
    H -- Sí --> I[El Visualizador]
    I --> J[Prompt visual]
    J --> K[Imagen base]
    K --> L[Tarjeta 1080x1080]
    L --> M[Markdown en docs/_posts]
    M --> N[Actualizar memoria]
    N --> O[GitHub Pages]
```

## Estructura

```text
ecos-del-alma/
├── .github/
│   └── workflows/
│       └── daily-escrito.yml
├── agentes/
│   └── agentes.py
├── biblia/
│   └── guia_estilo.json
├── docs/
│   ├── _config.yml
│   ├── index.md
│   ├── proceso.md
│   ├── _layouts/
│   │   ├── default.html
│   │   └── post.html
│   ├── _posts/
│   └── assets/
│       ├── css/
│       │   └── style.css
│       └── social/
├── memoria/
│   ├── estado_publicacion.json
│   └── temas_usados.json
├── utils/
│   └── render_social.py
├── config.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Guía de estilo

La base creativa está en:

```text
biblia/guia_estilo.json
```

Ahí se define:

- tono general;
- temas disponibles;
- longitud esperada;
- recursos literarios permitidos;
- frases o estilos que se deben evitar;
- estructura sugerida para cada escrito.

Algunos temas incluidos:

- Amor consciente
- Despedidas y duelos
- Soledad fértil
- Esperanza realista
- Vínculos humanos
- Cicatrices
- Volver a mí
- Lo que no dije

## Tecnologías

- **Python 3.11+** para orquestar el flujo.
- **Groq API** para generación y revisión de texto.
- **Llama 3.3 70B Versatile** como modelo principal.
- **Pollinations.ai** para generar una imagen base.
- **Pillow** para componer tarjetas visuales de 1080x1080 px.
- **Markdown + Jekyll** para publicar los escritos.
- **GitHub Pages** para alojar la web.
- **GitHub Actions** para automatizar la ejecución.
- **JSON** para configuración y memoria.

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/faridSprado/ecos-del-alma.git
cd ecos-del-alma
```

### 2. Crear entorno virtual

En Windows PowerShell:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
copy .env.example .env
```

Dentro de `.env`, agrega tu clave de Groq:

```env
GROQ_API_KEY=gsk_tu_clave_de_groq
GROQ_MODEL=llama-3.3-70b-versatile
PROJECT_TIMEZONE=America/Bogota
MAX_INTENTOS=3
TEMAS_RECIENTES_A_EVITAR=3
```

El archivo `.env` no se sube a GitHub.

### 5. Ejecutar

```bash
python main.py
```

Si todo está bien, se creará una nueva publicación en:

```text
docs/_posts/
```

Y una tarjeta visual en:

```text
docs/assets/social/
```

## Automatización

El workflow está en:

```text
.github/workflows/daily-escrito.yml
```

Se puede ejecutar manualmente desde la pestaña **Actions** de GitHub o dejarlo programado para correr una vez al día.

Para que funcione en GitHub Actions, el repositorio necesita un secret llamado:

```text
GROQ_API_KEY
```

Ruta en GitHub:

```text
Settings → Secrets and variables → Actions → New repository secret
```

## GitHub Pages

La web se publica desde la carpeta `docs/`.

Configuración recomendada:

```text
Settings → Pages
Source: Deploy from a branch
Branch: main
Folder: /docs
```

## Por qué está hecho así

El valor del proyecto no está solo en que genera textos. La parte interesante es el flujo completo:

- una guía de estilo editable;
- roles separados para escribir, revisar y visualizar;
- memoria para no repetir temas;
- publicación web automática;
- creación de piezas visuales reutilizables.

Es una forma de convertir la IA en una herramienta dirigida, no en un resultado aleatorio.

## Posibles siguientes mejoras

- Publicación automática en Instagram o Threads.
- Variantes visuales para stories verticales.
- Dashboard con métricas de temas y publicaciones.
- Selector de líneas editoriales.
- Modo oscuro en la web.
- Feed RSS.

## Autor

**Farid Prado**

Proyecto personal de escritura generativa, automatización creativa y publicación web.

# Configuración de Pinterest para Ecos del Alma

Esta integración publica las tarjetas de `docs/assets/social/` como Pins y enlaza cada Pin con su escrito correspondiente en GitHub Pages.

## Arquitectura

- `utils/pinterest_client.py`: autenticación y llamadas a Pinterest API v5.
- `utils/publish_pinterest.py`: detecta publicaciones pendientes, evita duplicados y crea Pins.
- `memoria/pinterest_publicados.json`: registra qué escritos ya fueron enviados a Pinterest.
- `.github/workflows/pinterest-historico.yml`: prueba, lista tableros y sincroniza el histórico bajo demanda.
- `.github/workflows/daily-escrito.yml`: después de generar cada escrito, intenta publicar cualquier escrito pendiente en Pinterest.

La autenticación usa **Client Credentials**, por lo que GitHub Actions solicita un access token nuevo en cada ejecución a partir del App ID y App Secret. No es necesario guardar ni renovar manualmente un access token mensual.

## 1. Preparar la cuenta

La cuenta que administra la app de Pinterest debe ser una cuenta Business, tener el correo verificado y tener activada la autenticación de dos factores para usar Client Credentials.

## 2. Crear el tablero

Crea manualmente en Pinterest un tablero público llamado:

`Ecos del Alma`

Puedes usar otro nombre, pero luego debes colocarlo en la variable `PINTEREST_BOARD_NAME` de GitHub.

## 3. Crear la app de Pinterest

En Pinterest Developers abre **My apps**, acepta los términos de desarrollador y usa **Connect app**.

URL del sitio:

`https://faridsprado.github.io/procedural-writing-system/`

URL de política de privacidad:

`https://faridsprado.github.io/procedural-writing-system/privacidad/`

Descripción sugerida del caso de uso:

> Ecos del Alma es un proyecto editorial automatizado administrado por el propietario de la cuenta. La integración usa Pinterest API para publicar en el tablero propio de Ecos del Alma las imágenes y escritos creados por el proyecto, enlazando cada Pin con su publicación original. No se administran cuentas de terceros ni se recopilan credenciales de usuarios.

Solicita primero **Trial access**. Para que los Pins creados por API sean públicamente visibles se necesita **Standard access**.

## 4. Configurar GitHub

En el repositorio abre:

`Settings > Secrets and variables > Actions`

### Secrets

Crea estos Repository secrets:

- `PINTEREST_APP_ID` = App ID de Pinterest.
- `PINTEREST_APP_SECRET` = App Secret de Pinterest.

Nunca guardes el App Secret dentro de `.env.example`, código, commits, issues o logs.

### Variables

En la pestaña **Variables** crea:

- `PINTEREST_BOARD_NAME` = `Ecos del Alma`

`PINTEREST_BOARD_ID` es opcional. Se usa únicamente si necesitas seleccionar el tablero por ID.

## 5. Probar la integración

Abre:

`Actions > Pinterest - configurar y sincronizar > Run workflow`

Selecciona `probar`.

Esto crea un único Pin técnico y no modifica `memoria/pinterest_publicados.json`.

Con Trial access el Pin de prueba solo será visible para el creador. Esta prueba puede usarse para comprobar la integración antes de solicitar Standard access.

## 6. Solicitar Standard access

Pinterest exige Standard access para que los Pins creados por API se comporten como publicaciones públicas normales. En **My apps**, usa **Upgrade** y sigue el proceso de revisión. Pinterest puede solicitar un video mostrando la autenticación y una acción real mediante API.

No ejecutes todavía el histórico completo si deseas que los 86 Pins sean públicos; espera a tener Standard access.

## 7. Publicar todo el histórico

Cuando tengas Standard access:

1. Abre `Actions > Pinterest - configurar y sincronizar`.
2. Pulsa `Run workflow`.
3. Selecciona `historico`.
4. Deja `max_pins` en `0` para publicar todos los pendientes.

El script registra cada Pin exitoso inmediatamente. Si una ejecución se interrumpe, al volver a ejecutarla continúa con los pendientes. También compara las URLs del tablero para evitar duplicados.

## 8. Nuevas publicaciones

No necesitas hacer nada adicional.

El workflow diario genera el nuevo escrito, lo guarda en GitHub y luego ejecuta `utils/publish_pinterest.py`. Como el script publica únicamente los pendientes, cada nuevo escrito termina automáticamente en Pinterest y cualquier fallo temporal se vuelve a intentar en la siguiente ejecución.

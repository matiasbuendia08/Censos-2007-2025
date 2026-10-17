# Perú en tres censos

Comparador de los Censos Nacionales 2007, 2017 y 2025 del INEI por región, provincia y distrito.

## Publicar en GitHub Pages (5 minutos)

1. En github.com, botón **New repository**. Nombre: `peru-tres-censos`. Público. Créalo vacío.
2. En el repositorio nuevo: **Add file → Upload files**. Arrastra todo el contenido de esta carpeta (index.html, README.md, .nojekyll y la carpeta data). Botón **Commit changes**.
3. **Settings → Pages**. En *Source* elige **Deploy from a branch**, rama **main**, carpeta **/ (root)**. Guarda.
4. En uno o dos minutos la página queda en `https://<tu-usuario>.github.io/peru-tres-censos/`.

## Contador de visitas (solo para ti)

La página ya trae el código de GoatCounter, un contador gratuito, sin cookies y con panel privado.

1. Entra a https://www.goatcounter.com/signup y crea una cuenta con el código **perutrescensos** (el campo "Code").
2. Tu panel queda en https://perutrescensos.goatcounter.com: visitas por día, páginas, de dónde llegan y países. Solo tú puedes verlo con tu usuario.
3. Si ese código ya está tomado, elige otro y cambia `perutrescensos` por el tuyo en la penúltima línea de `index.html`.

## Archivos

- `index.html`: la página completa (HTML, CSS y JavaScript, sin dependencias).
- `data/censos.json`: 41 indicadores de los tres censos para Perú, 25 regiones, 196 provincias y 1,893 distritos (geografía 2025).
- `data/geo.json`: límites provinciales y distritales para el mapa (aproximados, anteriores a 2025).

Para verla en tu computadora: abre una terminal en esta carpeta, corre `python -m http.server` y entra a http://localhost:8000.

Fuente: INEI – Censos Nacionales 2007, 2017 y 2025. Elaboración propia.

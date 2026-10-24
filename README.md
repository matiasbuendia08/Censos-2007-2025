# Perú en tres censos

Comparador de los Censos Nacionales 2007, 2017 y 2025 del INEI: 36 indicadores de población, vivienda, servicios, hogar, educación, salud y lengua, por región, provincia y distrito.

Página: https://matiasbuendia08.github.io/Censos-2007-2025/

## Qué muestra

- **Comparador:** elige tema, indicador, periodo (2007→2017, 2017→2025 o 2007→2025) y nivel. Un mapa pinta el cambio y dos tablas muestran los cinco territorios que más mejoraron y los cinco que más retrocedieron. Un gráfico muestra la evolución en los tres censos del ámbito elegido frente al Perú.
- **Ficha por territorio:** los 36 indicadores de cualquier región, provincia o distrito, con porcentaje, número y nota de comparabilidad.
- **Elige qué cuenta:** en paredes, techos, pisos, agua y desagüe puedes marcar qué materiales o fuentes cuentan; por defecto se usa la definición recomendada (material adecuado o red pública). En no asistencia escolar puedes ver de 6 a 16 años juntos o solo 6 a 11 o 12 a 16 años, y en nivel educativo (población de 15 años a más, como lo publica el INEI) puedes elegir qué niveles contar.
- **Metodología:** universos, geografía y qué no se compara entre censos.

## Datos

- `data/censos.json`: valores y conteos de los tres censos para Perú, 25 regiones, 196 provincias y 1,893 distritos (división territorial de 2025, cruce por ubigeo), con el detalle por categoría de paredes, techos, pisos, agua y desagüe.
- `data/geo.json`: límites para el mapa: distritos censales del INEI con la división de 2017 (versión simplificada de josedaniel-cb/limites-peru-geojson, licencia MIT); provincias y regiones unidas a partir de ellos. Los 19 distritos creados entre 2017 y 2025 no tienen polígono propio.

Población y viviendas censadas, sin la estimación de población omitida.

Fuente: INEI – Censos Nacionales 2007, 2017 y 2025. Elaboración propia.

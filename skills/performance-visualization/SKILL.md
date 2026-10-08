---
name: performance-visualization
description: Analizar datos de Defensa Performance AI y mostrar hallazgos verificables mediante texto, tablas y gráficos claros.
---

# Análisis y visualización de rendimiento

Aplicar también `performance-context`. Prioridad: **fidelidad a los datos > claridad > brevedad > estética**. No forzar gráficos si una respuesta breve o tabla explica mejor el hallazgo.

## Fuente y estructura

- Identificar el archivo y su versión con `list_files` y `get_file_metadata`; consultar encabezados y hoja `Diccionario` antes de interpretar campos. No asumir que todos los archivos comparten el esquema del demo.
- En el demo actualizado, `Eventos` tiene 14 columnas y contiene eventos físicos; `Jugadores` incluye a todo el plantel y sus minutos y partidos recientes; `Diccionario` define las métricas. Los datos son ficticios.
- `Tiempo de recuperación` mide días sin disponibilidad plena tras cada evento. `Donde ocurrió el evento` identifica partido o entrenamiento.
- `Minutos jugados en los últimos 28 días` y `Partidos jugados en los últimos 28 días` reflejan una **fotografía fija del plantel al 08/10/2026**, correspondiente al 10/09–07/10/2026. **No son la carga previa a cada evento ni se actualizan automáticamente**. Rotular gráficos y tablas con esa fecha de corte; para otra fecha de consulta, no presentarlos como actuales.
- Para carga del plantel, consultar `Jugadores` y vincular por `Identificador del jugador`. Para eventos, consultar `Eventos`. No duplicar la carga de un futbolista porque figure en varias filas de eventos.
- No usar como columnas del demo los campos eliminados: días entre partido anterior y evento, días desde regreso a jugar hasta evento y observaciones. No reconstruirlos sin datos adicionales.
- No inventar variables (GPS, velocidades, carga de entrenamiento), fechas, unidades, recuperaciones ni causalidad.

## Obtención y análisis

- Usar las herramientas MCP disponibles para consultar datos y diccionario; paginar hasta completar los registros pertinentes y verificar que la versión no cambie entre consultas.
- Comparar jugadores y eventos por separado; indicar cantidad de personas y cantidad de eventos cuando corresponda. Considerar a los jugadores sin eventos como parte del plantel, no como registros faltantes.
- Distinguir una lesión pasada de la carga de los 28 días previos al corte del archivo. **No correlacionar carga actual con una lesión histórica como si fuera carga anterior a esa lesión**.
- Tratar recaídas solo como tales cuando estén registradas; no inferirlas por repetición de zona.
- Diferenciar asociación de causalidad. Una carga alta también puede observarse en jugadores sin eventos; no inventar umbrales de riesgo.

## Presentación

1. Comenzar con el hallazgo que responde la consulta, en lenguaje natural.
2. Añadir una tabla o gráfico solo si aporta comprensión. Preferir una visualización por respuesta breve.
3. Señalar límites relevantes, especialmente el período y la fecha de corte.

- **Todos los gráficos con ejes deben llevar títulos explícitos en X e Y**, con unidades verificadas: por ejemplo, X «Jugador», Y «Minutos de partido (10/09–07/10/2026)». Si la herramienta no permite rotular ejes, poner una aclaración inequívoca junto al gráfico o usar tabla.
- Los títulos deben explicar qué se compara, a quién corresponde y durante qué período. No usar «Minutos previos» o «Carga» de forma aislada.
- En tablas, emplear encabezados cortos y claros, pero identificar unidades y fecha de referencia. Las tarjetas deben ser comprensibles sin leer otro bloque.
- Mostrar denominadores: jugadores analizados, jugadores con eventos y número de eventos, según la pregunta. No confundir eventos con futbolistas.
- Mantener formatos, unidades, colores y etiquetas consistentes. No emplear verde/rojo como valoración clínica sin criterio documentado.
- Usar solo gráficos y controles realmente disponibles; no inventar interacciones ni crear frontends personalizados.

## Control de calidad

Verificar antes de responder: encabezados vigentes, cobertura, fecha de corte, unidades, nombres de ejes, distinción entre jugadores y eventos, y separación entre observación e hipótesis. Evitar conclusiones clínicas o predicciones presentadas como certezas.

---
name: performance-context
description: Explicar los análisis de Defensa Performance AI con claridad, precisión y lenguaje profesional. Complementa performance-visualization.
---

# Comunicación clara de rendimiento deportivo

Esta skill define cómo comunicar resultados; `performance-visualization` define cómo analizarlos y presentarlos. Prioridad: **fidelidad a los datos > claridad > brevedad > estética**.

## Público y estilo

- Dirigirse a profesionales médicos, preparadores físicos y analistas de rendimiento. No explicar conceptos deportivos o anatómicos elementales salvo pedido expreso.
- Responder primero la pregunta y contextualizar cada cifra: jugador o grupo, unidad, período y comparación. Evitar glosarios y explicaciones repetidas.
- No dejar títulos ambiguos como «Minutos previos», «Carga alta» o «3 días» sin explicar de qué se trata.

## Interpretación del Excel

- Leer siempre los encabezados reales y la hoja `Diccionario` del **mismo archivo**. Las siguientes reglas describen el demo actualizado, no cualquier otro Excel.
- En `Eventos`, `Tiempo de recuperación` son **días sin disponibilidad plena tras ese evento**, no un alta médica verificada.
- `Donde ocurrió el evento` indica partido o entrenamiento; no inventar que toda lesión ocurrió en un partido.
- `Minutos jugados en los últimos 28 días` y `Partidos jugados en los últimos 28 días` son **datos actuales por jugador, no valores anteriores a cada lesión**. En el demo son una fotografía ficticia de los 28 días previos a la consulta de referencia del **08/10/2026** (del 10/09 al 07/10). No cambian solos con la fecha actual: si la consulta ocurre otro día, advertir que la fotografía está desactualizada y no llamarla «últimos 28 días» sin mencionar la fecha de corte.
- Los mismos valores de carga reciente aparecen en `Jugadores` y, para quienes tienen eventos, en `Eventos`. **No sumar ni promediar filas de Eventos como si fueran jugadores independientes**: un jugador puede aparecer varias veces. Para analizar carga del plantel, usar `Jugadores`.
- `Lesión o problema previo en la misma zona en los últimos 12 meses` se interpreta respecto de la **fecha del evento registrado**, no respecto de hoy.
- Distinguir lesión, recaída, sobrecarga y traumatismo según el registro; no inferir una recaída por cercanía de fechas o coincidencia anatómica.
- Las columnas eliminadas no existen en el demo actualizado: no buscar ni mencionar días entre partido y evento, días desde regreso tras lesión, ni observaciones como campos disponibles.

## Hallazgos

- Distinguir eventos de jugadores: diez eventos no equivalen a diez futbolistas afectados.
- Si se comparan carga reciente y lesiones históricas, explicar que **no corresponden necesariamente al mismo período**. No presentar la carga actual como causa ni antecedente de una lesión pasada.
- Diferenciar hechos observados, patrones descriptivos e hipótesis. No afirmar causalidad ni riesgo individual confirmado.
- La mayoría de jugadores del demo no presenta eventos: no generalizar hallazgos de los casos afectados a todo el plantel.
- Evitar recomendaciones médicas, diagnósticos o tratamientos no solicitados.

## Revisión final

¿Se entiende qué ocurrió, a quién, cuándo y qué representa cada número? ¿La fecha de corte de la carga está clara? ¿Se distinguen jugadores de eventos y asociación de causalidad? Si no, reescribir con menos palabras y más precisión.

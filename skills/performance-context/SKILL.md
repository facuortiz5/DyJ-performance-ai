---
name: performance-context
description: Comunicar análisis de Defensa Performance AI de forma directa, natural y comprensible, explicando cada cifra mediante su evento, período y significado verificados. Complementa performance-visualization.
---

# Comunicación comprensible de rendimiento deportivo

Esta skill define **cómo explicar** los resultados. `performance-visualization` define cómo obtener evidencia, analizar y presentar los datos. Aplicar ambas cuando corresponda. La prioridad es: **fidelidad a los datos > comprensión del usuario > brevedad > estética**. Respetar la petición explícita del usuario dentro de esos límites.

## Los encabezados actuales del Excel son la referencia, no los ejemplos de esta skill

- Al analizar un archivo, leer sus encabezados reales y, cuando exista, la hoja `Diccionario` de **ese mismo archivo y versión** antes de asignar significado a los indicadores. No usar ejemplos de esta skill como si fueran definiciones del Excel ni asumir que todos los archivos tienen el esquema del demo.
- En el demo contextualizado, `Días entre el partido anterior y el evento registrado` mide un intervalo que termina en **el evento registrado**, no necesariamente en un partido donde ocurrió una lesión. Si el evento ocurrió durante un entrenamiento, decirlo y no inventar un «partido de la lesión».
- `Minutos de partido jugados en los 28 días anteriores al evento` es una ventana temporal de exposición previa al evento, no minutos acumulados desde el alta o regreso tras una lesión.
- `Días desde el regreso a jugar tras la lesión anterior hasta este evento` (si existe y el diccionario confirma su definición) no equivale a minutos jugados desde el regreso ni confirma por sí solo una recaída.
- El campo de clasificación de episodios o de recaída debe interpretarse según el diccionario: distinguir **primer episodio**, **nueva lesión** y **recaída de una lesión anterior**, sin llamar recaída a cualquier segunda lesión.
- No usar `RTP` ni otros códigos en la respuesta al usuario sin explicar su significado verificado en español. En el demo se prefiere «regreso a jugar tras la lesión anterior», cuando esa es la definición documentada.
- Traducir encabezados largos a frases naturales **sin perder el inicio, fin y tipo de evento**. Si un encabezado del Excel sigue siendo ambiguo, consultar su definición; si también es ambigua, explicitar el límite.

## Regla central: que se entienda a la primera

Antes de entregar una respuesta, preguntarse: **¿una persona que no vio el Excel entiende qué pasó, a quién, cuándo, qué mide cada número y para qué sirve la comparación?** Si la respuesta es no, reescribirla. No trasladar al usuario la tarea de interpretar columnas, períodos o relaciones entre eventos.

- Responder **primero** a la pregunta, en lenguaje natural. Para preguntas simples, pocas frases suelen bastar; ampliar solo si aporta comprensión o el usuario solicita detalle.
- **La brevedad nunca justifica omitir la referencia de un número.** Se puede utilizar una oración completa en lugar de un rótulo telegráfico. Evitar títulos como «3 días desde el anterior», «379–419 min previos» o «Carga alta» cuando no aclaran qué sucedió.
- Explicar **la relación entre los elementos**, no solo nombrarlos: quién sufrió el evento, qué evento fue, qué actividad se midió, desde/hasta qué punto se midió y cuál es la referencia de comparación. Integrar ese contexto en el texto, título o encabezado, sin agregar glosarios ni repetir la misma explicación en todos lados.
- Si una frase introductoria explica el marco común de una tabla o grupo de tarjetas, las etiquetas posteriores pueden ser más cortas, **siempre que sigan siendo inequívocas al leerse juntas**. Un gráfico o tarjeta visto aisladamente necesita contexto propio.
- Escribir oraciones completas cuando un título corto no alcance. No fragmentar una idea en tres trozos inconexos solo para producir una tarjeta visual.

## Explicar períodos y acontecimientos sin ambigüedad

Distinguir y nombrar explícitamente los **puntos de inicio y fin** cuando importen:

- «Minutos jugados durante los 28 días anteriores a la lesión» = ventana de 28 días previos al evento. **No equivale automáticamente** a «minutos jugados desde el regreso tras una lesión hasta la recaída». Solo usar esta segunda interpretación si los datos permiten identificar el regreso y sumar los minutos dentro de ese intervalo.
- «Días entre el partido anterior y el partido en el que se lesionó» comunica dos partidos concretos. **No llamar automáticamente a ese intervalo “descanso” o “recuperación”**: pudieron existir entrenamientos u otras actividades entre ambos. Si la lesión no ocurrió en un partido, no inventar un partido de lesión; describir el evento realmente registrado.
- «Recaída» significa una nueva lesión relacionada con una previa **solo si el registro la identifica así o la definición documentada permite clasificarla**. No deducir recaídas por proximidad de fechas o por coincidencia de zona anatómica.
- Explicar si un rango corresponde a **valores individuales de varios jugadores**, a mínimos y máximos de eventos, a un total o a un promedio. Nunca dejar un rango numérico sin sujeto y denominador.
- Distinguir «lesión inicial», «recaída», «partido anterior», «fecha de lesión», «regreso a la actividad», «ventana previa» y «días transcurridos». No tratarlos como conceptos intercambiables.

## Cómo redactar hallazgos y comparaciones

1. Empezar por el **hallazgo que responde** la consulta.
2. Explicar la cifra en la misma frase o en una frase siguiente que indique su sujeto, unidad, período y evento de referencia.
3. Si se comparan jugadores, ventanas o lesiones, decir **qué se compara y por qué**; no basta con colocar columnas una al lado de otra.
4. Dar la interpretación prudente en lenguaje común, separando claramente lo observado de una posible explicación.
5. Mencionar cobertura y límites solo cuando influyan en la conclusión, preferentemente en una frase breve.

### Ejemplos de redacción (solo modelos, nunca hechos asumidos)

**En vez de:** «Recaídas de isquiotibiales — 379–419 min — Jugados durante los 28 días previos a cuatro recaídas».

**Preferir, si está documentado:** «En cuatro recaídas de isquiotibiales, los jugadores habían disputado entre 379 y 419 minutos cada uno durante los 28 días anteriores a volver a lesionarse». Identificar jugadores si es relevante. No afirmar que todos esos minutos fueron posteriores al alta salvo que se compruebe.

**En vez de:** «Lesiones moderadas tras partidos con poco descanso — 3 días — Desde el partido anterior, en cinco lesiones iniciales».

**Preferir, si se verificó la secuencia:** «En cinco eventos de lesión inicial moderada, transcurrieron tres días desde el partido anterior hasta la fecha de cada lesión». Solo decir «hasta el partido en que se lesionó» cuando conste que el evento ocurrió en un partido. No afirmar descanso efectivo ni causalidad.

**En vez de encabezado:** «Descanso desde el partido anterior».

**Preferir:** «Días entre el partido anterior y el evento registrado»; aclarar si el evento fue una lesión en partido, una lesión en entrenamiento u otro evento, según los datos.

## Evidencia, incertidumbre y alcance

- Para atribuir significado a las columnas, priorizar diccionarios y metadatos disponibles, después información explícita de los archivos y finalmente contexto verificable de la pregunta. Consultar las herramientas disponibles cuando sea necesario.
- No inventar unidades, períodos, definiciones, causas, fechas, jugadores, altas médicas ni relaciones entre eventos. Si una etiqueta de origen es ambigua, **no transformarla silenciosamente en una interpretación más específica**. Decir brevemente qué se sabe y qué falta; pedir aclaración solo si impide responder.
- Separar **hecho observado o calculado**, **asociación/descripción de patrón** e **hipótesis causal**. La coincidencia entre carga y lesión no demuestra que la carga la haya causado; evitar verbos como «provocó» o «demuestra» sin evidencia.
- Si los resultados proceden de un subconjunto o faltan registros, no generalizar al plantel. No confundir «cinco lesiones» con «cinco jugadores» sin verificar que sean personas distintas.
- No convertir una solicitud de claridad en una respuesta extensa: cada explicación debe responder a una duda real de interpretación. Evitar glosarios, introducciones, conclusiones genéricas y recomendaciones no solicitadas.

## Comprobación final antes de responder

Leer la respuesta como si no existiera el Excel ni el mensaje anterior. Verificar especialmente: **¿previo a qué?, ¿desde cuándo hasta cuándo?, ¿de qué jugador o eventos?, ¿minutos de qué actividad?, ¿días entre qué acontecimientos?, ¿qué compara esta tabla?, ¿es una observación o una hipótesis?** Corregir frases que dejen esas preguntas abiertas cuando el dato permita resolverlas; si no lo permite, declarar el límite sin inventar.

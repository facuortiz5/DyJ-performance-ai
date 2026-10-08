# Mantenimiento de Defensa Performance AI

Guía técnica para el servidor MCP, las skills de contexto y visual y Secure MCP Tunnel.
El README público se conserva sin cambios. Las rutas de la guía manual
corresponden al equipo de la demo; no se incluyen credenciales ni el perfil privado.

## Fase 2: MCP local de solo lectura

La Fase 1 administra archivos; la Fase 2 agrega lectura de CSV/XLSX mediante
MCP. El servidor comparte `storage/` con Streamlit y funciona sin abrir la UI.
No requiere hosting, bases de datos ni llamadas a una API de modelos.
Secure MCP Tunnel está configurado en el equipo de la demo. La creación del
plugin y la prueba completa desde ChatGPT requieren iniciar sesión en ChatGPT.

### Instalación en Windows (PowerShell)

Requiere Python 3.10 o superior. Verificá un intérprete real: los comandos
`python`/`py` pueden ser alias de Microsoft Store. Desde la raíz del proyecto:

```powershell
py -3 --version
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-mcp.txt
```

Si `py` no funciona, usá la ruta absoluta de tu Python en los dos primeros
comandos. `requirements-mcp.txt` fija `mcp==2.3.0` y `openpyxl==3.1.5`.
Streamlit mantiene sus dependencias en `requirements.txt`; para ejecutar la
app o sus tests en ese entorno, instalalas también:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m streamlit run app.py
```

### Ejecutar el servidor

```powershell
& .\.venv\Scripts\python.exe mcp_server.py
```

El transporte es exclusivamente `stdio`: espera mensajes MCP en stdin y
responde en stdout. No abre puertos ni muestra una interfaz. El cliente MCP
debe lanzar el proceso; ejecutarlo manualmente solo lo deja esperando.
El almacenamiento se resuelve junto a los archivos Python, independientemente
del directorio desde el que se lance el servidor. No se crea `storage/` al leer.

### Herramientas

| Herramienta | Parámetros | Resultado |
|---|---|---|
| `list_files` | `offset=0`, `limit=100` | Archivos ordenados por nombre, metadatos y `next_offset`. |
| `get_file_metadata` | `filename`, `sheet` opcional | Nombre, extensión, bytes, modificación UTC y versión; CSV/XLSX incluye hojas y encabezados. |
| `read_performance_data` | `filename`, `sheet`, `columns`, `filters`, `date_column`, `date_from`, `date_to`, `offset`, `limit` | Filas estructuradas, columnas, versión del archivo y `next_offset`. |

Todas declaran `readOnlyHint=true`, `destructiveHint=false` y
`openWorldHint=false`. No hay herramientas para modificar o descargar archivos.
Los nombres son nombres simples, nunca rutas.

Ejemplo de argumentos para leer eventos:

```json
{
  "filename": "defensa_performance_demo.xlsx",
  "sheet": "Eventos",
  "columns": ["ID_Jugador", "Fecha", "Tipo_evento", "Minutos_últimos_28d"],
  "date_column": "Fecha",
  "date_from": "2026-01-01",
  "date_to": "2026-12-31",
  "offset": 0,
  "limit": 100
}
```

La planilla de `data/` no se expone automáticamente: cargala mediante la app
para que quede en `storage/`. Consultá primero sus encabezados y fechas.
`filters`, por ejemplo `{"ID_Jugador": "J001"}`, compara texto exacto,
distingue mayúsculas y combina condiciones con AND. CSV conserva valores
como texto; XLSX conserva números y convierte fechas a ISO. Los rangos de
fecha son inclusivos y requieren valores ISO y `date_column` explícita.

`offset` cuenta filas que cumplen los filtros. Para continuar, usá
`next_offset` con los mismos parámetros; `null` indica el fin. No se devuelve
un total global. Compará `version` entre páginas y reiniciá si cambió: no hay
snapshot persistente. Se detectan cambios ordinarios durante una lectura.

### Pruebas automatizadas

```powershell
& .\.venv\Scripts\python.exe -m unittest test_app test_mcp -v
```

Los tests usan directorios temporales y datos sintéticos, sin alterar los
archivos reales de `storage/`. Incluyen operaciones de Fase 1, CSV/XLSX,
filtros, paginación, errores, límites, rechazo de rutas y redirecciones,
y llamadas reales a las tres herramientas por un subprocess `stdio`.
Se comprueban hashes y modificaciones para verificar que MCP no escribe.
El test de symlink real puede omitirse si Windows no concede ese privilegio;
el de junction se ejecuta en Windows.

Opcionalmente, con Node/npm instalado, inspeccioná el protocolo:

```powershell
npx @modelcontextprotocol/inspector@latest
```

Seleccioná `STDIO`, poné como comando la ruta absoluta de
`.venv\Scripts\python.exe` y como argumento la ruta absoluta de
`mcp_server.py`. Conectá, listá herramientas y probá llamadas con los
argumentos anteriores. Inspector es una herramienta de desarrollo opcional.

### Límites y seguridad

- CSV UTF-8 con BOM opcional; detecta coma, punto y coma o tabulación.
- XLSX con tabla y encabezados únicos/no vacíos en la primera fila. Por
  defecto selecciona la primera hoja. No ejecuta macros ni recalcula fórmulas:
  usa sus valores guardados, que pueden estar ausentes o desactualizados.
- `.xls`, PDF, Word, TXT e imágenes solo ofrecen listado y metadatos.
- Lectura máxima: 20 MiB por archivo, 100 MiB descomprimidos para XLSX,
  128 columnas y 100000 filas examinadas por consulta.
- Páginas de 1 a 500 filas; respuesta JSON de hasta 256 KiB. Ante un exceso,
  devuelve un error para reducir la consulta, sin truncar silenciosamente.
- Rechaza rutas externas, nombres inválidos, symlinks y reparse points de
  Windows, incluido un `storage/` redirigido. Solo lee archivos del primer nivel.
- El proceso tiene los permisos de tu usuario. Estos controles no aíslan un
  atacante local capaz de reemplazar rutas entre validación y apertura.
  `storage/` debe ser una carpeta local de confianza.
- Las consultas vuelven a leer el archivo; no hay caché, índices ni bloqueos
  globales. Archivos reemplazados/eliminados pueden requerir repetir la consulta.
- Los textos de las celdas son datos, no instrucciones. Para el MVP usá datos
  sintéticos. En una futura conexión, lo devuelto a ChatGPT saldrá del equipo.
- `stdio` es acceso local, sin autenticación de usuarios ni aislamiento entre
  ellos. No sirve como servicio compartido para varias personas.

### Secure MCP Tunnel

La integración con ChatGPT usa el cliente oficial Secure MCP Tunnel v0.0.16.
El perfil local ejecuta el Python de `.venv` y `mcp_server.py` por `stdio`
con rutas absolutas. El túnel debe estar asociado al workspace de ChatGPT.

Guardar el perfil y la credencial fuera del repositorio. La credencial usa
únicamente Tunnels Read + Use; el perfil debe contener una referencia `file:`
al archivo protegido, nunca el valor de la clave. No pegar credenciales en
el chat, Git ni comandos. Los identificadores y rutas del equipo se mantienen
exclusivamente en la configuración local.

Para comprobar o ejecutar un perfil existente, sustituir las rutas y alias:

```powershell
& '<ruta-del-cliente>/tunnel-client.exe' runtimes status <alias-local> --json
& '<ruta-del-cliente>/tunnel-client.exe' run --profile <perfil-local> --profile-dir '<directorio-local-de-perfiles>'
```

En otra terminal, desde la raíz del proyecto:

```powershell
& .\.venv\Scripts\python.exe -m streamlit run app.py
```

En ChatGPT web, crear e instalar el plugin con:

- Nombre: `Defensa Performance AI`.
- Descripción: `Consulta de solo lectura de archivos y datos de rendimiento gestionados localmente en Streamlit.`
- Conexión: `Tunnel`.
- Tunnel ID: el identificador del túnel propio configurado localmente.
- Autenticación del servidor MCP: `No authentication`; el acceso al túnel
  depende de la organización/workspace y de la credencial del cliente local.

Seleccionar el plugin en el chat con `@`. Cargar la planilla sintética de
`data/` mediante Streamlit y pedir al plugin que liste archivos, consulte las
hojas y lea una página de `Eventos`. No adjuntar nuevamente el Excel a ChatGPT.
La computadora y el cliente del túnel deben seguir encendidos. No se contrata
hosting ni se realizan llamadas a modelos desde el servidor.

La prueba del 07/10/2026 en ChatGPT consultó el demo ya almacenado, sin volver
a adjuntarlo: devolvió las hojas `Eventos`, `Jugadores` y `Diccionario`, y las
primeras cinco filas, coincidentes con la lectura local (`next_offset=5`).
El cliente informó `healthy=true` y `ready=true`, pero `/health/mcp` permaneció
en `not_observed`; para comprobar la integración usar también una consulta real.

Las celdas XLSX con formato de fecha se devuelven como `YYYY-MM-DD`, también
si incluyen hora (se omite la hora), respetando el calendario 1900 o 1904 del
libro. Los números con formato `General` y los textos no se convierten.
La columna `Fecha` del demo tiene formato `yyyy-mm-dd`, conservando sus
seriales originales. La lectura local verificó las 59 fechas ISO tanto en
`data/` como en la copia de `storage/`, que permanece excluida de Git.

## Fase 3: guía visual y análisis deportivo

`skills/performance-visualization/SKILL.md` contiene las instrucciones de
presentación e interpretación, con el frontmatter `name` y `description` de
una skill. El servidor carga el archivo UTF-8 al arrancar, desde una ruta
relativa a `mcp_server.py`, y lo agrega íntegro al campo MCP `instructions`
después de las reglas existentes. La descripción de `read_performance_data`
también orienta al modelo a aplicar la guía. No cambia los argumentos,
resultados ni procesamiento de las tres herramientas.

La guía prioriza tarjetas/KPI, líneas, barras, comparaciones, colores con
significado deportivo e interacción nativa cuando estén disponibles. Incluye
paginación y versiones, exposición y unidades comparables, relaciones entre
jugadores, tendencias colectivas y separación entre hechos, tendencias e
hipótesis. Si no hay capacidades gráficas, pide indicadores destacados y
tablas. No implementa UI, modelos externos ni nuevos cálculos en el servidor.

Esta integración transmite instrucciones del servidor; no instala una skill
global en ChatGPT ni garantiza su selección o un formato visual determinado.
OpenAI documenta el uso de `instructions` junto con los metadatos de herramientas
y recomienda que los primeros 512 caracteres sean autosuficientes; las reglas
base se conservan al comienzo. Las tarjetas, gráficos y controles dependen de
las capacidades de la sesión y de la respuesta del modelo.

Existe además empaquetado de skills para plugins e importación desde MCP por
`Scan Tools` durante la preparación de una versión del plugin. Esa importación
genera una copia estática, no una lectura del archivo en cada consulta. Esta
fase usa únicamente `instructions`, sin añadir extensiones de importación ni
un paquete independiente; la conexión existente se actualiza con Refresh tools.

### Método recomendado: cargar la skill y usar Refresh tools

1. Editar `skills/performance-visualization/SKILL.md` y conservarlo junto al servidor.
2. Asegurarse de que MCP cargue el nuevo archivo: se lee al iniciar el proceso,
   no en cada consulta. Si cambió desde el arranque, detener e iniciar el túnel
   con el mismo perfil siguiendo la guía de abajo. No reiniciar si ya lo cargó.
3. En **ChatGPT web**, abrir **Plugins**, entrar en **Defensa Performance AI**
   y pulsar **Manage**. En la pantalla de configuración, desplazarse hacia abajo,
   después de **About**, hasta **Manage app**. Pulsar **Refresh tools**.
4. Esperar a que termine y abrir un chat nuevo con Defensa Performance AI.
   Pedir un análisis normalmente: no hace falta invocar ni instalar la skill.

**Refresh tools está en ChatGPT**, no en OpenAI Platform. No es el menú
**Connected → Reconnect**. En la cuenta del creador de este plugin de desarrollo,
**Manage app** muestra **App name**, **App description**, **Refresh tools** y
**Delete app**. La administración depende del rol y de la interfaz disponible;
no se comprobó que otros usuarios o instaladores tengan el mismo control.
Si falta, verificar que se usa la cuenta y el workspace del creador y que se
está al final de la página de configuración, no en la ficha del directorio.

No hace falta desconectar, reinstalar ni recrear el plugin para actualizar sus
herramientas e instrucciones. Conservar el Tunnel ID, perfil y credenciales.
No usar **Delete app**, **Delete plugin** ni **Uninstall** para este procedimiento.

Si falta una skill o no se puede leer como UTF-8, el servidor registra una
advertencia por stderr y conserva las instrucciones base y las otras skills disponibles. Restaurar el archivo,
volver a iniciar MCP y ejecutar **Refresh tools**.

### Evidencia de la actualización del 08/10/2026

Al ejecutar **Manage → Refresh tools** desde ChatGPT, el túnel registró una
solicitud `server/discover` y una `tools/list`, ambas con respuesta HTTP 200.
Antes de esta acción no había registros de esos métodos desde el reinicio.
El handler del SDK incluye `instructions` en `server/discover`; la comprobación
local confirmó que devuelve las reglas base y el contenido íntegro del archivo
actual: 8160 bytes de instrucciones en total. SHA-256 de la skill UTF-8:
`f3afa20a39c668f3fb235284fdd00a522768f793fe6d7a014dcda21a58e933ac`.

Esto aporta evidencia sólida de recuperación de metadatos actualizados. Los logs
no capturan el cuerpo de la respuesta ni el contexto interno del modelo: no
permiten comparar directamente la copia guardada en ChatGPT ni garantizar que
cada respuesta aplique cada indicación. El estado **Connected** o una respuesta
visual por sí solos no prueban qué versión de instrucciones recibió.
`initialize_epoch=0` tampoco descarta el descubrimiento moderno `server/discover`.

### Reiniciar manualmente en este equipo (Windows)

Abrí Inicio, buscá **PowerShell** y abrilo. Los comandos siguientes usan las
rutas instaladas en este equipo; no crean túneles ni credenciales. El perfil
`defensa-performance` conserva el Tunnel ID. El puerto del panel local
`127.0.0.1` puede cambiar al reiniciar, sin cambiar la conexión de ChatGPT.

**1. Comprobar si está funcionando.** Pegá este bloque en PowerShell:

```powershell
$direccionTunel = (Get-Content -LiteralPath 'C:\Users\facun\.local\state\tunnel-client\health\defensa-performance.url' -Raw).Trim()
Invoke-RestMethod "$direccionTunel/healthz"
Invoke-RestMethod "$direccionTunel/readyz"
Start-Process "$direccionTunel/ui"
```

Las respuestas deben ser `live` y `ready`. El último comando abre el panel de
estado en el navegador. El canal `main` debe indicar `stdio`. Estos indicadores verifican la salud
del túnel; no prueban que ChatGPT haya recibido instrucciones o descubierto
herramientas. `/health/mcp` puede mostrar `not_observed` incluso con consultas
correctas; usar también los registros y una consulta real. Si el archivo falta o las consultas fallan, el túnel puede estar
apagado o el archivo puede conservar la dirección de una ejecución anterior.

**2. Detenerlo.** Si lo iniciaste con el comando del paso 3 y conservás esa
ventana abierta, presioná **Ctrl+C** y esperá a que vuelva el cursor.

Para detener la ejecución oculta iniciada por Codex, usá este bloque. Busca
únicamente el cliente con el perfil de este proyecto, detiene su servidor
Python y luego el cliente; no borra el túnel remoto ni el perfil:

```powershell
$tunelesDefensa = Get-CimInstance Win32_Process -Filter "Name = 'tunnel-client.exe'" | Where-Object {
    $_.ExecutablePath -eq 'C:\Users\facun\AppData\Local\OpenAI\tunnel-client\v0.0.16\tunnel-client.exe' -and
    $_.CommandLine -match '--profile defensa-performance(?:\s|$)'
}
foreach ($procesoTunel in $tunelesDefensa) {
    Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
        $_.ParentProcessId -eq $procesoTunel.ProcessId -and $_.CommandLine -match 'mcp_server\.py'
    } | ForEach-Object { Stop-Process -Id $_.ProcessId }
    Stop-Process -Id $procesoTunel.ProcessId
}
```

Si la ejecución fue registrada mediante `runtimes connect`, también existe
`runtimes stop defensa-performance`. Esa orden depende del registro del runtime;
una ejecución directa con `run` no actualiza ese registro. Para las ejecuciones
directas, comprobar salud con el paso 1 en lugar de confiar en el PID guardado
por `runtimes status`. No ejecutar dos clientes del mismo perfil a la vez.

**3. Iniciarlo otra vez.** En PowerShell, pegá:

```powershell
& 'C:\Users\facun\AppData\Local\OpenAI\tunnel-client\v0.0.16\tunnel-client.exe' run --profile defensa-performance --profile-dir 'C:\Users\facun\AppData\Local\OpenAI\DefensaPerformanceAI\profiles' --log.file=
```

Dejá esa ventana abierta mientras uses ChatGPT. El cliente inicia automáticamente
el Python de `.venv` y `mcp_server.py`; no ejecutar el servidor aparte.
Streamlit es independiente y no requiere reinicio para actualizar la skill.

**4. Comprobar y actualizar metadatos.** En una segunda ventana de PowerShell, repetí el
paso 1. Cuando responda `live` y `ready`, usá **Manage → Refresh tools** en
**Defensa Performance AI** en ChatGPT, siguiendo el procedimiento anterior. Abrí un chat nuevo, seleccioná el plugin
con `@` y pedile que liste archivos y compare la evolución de dos jugadores con
las métricas disponibles. Una consulta real confirma el recorrido completo;
no hace falta adjuntar nuevamente el Excel ni copiar un prompt visual.

**Si aparece un error:** comprobá Internet y el mensaje de la ventana del
túnel. Si cambia solo el puerto de `127.0.0.1`, repetí el paso 1 para abrir el
panel nuevo. Si falla la autenticación o el plugin muestra otro túnel, conservá
el perfil y revisá el error antes de cambiar configuración o crear credenciales.
No usar `init`, `runtimes create` ni recrear el plugin para actualizar la skill.

### Verificación y fuentes

`test_mcp.py` comprueba que un cliente real por `stdio` recibe exactamente las
instrucciones base y ambas skills completas, tanto en modo automático como en el
handshake `initialize` de modo legacy. También verifica el arranque desde otro
directorio de trabajo. Las pruebas existentes conservan sus comprobaciones de
las tres herramientas, CSV/XLSX, errores y ausencia de escritura sobre datos.

```powershell
& .\.venv\Scripts\python.exe -m unittest test_mcp -v
```

- [Instrucciones, metadatos e importación de skills MCP](https://developers.openai.com/plugins/build/mcp-server).
- [Formato y empaquetado de skills; importación como copia estática](https://developers.openai.com/plugins/build/skills).
- [Actualizar herramientas, descripciones e instrucciones en ChatGPT](https://developers.openai.com/api/docs/guides/custom-mcp-server).

- [Refresh de conexiones personalizadas y versiones de plugins publicados](https://developers.openai.com/plugins/deploy/connect-chatgpt).

## Fase 4: comunicación contextualizada y presentación clara

El servidor carga al arrancar, en orden, las instrucciones base,
`skills/performance-context/SKILL.md` y `skills/performance-visualization/SKILL.md`.
Ambos archivos se incorporan íntegros a MCP `instructions`; no requieren
instalación ni invocación manual por parte del usuario final.

La Context Skill define cómo responder: primero lo preguntado, con extensión
proporcional y contexto integrado, sin glosarios automáticos ni significados
inventados. La Visual Skill conserva los criterios de evidencia y análisis de
la Fase 3 y define gráficos autosuficientes, etiquetas de tarjetas y encabezados
de tablas descriptivos. La claridad prevalece sobre la estética; una respuesta
textual breve es suficiente cuando explica mejor el resultado. Los encabezados
originales y los datos de los archivos permanecen intactos.

Para actualizar ChatGPT, seguir el procedimiento anterior de reinicio del
proceso MCP y **Refresh tools**, y abrir un chat nuevo. Esta implementación no
reinicia el túnel ni cambia su configuración. La evidencia de hash y tamaño del
08/10/2026 documentada arriba corresponde a la Fase 3, anterior a estos cambios.

Verificación acotada de esta fase:

```powershell
& .\.venv\Scripts\python.exe -m unittest test_mcp.ReadOnlyTest.test_skill_communication_and_visual_requirements test_mcp.ReadOnlyTest.test_missing_or_invalid_skill_preserves_other_instructions test_mcp.ReadOnlyTest.test_mcp_stdio_all_tools_and_no_writes test_mcp.ReadOnlyTest.test_stdio_script_entrypoint -v
```

Las pruebas comprueban integración exacta de ambas skills, reglas de comunicación
y presentación, conservación de los criterios visuales esenciales y las tres
herramientas por MCP sin escribir datos. Verifican además que una skill ausente
o ilegible no impida cargar la otra. No garantizan la calidad de todas las
respuestas del modelo ni prueban la actualización remota de ChatGPT.

Para revisión manual con el demo, pedir primero un dato puntual de un jugador
y luego comparar jugadores o eventos. Comprobar brevedad, período, unidad y
referencia respaldados por `Diccionario`, y títulos/ejes/series comprensibles si
se genera un gráfico. Si una definición no está disponible, la respuesta debe
reconocerlo en lugar de asumirla. Las capacidades visuales dependen de la sesión.

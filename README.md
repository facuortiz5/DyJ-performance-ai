# DyJ Performance AI

Prototype developed for **Club Social y Deportivo Defensa y Justicia** to explore how AI can help performance and medical staff analyze player injury and workload data.

## What it does

Performance AI connects structured club data with ChatGPT, allowing staff to ask questions in natural language such as:

- Which players have recurring muscle injuries?
- Are there patterns before certain injuries?
- Which players suffered a recurrence shortly after returning to play?
- Are recent match loads associated with particular injury patterns?

The goal is to turn historical performance data into useful insights without requiring staff to manually analyze spreadsheets.

## How it works

1. Performance staff upload an Excel file to the Performance AI app.
2. The app processes and structures the data.
3. ChatGPT connects to Performance AI and retrieves the relevant information.
4. ChatGPT analyzes the data and explains the findings in natural language.

## Demo data

The dataset included in this repository is **100% synthetic**.

Player names, injuries, workloads and medical events are fictional and were created exclusively to test the prototype. **No real medical or performance data from Defensa y Justicia is included.**

## Disclaimer

Performance AI is designed as a decision-support tool. It does not provide medical diagnoses or replace the judgment of qualified medical and performance professionals.

## Status

🚧 Early-stage academic prototype / MVP.

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

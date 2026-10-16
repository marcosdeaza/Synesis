# Ficha de las colecciones públicas · v0.1.0

## Motivación y composición

Colección real para comprobar acceso, tipos, fechas, procedencia, derechos y reproducibilidad de Synesis. Se publican **225 referencias universitarias** en [`data/research_225/`](../data/research_225/): 190 de España y 35 internacionales, recuperadas el 16 de octubre de 2026. Las instituciones de las filas son UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10 y USP 5. El registro de fuentes reúne 13 instituciones; otras siete candidatas no aportan filas en esta versión.

El piloto ejecutable de [`data/pilot/rights_cleared.jsonl`](../data/pilot/rights_cleared.jsonl) contiene diez filas de TU Berlin con evidencia CC0 y alimenta los informes y las figuras analíticas. Esas diez filas ya están entre las 225: **no hay 235 trabajos únicos**. `make reproduce` valida además, por separado, la colección completa y guarda [`reports/research_225_validation.json`](../reports/research_225_validation.json); esa comprobación de integridad no incorpora las 225 filas al análisis piloto.

La publicación completa responde a la solicitud del responsable, quien confirmó contar con permiso para los 225 metadatos pensando en su posible uso investigacional y entrenamiento posterior. [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) registra la declaración y su origen; no equivale a validación independiente ni autorización institucional verificada. Las licencias observadas por fuente permanecen intactas, sin asignar CC0 o MIT al conjunto completo. No se ha entrenado un modelo con estos trabajos.

La selección española es la primera página de dos conjuntos OAI; la internacional es intencional por tipo y año. No hay aleatorización, cuotas poblacionales ni exhaustividad. Algunos repositorios seleccionan trabajos por calidad o autorización, y los filtros de publicación cambian con el tiempo. No hay etiquetas de uso real de IA ni anotaciones humanas finalizadas.

## Unidad, procedencia y duplicados

Una fila representa un trabajo referenciado, no una persona. `id` es estable en esta captura; `record_identifier` puede ser un OAI ID, UUID o identificador de listado según fuente. HKUST usa una referencia derivada del título/listado y no se presenta como PID editorial del trabajo. `source_url` enlaza evidencia pública. Los títulos originales se conservan sin traducir.

La validación controla identidad por institución/identificador y por ID público. Un fingerprint del título ayuda a detectar candidatos duplicados; dos trabajos distintos con igual título no se fusionan automáticamente. Una futura deduplicación entre repositorios necesita evidencia de versiones y obra.

Los hashes de los archivos completos están en [`data/research_225/manifest.json`](../data/research_225/manifest.json); `reports/manifest.json` identifica los diez registros que usa el pipeline. Las fichas de fuentes guardan URLs, fecha, selección y hashes de respuestas cuando están disponibles. Una consulta futura puede variar: reproducir las transformaciones de un snapshot es distinto de volver a consultar una fuente cambiante.

## Diccionario de campos

| Campo | Tipo | Significado |
|---|---|---|
| `id`, `institution_id` | texto | Identidad de fila y clave del registro de instituciones |
| `title` | texto | Título principal original, no resumen |
| `abstract` | nulo en esta versión | Texto no redistribuido ni analizado |
| `abstract_available` | booleano | Se observó un campo descriptivo en origen; puede ser administrativo |
| `abstract_omitted_by_policy` | booleano | Se omitió su contenido en la salida |
| `issued_raw` | texto/nulo | Valor original de fecha; puede no ser defensa |
| `created_raw`, `accessioned_raw` | texto/nulo opcional | Fechas adicionales de repositorio, sin armonización automática |
| `year` | entero/nulo | Año del valor declarado o listado de origen; no cohorte académica verificada |
| `date_precision` | categoría | `year`, `month`, `day`, `unknown` |
| `date_semantics`, `date_evidence` | texto | Qué campo/listado se observó y su evidencia |
| `academic_date_verified` | booleano opcional | Solo verdadero cuando la fuente mapea explícitamente a fecha académica, actualmente USP 5 |
| `degree_level` | categoría | `bachelor`, `master` o `unknown`; el original sigue en evidencia |
| `degree_evidence` | texto | Campo institucional que sustenta el nivel |
| `source_url`, `record_identifier` | texto | Enlace verificable e identificador original |
| `language`, `subjects` | texto/nulo, lista | Idioma y materias declarados; cobertura desigual |
| `license` | URI/nulo | Licencia explícita de obra, si existe; no la licencia general del dataset |
| `metadata_license`, `metadata_license_evidence_url` | texto/nulo opcional | Condición específica de reutilización de metadatos y evidencia |
| `rights_statement`, `rights_reference_url`, `access_rights` | texto/nulo opcional | Declaraciones/referencias de derechos y estado de acceso; no se convierten en CC |
| `retrieved_at` | fecha/hora ISO | Recuperación o responseDate de la respuesta institucional |
| `evidence_kind` | texto | `metadata` en este piloto |
| `campus`, `campus_evidence_url` | texto/nulo | Solo con prueba explícita; todos desconocidos en este piloto |

Los campos derivados de `reports/features.jsonl` corresponden al piloto de diez e incluyen indicadores léxicos, longitud de metadatos, resumen efectivamente analizado, fingerprint de título, periodo descriptivo y `ai_use_status=not_assessed`. `period` agrupa año de metadatos hasta 2021, 2022–2023 y desde 2024; es una auditoría operativa, distinta de la ventana académica candidata 2018–2021 frente a 2023–2025 del protocolo. No se usa para estimar efectos. No se presentan esos derivados como si ya se hubieran recalculado para los 225.

## Uso previsto y límites

Uso actual: consulta y validación automática de los 225 metadatos publicados, más reproducción analítica sobre el piloto CC0 de diez. La colección completa queda disponible según la autorización declarada por el responsable, con el alcance registrado en `PERMISSIONS.json`. La publicación no constituye una licencia abierta universal, una certificación de idoneidad para cualquier entrenamiento ni evidencia de representatividad o anonimato. El entrenamiento futuro deberá identificar tarea, campos, condiciones y particiones; no se ha realizado en esta versión.

No se distribuyen PDFs, texto completo, resúmenes, campos de autores/directores/correos o etiquetas humanas finalizadas. Los títulos y enlaces pueden permitir identificar a las personas en la fuente; el corpus está minimizado, no anonimizado de forma irreversible.

No usar para clasificar autoría IA, integridad, plagio, rendimiento individual o calidad de universidades. Una mención, una declaración, una fecha y un resultado de un detector no son intercambiables. Los sesgos de selección y medición no se arreglan con un intervalo de confianza.

## Mantenimiento

Cada ampliación produce un snapshot nuevo y una versión del diccionario, registro de exclusiones, permisos y manifiesto. Cambios de fuente, correcciones y retiradas se documentan en la memoria pública; los snapshots no se sobrescriben. La publicación de estos 225 ya está autorizada por el responsable; las ampliaciones de contenido y el contacto con personas se documentarán según su propio alcance. No inventar un canal de contacto, una afiliación o una revisión independiente que todavía no consten.

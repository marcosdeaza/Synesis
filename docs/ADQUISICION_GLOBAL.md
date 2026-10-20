# Adquisición de documentos internacionales · Synesis v0.2

Esta capa trata **los 35 trabajos internacionales** del snapshot `data/research_225/global.jsonl`: MIT 10, TU Berlin 10, HKUST 10 y USP 5. La petición del responsable de incorporar documentos completos amplía las operaciones de la versión anterior. No se modifican los metadatos congelados ni se transforma una autorización declarada en una licencia abierta de la fuente.

El registro operativo es `data/fulltext/sources_global.jsonl`, una fila por `record_id`, incluidos los casos sin descarga. `files` identifica cada documento guardado mediante ruta relativa, URL de descarga, URL final, SHA-256, tamaño, páginas y derechos observados. Un trabajo localizado pero bloqueado conserva sus enlaces y el motivo real; no se rellena con otro trabajo o un artículo relacionado.

## Ejecución y reanudación

```sh
python3 scripts/acquire_global.py
python3 scripts/acquire_global.py --retry-failures
python3 scripts/acquire_global.py --institution usp
```

El script usa el cliente compartido `PoliteClient`, identifica el proyecto y aplica al menos tres segundos entre peticiones al mismo origen, además de demoras institucionales cuando se declaran. El índice se sustituye atómicamente después de cada registro. Una ejecución posterior conserva los registros completados; `--retry-failures` vuelve a consultar los estados pendientes o fallidos. Antes de omitir un caso descargado se comprueban existencia y SHA-256 de sus archivos. No deben ejecutarse dos procesos globales sobre el mismo índice a la vez.

Los PDF se descargan mediante un archivo temporal `.part`, se verifica su cabecera y se analizan con `pypdf` para confirmar que contienen páginas. Se preservan los bytes originales. El programa no ejecuta anexos, no intenta adivinar contraseñas y no usa credenciales institucionales. Los nombres de archivo se derivan del identificador del registro y del bitstream o enlace, sin deducir identidades del alumnado.

La descarga y el análisis de documentos requieren `pypdf`, además de la biblioteca estándar del pipeline. El conector no depende de `requests`.

## Descubrimiento por institución

### MIT y TU Berlin

A partir del UUID ya conservado en `record_identifier`, se consulta el ítem de la API DSpace, sus bundles y sus bitstreams. Se sigue la paginación que proporciona el servidor, con un límite de diez páginas por ítem/bundle. Se descarga el contenido PDF del bundle **ORIGINAL**: esto excluye miniaturas, texto OCR derivado, licencias, metadatos ALEPH y portadas generadas por el repositorio.

- MIT: `https://dspace.mit.edu/server/api/core/items/{UUID}`.
- TU Berlin: `https://api-depositonce.tu-berlin.de/server/api/core/items/{UUID}`.

Los enlaces de contenido proceden de `_links.content.href`, no de números de bitstream inventados. Si falla la API, se intenta la ficha pública identificada en el snapshot y sólo se siguen enlaces PDF institucionales. Las licencias de obra se extraen de los campos de derechos de la ficha, separadas de CC0 de metadatos.

MIT sirve contenido mediante redirecciones a `cf003.cdn.4science.cloud`. El primer intento trató un HTTP 403 del propio `robots.txt` como bloqueo preventivo. Tras corregir el cliente conforme al [RFC 9309 §2.3.1.3](https://www.rfc-editor.org/rfc/rfc9309.html#section-2.3.1.3), se repitieron esos casos: un 4xx de robots es una política no disponible y no una regla `Disallow`. Un HTTP 401/403 **del documento** sigue bloqueando la descarga. Las observaciones de robots y su tratamiento quedan en el índice; no se cambió la identidad del cliente ni se eludió autenticación.

### USP

Se examinan las cinco fichas HTML originales. Sólo se aceptan enlaces PDF bajo `/publico/` en el directorio de la **misma tesis**; se excluyen políticas del sitio, documentos de bibliografía y enlaces a otros servidores. La licencia de un pie de página no se atribuye a la tesis. Si la ficha no identifica una licencia abierta de la obra, `source_license` permanece en `null`; las condiciones observadas y la autorización del responsable se mantienen conceptualmente separadas.

### HKUST: investigación individual y límites de acceso

Los diez títulos se buscaron individualmente en fuentes oficiales. Se localizaron cuatro enlaces PDF exactos y dos registros del portal con DOI. Los otros cuatro casos se contrastaron con el listado institucional y, cuando existe, el evento de defensa; no se sustituyeron por publicaciones posteriores relacionadas.

| Registro local (sufijo) | Trabajo abreviado | Evidencia institucional específica |
|---|---|---|
| `90343bdae8880ec3` | Understanding Young Adults' Views… | [Portal de la tesis](https://researchportal.hkust.edu.hk/en/studentTheses/understanding-young-adults-views-on-marriage-fertility-and-gender-2/), DOI `10.14711/thesis-hdl167723` |
| `acf38ac3f05067da` | Social and Political Views and Consumer Behavior… | [Portal de la tesis](https://researchportal.hkust.edu.hk/en/studentTheses/social-and-political-views-and-consumer-behavior-in-hong-kong/), DOI `10.14711/thesis-hdl152458` |
| `0c1f642576481f66` | Trump Effect on Obamacare… | [PDF institucional identificado](https://repository.hkust.edu.hk/ir/bitstream/1783.1-152691/1/1783.1-152691.pdf) |
| `37d1ffefc354dd42` | Fragmentation and Divergence… | [PDF institucional identificado](https://repository.hkust.edu.hk/ir/bitstream/1783.1-152483/1/1783.1-152483.pdf) |
| `ddfef707718d2e17` | Sticky Gender Roles in Caregiving… | [PDF institucional identificado](https://repository.hkust.edu.hk/ir/bitstream/1783.1-152513/1/1783.1-152513.pdf) |
| `15978be832848fb8` | Comparative Analysis of Innovation Systems… | [Listado oficial de máster, 2019](https://sosc.hkust.edu.hk/research_n_facilities/master_theses#2019) |
| `757cc9c24da27a4e` | The Effect of Factional Connections… | [PDF institucional identificado](https://repository.hkust.edu.hk/ir/bitstream/1783.1-122003/1/991012770769703412.pdf) |
| `175e500b197f12cb` | Revolutionary Dramas… | [Evento institucional de defensa](https://sosc.hkust.edu.hk/events/revolutionary-dramas-state-hegemony-propagandist-genre-and-divergent-meanings) |
| `bfa9b489208216a5` | Knowledge Elites and Industrialization… | [Evento institucional de defensa](https://sosc.hkust.edu.hk/events/knowledge-elites-and-industrialization-evidence-china-1862-1911) |
| `41be23a8d3161841` | From Online Users to Civil Buddies… | [Listado oficial de máster, 2019](https://sosc.hkust.edu.hk/research_n_facilities/master_theses#2019) |

El [robots del repositorio](https://repository.hkust.edu.hk/robots.txt) devuelve HTTP 200 y contiene `User-agent: *` seguido de `Disallow: /`; las excepciones nominales para buscadores no se aplican a Synesis. No se simula Googlebot/Bingbot ni se descargan esos PDF a través de un proxy.

Se verificaron además las rutas alternativas enlazadas por la biblioteca: [University Theses](https://lbezone.hkust.edu.hk/rse/electronic-theses) redirige al mismo repositorio y el [catálogo Primo](https://julac-hkust.primo.exlibrisgroup.com/discovery/search?vid=852JULAC_HKUST%3AHKUST) también impide la consulta automatizada mediante su política de robots. La [guía oficial de tesis](https://libguides.hkust.edu.hk/e-thesis/find) remite al repositorio y a préstamo interbibliotecario, con acceso condicionado para ciertas colecciones. Los identificadores encontrados sirven para continuar por vías institucionales permitidas; su localización en un buscador no elimina la restricción técnica.

## Lectura de estados, derechos y límites

- `downloaded`: existe al menos un PDF institucional descargado y validado; `files` enumera lo realmente disponible.
- `robots_disallowed`: una regla de robots o un fallo que impide revisar una política, según el detalle conservado, bloqueó la operación.
- `restricted`: respuesta de acceso restringido, como HTTP 401/403 del recurso. No se intentan credenciales o captchas.
- `not_found`: las fuentes revisadas no permitieron identificar un enlace PDF específico. No demuestra que la obra no exista.
- `http_error` / `invalid_pdf`: error HTTP/transporte o respuesta que no valida como PDF. El motivo se conserva en `notes`.

Los anexos no PDF que exponga el bundle se inventarían mediante sus enlaces concretos en `notes`; no se presentan como datasets descargados si no están en `files`. Una tesis puede citar datos o software externos sin adjuntarlos: esos enlaces requieren una siguiente operación específica y no se cuentan como datos obtenidos por este conector.

`source_license` sólo recoge una URI Creative Commons inequívoca observada para la obra. `null` mantiene la falta de una licencia normalizada; no significa dominio público. `license_evidence_url` apunta a la ficha donde se revisó esa información. La autorización declarada por el responsable no modifica la licencia que muestra una institución. Los documentos completos pueden contener autoría, agradecimientos o firmas propios de la publicación original: la minimización del snapshot de metadatos no se describe como anonimización de los PDF.

Las cifras de disponibilidad son resultados de esta adquisición, no denominadores de producción universitaria, adopción de IA o calidad. HKUST sigue siendo Hong Kong SAR, China, no una muestra de China continental. TU Berlin mantiene su selección de trabajos por nota y aval. Los datos de fecha del snapshot no se convierten automáticamente en fechas académicas por obtener el texto.

## Resultado de ejecución

Cierre: **20 de octubre de 2026**. Los 35 registros tienen resultado individual y no quedan casos sin evaluar en este lote.

| Institución | Registros tratados | PDF descargados | Resultado de los restantes |
|---|---:|---:|---|
| MIT | 10 | 10 | — |
| TU Berlin | 10 | 10 | — |
| HKUST | 10 | 0 | 10 bloqueados por robots, con investigación individual y alternativas documentadas |
| USP | 5 | 5 | — |
| **Total** | **35** | **25** | **10 con impedimento técnico explícito** |

Los 25 archivos suman **253.773.914 bytes** y **2.654 páginas**. No se identificaron anexos adicionales no PDF en los bundles originales consultados. Los documentos recuperados tienen cabecera PDF, páginas legibles por `pypdf`, tamaño y SHA-256 verificados. No se guarda una respuesta HTML como si fuera una tesis.

Como comprobación de correspondencia, 24 documentos incluyen los términos del título principal en las primeras cuatro páginas. El trabajo USP `synesis:usp:b8c048abe9604d54` tiene portada en inglés y título principal de ficha en portugués: se comprobó la coincidencia con `dc.title.alternative` de la misma ficha, y el detalle queda en `notes`. No se trata de una tesis diferente. También se conserva la diferencia entre defensa institucional de diciembre de 2023 y portada/disponibilidad de 2024, sin modificar el snapshot ni deducir idioma del PDF de `dc.language=por`.

Se probó la reanudación con acceso de red desactivado: conserva los 35 resultados y los 25 SHA-256, sin nuevas descargas ni cambios de índice. Las diez URLs finales de CDN de MIT se guardan sin credenciales de enlace temporales; `final_url_redacted=true` lo indica y `download_url` mantiene la ruta canónica del repositorio. Las URLs incluidas en errores y notas reciben la misma redacción.

El snapshot `data/research_225/global.jsonl` conserva su SHA-256 original:

```text
0e8554febcdc0eea5a636c87baed65ebe0b07392edddcf0676c82518e66c40c3
```

La falta de descargas HKUST no se presenta como embargo o ausencia de tesis: el impedimento observado es de automatización. Los enlaces exactos y DOI encontrados permiten continuar cuando exista una vía institucional permitida.

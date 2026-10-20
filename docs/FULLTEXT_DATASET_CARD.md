# Ficha de la capa PDF y corpus derivado · v0.2

## Finalidad y alcance

La capa de texto completo añade originales recuperados y transformaciones locales al snapshot estable de **225 metadatos**. Permite lectura, búsqueda léxica, fragmentación trazable y preparación de nuevos proyectos. No modifica los metadatos congelados ni incorpora el piloto solapado de diez como obras nuevas. No crea etiquetas de uso de IA ni entrena modelos.

La cobertura efectiva se calcula en [`reports/corpus_summary.json`](../reports/corpus_summary.json), a partir de los archivos presentes en cada ejecución. El informe distingue trabajos catalogados, trabajos con PDF de checksum verificado, trabajos con texto, documentos/versiones, páginas y chunks. Esos denominadores no son intercambiables; no se presupone acceso o texto para todos los trabajos.

## Entradas y procedencia

| Entrada | Unidad | Tratamiento |
|---|---|---|
| `data/research_225/spain.jsonl`, `global.jsonl` | Trabajo identificado por `id` | Lectura sin modificación; control de IDs únicos |
| `data/fulltext/sources_spain.jsonl`, `sources_global.jsonl` | Resultado de recuperación por `record_id`, con estado y `files[]` | Conservar estado de origen; unir al snapshot por ID, no por semejanza de título |
| `data/fulltext/pdf/{institution}/` | Archivo PDF original | Leer solo después de comprobar ruta, tamaño declarado y SHA-256; no editar ni reescribir |

Cada archivo del manifiesto indica `path` relativo al repositorio, `sha256`, `bytes`, `download_url` y derechos observados como `source_license` cuando estén disponibles. Una licencia ausente permanece desconocida; no se hereda una licencia CC0 de metadatos al PDF. La declaración y alcance de permiso de la capa correspondiente se documentan junto con la recuperación; el builder transporta esa evidencia y no la certifica de forma independiente.

Un registro de recuperación desconocido no crea un trabajo nuevo: se cuenta como incidencia. Un manifiesto aún no creado deja los trabajos en catálogo. Un manifiesto inválido se registra y no impide procesar el otro. Los conteos de errores están en el resumen, sin volcar texto o mensajes privados del PDF al log.

## Unidades de salida

| Archivo en `data/derived/` | Unidad y campos principales |
|---|---|
| `catalog.jsonl` | Una fila por trabajo: `record_id`, `metadata` original, `fulltext_status`, `source_statuses`, `document_ids`, conteos y `work_group_id` |
| `documents.jsonl` | Una fila por combinación trabajo/hash de PDF: `document_id`, `record_id`, `work_group_id`, `pdf_sha256`, ruta, URL, derechos, rol, estado y conteos de páginas/texto |
| `pages.jsonl` | Una página: `page_id`, documento, trabajo, página desde 1, `text`, estado, hash del texto y procedencia PDF |
| `chunks.jsonl` | Un fragmento de una página: IDs, página, `start_char`, `end_char`, texto, hash, hash de página/PDF, fuente y derechos |
| `corpus.sqlite` | Tablas `metadata`, `documents`, `pages`, `chunks`, `corpus_info`; índice `chunks_fts` si SQLite ofrece FTS5 |
| `corpus_summary.json` | Informe de entradas/salidas por hash, cobertura, errores, parámetros y capacidad de búsqueda; copia en `reports/` |

Los documentos iguales por hash dentro de un trabajo se procesan una vez, aunque varias entradas del manifiesto los referencien. PDFs distintos del mismo trabajo permanecen como documentos/versiones separados con un mismo `work_group_id`. Un hash compartido por trabajos diferentes permite reutilizar extracción, pero sus documentos, páginas y chunks conservan IDs distintos y no se mezclan entre obras. Revisar esos hashes compartidos al dividir conjuntos de evaluación.

## Extracción, offsets y caché

El extractor es `pypdf`; se registran su versión y `page-nfc-v1`. Normaliza Unicode a NFC, conserva saltos de línea, homogeneiza CR/LF y elimina NUL. No reconstruye tablas ni interpreta imágenes. Los offsets son **caracteres Unicode del texto normalizado de la página**, base cero e intervalo semiabierto `[start_char, end_char)`; no son posiciones en bytes del PDF, coordenadas visuales o tokens de un modelo.

La condición verificable de cada chunk es:

```python
chunk['text'] == page['text'][chunk['start_char']:chunk['end_char']]
```

La fragmentación no cruza página ni documento. La configuración predeterminada es 1800 caracteres y 200 de solapamiento, con preferencia por separadores cercanos de párrafo, línea o espacio. Un chunk cita la página fuente, sus hashes y la licencia observada del documento.

La caché de extracción está en `data/derived/.cache/`, identificada por hash PDF y versiones del extractor/normalización. Antes de reutilizarla se validan sus hashes de texto. Cambiar el contenido original invalida el checksum; cambiar versión de `pypdf` o de normalización cambia la clave. Cambiar tamaño/solapamiento de chunks rehace la fragmentación sobre las páginas extraídas. La caché contiene texto completo y tiene el mismo alcance de acceso que el resto de derivados.

## Estados y ausencias

| Estado | Significado |
|---|---|
| `not_downloaded` en catálogo | No hay un candidato PDF local declarado para ese trabajo; consultar el estado de recuperación original |
| `text_extracted` | Todas las páginas procesadas del documento contienen texto extraíble; no certifica fidelidad de fórmulas, tablas o lectura visual |
| `partial_text` | Hay texto, pero también páginas sin texto, con error o documentos asociados no procesables |
| `ocr_needed` | No hay texto utilizable en la página/documento; puede ser escaneo o página vacía. OCR no ejecutado |
| `unusable_pdf` en catálogo | Hay candidatos, pero ninguno aporta texto; consultar documentos y códigos de error |
| `checksum_mismatch`, `size_mismatch`, `missing_file` | El archivo local no coincide con lo declarado o no está presente; no se extrae |
| `unsafe_path`, `not_pdf_path`, `missing_or_invalid_sha256` | Manifiesto insuficiente o ruta no admitida; no se abre el candidato |
| `parse_error`, `page_error`, `encrypted`, `dependency_missing` | Error de lectura, página, contraseña o dependencia; no se inventa texto |

Un PDF con checksum verificado puede seguir siendo ilegible, cifrado o escaneado. `records_with_verified_pdf` mide integridad del archivo declarado, no lectura completa. Una página sin texto no recibe una transcripción simulada. Los errores se aíslan para que otras obras continúen; los reintentos no duplican filas del corpus.

## Búsqueda y reutilización

FTS5 indexa texto de chunks con tokenización Unicode y ofrece ranking BM25 y fragmentos citables. Cuando no está disponible se utiliza búsqueda literal `LIKE`, identificada expresamente como fallback; no equivale a búsqueda semántica. La consulta no modifica SQLite. [REUTILIZAR.md](REUTILIZAR.md) ofrece comandos, filtros y ejemplos Python/SQLite para RAG y análisis.

El año de `metadata` mantiene su significado original. No se convierte en fecha académica al indexarlo. La selección por disponibilidad de PDF y calidad de extracción puede sesgar idiomas, disciplinas, instituciones y periodos; informar cobertura antes de comparar resultados.

## Derechos, privacidad y uso previsto

Los PDFs y derivados preservan las condiciones de sus fuentes y el alcance documentado de la operación, separado de la licencia MIT del código y de CC BY de documentos propios. No se asigna una licencia nueva a las tesis. La capa original de metadatos mantiene su `PERMISSIONS.json` y sus hashes; esta ampliación no reescribe esos archivos.

El texto extraído puede contener nombres, firmas o contactos presentes en los originales. El corpus textual no se presenta como anonimizado. Los logs de extracción informan códigos y conteos, sin mensajes de excepción que puedan incluir pasajes o contactos; las búsquedas devuelven los extractos solicitados como contenido, con localizadores de fuente.

Uso previsto: consulta, recuperación de evidencia, análisis documental y preparación de experimentos trazables. No hay verdad de referencia supervisada sobre uso real de IA, autoría, plagio, integridad o calidad. No se entrenan pesos en esta versión. Para entrenamiento o evaluación posterior, dividir por obra y por hash duplicado, conservar versiones/anexos en el mismo grupo, documentar condiciones y evaluar con datos reservados.

## Mantenimiento y pruebas

Los originales y derivados grandes se mantienen fuera del historial Git. Conservar manifiestos, hashes y permisos junto al paquete de datos de cada versión. El código y la configuración permiten reconstruir derivados; las fuentes remotas pueden cambiar y no se promete que repetir una descarga futura recupere los mismos bytes.

Las pruebas usan fixtures sintéticos, separados de todo dato científico. Comprueban verificación de checksum antes de extraer, offsets Unicode, aislamiento entre páginas/obras, caché íntegra, rutas confinadas, tratamiento de OCR y errores, búsqueda con filtros y ausencia de contenido privado en diagnósticos. La extracción automática requiere revisión visual de la página original cuando una afirmación dependa de diseño, fórmula, tabla o figura.

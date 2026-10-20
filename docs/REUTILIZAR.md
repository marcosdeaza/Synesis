# Reutilizar Synesis en otro proyecto

Synesis ofrece una colección estable de **225 metadatos**, una capa separada de PDFs recuperados y derivados que permiten buscar, filtrar y preparar experimentos. El piloto CC0 de diez registros está incluido entre los 225 y no se concatena como si fueran obras nuevas. Los recuentos reales de texto disponible, páginas, errores y chunks se calculan en [`reports/corpus_summary.json`](../reports/corpus_summary.json) cada vez que se construye el corpus; no se presupone que los 225 tengan PDF o texto extraíble.

## Elegir la capa adecuada

| Necesidad | Entrada | Qué representa |
|---|---|---|
| Bibliografía, filtros y cobertura | `data/research_225/spain.jsonl` y `global.jsonl` | Metadatos congelados; una fila por trabajo, con fechas y derechos observados |
| Comprobar disponibilidad del texto | `data/derived/catalog.jsonl` | Los mismos trabajos con estado de recuperación/extracción y enlaces a documentos |
| Leer una página con procedencia | `data/derived/pages.jsonl` | Texto extraído por página del PDF, con SHA-256 y estado |
| Preparar recuperación de fragmentos | `data/derived/chunks.jsonl` | Fragmentos que nunca cruzan página ni obra, con offsets y hashes |
| Buscar o combinar filtros sin cargar todo | `data/derived/corpus.sqlite` | Tablas de metadatos, documentos, páginas y chunks; índice FTS5 cuando está disponible |
| Ver PDF, licencia y errores de origen | `data/fulltext/sources_spain.jsonl` y `sources_global.jsonl` | Manifiestos de recuperación con estado y archivos; conservar su procedencia |

Los derivados grandes y PDFs no se incorporan al historial Git. Se construyen localmente o se obtienen del paquete de datos de la versión que corresponda. El código no descarga archivos por el hecho de construir o buscar. La ficha del [texto completo](FULLTEXT_DATASET_CARD.md) describe las unidades y limitaciones; la [ficha de metadatos](DATASET_CARD.md) conserva las del snapshot original.

## Descargar una versión lista

[Release v0.2.0](https://github.com/marcosdeaza/Synesis/releases/tag/v0.2.0) incluye metadatos, corpus procesado y paquetes de originales por institución. Después de clonar el repositorio:

```sh
python3 scripts/download_release.py --tag v0.2.0
python3 scripts/download_release.py --tag v0.2.0 --pdfs
```

El primer comando obtiene metadatos y derivados; el segundo añade los originales. El descargador valida SHA-256 y tamaño antes de extraer. Los ZIP conservan las rutas desde la raíz del repositorio. Consultar [PUBLICACION.md](PUBLICACION.md) y `SHA256SUMS` en la release para descargas manuales.

## Construir localmente

Se necesita Python 3.11 o posterior y `pypdf` para extraer texto de PDFs. SQLite, JSONL, hashes, caché y búsqueda usan la biblioteca estándar. No hacen falta claves, API de modelos, servidor de vectores, pandas o Parquet.

```sh
python3 -m pip install -e ".[corpus]"
python3 scripts/build_corpus.py
```

El builder lee los dos archivos originales de `research_225` y los manifiestos de `fulltext`; no modifica el snapshot ni los PDFs. Un manifiesto aún no creado es admisible: el catálogo conserva el trabajo sin inventar disponibilidad. Una vez descargados nuevos documentos, repetir el comando actualiza los derivados. La extracción correcta se reutiliza desde una caché por hash, versión de `pypdf` y versión de normalización. Los fallos de PDF no bloquean otras obras.

La salida predeterminada es `data/derived/`. Para cambiar fragmentación o destino:

```sh
python3 scripts/build_corpus.py --max-chars 1800 --overlap 200
python3 scripts/build_corpus.py --output data/derived-experiment
```

`max-chars` mide caracteres Unicode, no tokens del modelo. Debe ser positivo y el solapamiento menor que él. Cambiar estos parámetros genera chunks diferentes; registrar configuración y hashes al compartir un experimento. Un destino alternativo puede contener texto completo y debe mantenerse fuera de Git igual que el destino predeterminado.

`reports/corpus_summary.json` registra entradas y hashes, configuración, disponibilidad, errores, capacidad FTS5 y hashes de las salidas. El resumen también se conserva junto a los derivados. Para retomar una construcción interrumpida, ejecutar otra vez: los PDFs se vuelven a comprobar por checksum y las extracciones válidas de caché se reutilizan. El índice y las tablas se reconstruyen en un área temporal y se sustituyen al finalizar; no se añaden filas duplicadas a un índice antiguo.

## Buscar con citas de página

```sh
python3 scripts/search_corpus.py 'inteligencia artificial' --limit 5
python3 scripts/search_corpus.py 'rehabilitación' --institution uev --degree master --limit 5
python3 scripts/search_corpus.py 'machine learning' --year-min 2023 --literal --limit 10
```

FTS5 acepta su sintaxis de palabras, frases entre comillas y operadores; `--literal` trata la consulta como una frase. Si SQLite no dispone de FTS5, el buscador indica `literal_like_fallback` y usa una coincidencia literal más limitada. No presenta ese fallback como ranking BM25 ni como búsqueda semántica. La búsqueda abre SQLite en modo de solo lectura.

Cada resultado identifica `record_id`, `document_id`, página, chunk, offsets, título, fuente y ruta del PDF. Verificar el pasaje en la página original antes de citarlo: tablas, fórmulas, columnas, ligaduras y figuras pueden perder información durante la extracción. Un resultado vacío indica ausencia en el texto indexado y en esa consulta, sin demostrar ausencia en la tesis.

**Los filtros de año utilizan el año del metadato.** No lo convierten en fecha de defensa o exposición a IA. Para una comparación académica hay que revisar `academic_date_verified` y la evidencia temporal, además del [plan de análisis](PLAN_ANALISIS.md).

## Cargar las unidades en Python

Cargar metadatos requiere solo la biblioteca estándar:

```python
from pathlib import Path
import json

root = Path('.')
metadata = [
    json.loads(line)
    for name in ('spain.jsonl', 'global.jsonl')
    for line in (root / 'data/research_225' / name).read_text(encoding='utf-8').splitlines()
    if line.strip()
]
by_id = {row['id']: row for row in metadata}
assert len(by_id) == len(metadata)  # no concatenar el piloto de diez
```

Para RAG, leer chunks de manera incremental y llevar los localizadores al sistema de recuperación:

```python
with open('data/derived/chunks.jsonl', encoding='utf-8') as stream:
    for line in stream:
        chunk = json.loads(line)
        text = chunk['text']
        provenance = {
            key: chunk[key] for key in (
                'chunk_id', 'record_id', 'work_group_id', 'document_id',
                'page_number', 'start_char', 'end_char', 'pdf_sha256',
                'source_url', 'source_license'
            )
        }
        # Entregar text + provenance al índice elegido por tu proyecto.
```

No se incluyen embeddings ni pesos entrenados. Generarlos es una operación posterior que debe registrar modelo exacto, configuración, datos utilizados y condiciones de uso. El permiso y las licencias del PDF no se sustituyen por la licencia del software. Los originales pueden contener nombres, firmas o contactos aunque el snapshot de metadatos omita esos campos; el corpus textual no se presenta como anónimo.

SQLite permite filtrar antes de exportar o vectorizar:

```python
import sqlite3

connection = sqlite3.connect('file:data/derived/corpus.sqlite?mode=ro', uri=True)
rows = connection.execute('''
    SELECT c.chunk_id, c.record_id, c.page_number, c.text, m.source_url
    FROM chunks c JOIN metadata m ON m.record_id = c.record_id
    WHERE m.institution_id = ? AND m.degree_level = ?
    ORDER BY c.record_id, c.page_number, c.start_char
''', ('uev', 'master'))
for row in rows:
    pass  # Guardar solo la selección y el alcance necesarios.
connection.close()
```

## Particiones y evaluación que no mezclen obras

- Dividir por `work_group_id` **antes** de repartir páginas o chunks. El grupo conserva juntos todos los PDFs, versiones y anexos asociados al mismo trabajo.
- Agrupar también hashes `pdf_sha256` idénticos que aparezcan asociados a distintos registros; la caché compartida no implica que esos registros sean observaciones independientes.
- Revisar versiones o duplicados entre repositorios. Compartir título no basta para fusionarlos, y tener identificadores distintos no descarta duplicación de contenido.
- Para evaluación temporal, separar cohortes académicas verificadas y conservar los desconocidos fuera de afirmaciones temporales que no puedan sostener.
- Mantener fuera del entrenamiento las preguntas y páginas usadas para evaluación; ajustar umbrales y prompts con validación, no con el test final.
- En RAG evaluar localización de evidencia, precisión de citas, recuperación y respuestas sin apoyo. Un texto recuperado no prueba que una respuesta sea correcta.

Estos son materiales de investigación, **no un conjunto supervisado de verdad de referencia**. No hay etiquetas humanas finalizadas de uso real de IA, autoría, plagio o calidad. Una mención en el texto y una fecha posterior a ChatGPT no producen tales etiquetas. Las pruebas de software usan fixtures sintéticos separados del corpus científico.

## Mantener una versión reutilizable

Guardar, junto al experimento, el manifiesto del snapshot, los manifiestos PDF, el resumen calculado y las reglas de selección. Conservar el PDF original por hash; no reconstruirlo a partir de chunks. Registrar errores y páginas sin texto en vez de rellenarlas. El estado `ocr_needed` señala que no se extrajo texto utilizable, posiblemente por escaneo o página vacía; esta versión no ejecuta OCR ni finge haber recuperado ese contenido.

Al citar un pasaje, incluir trabajo, documento, página y fuente. Al compartir un derivado, mantener derechos y procedencia y revisar el alcance de esa distribución. El corpus puede apoyar nuevos proyectos de búsqueda, análisis o evaluación; sus sesgos de selección, fechas y acceso deben viajar con él.

## Parquet

El paquete de corpus contiene también `catalog.parquet`, `documents.parquet`, `pages.parquet` y `chunks.parquet`. Las columnas principales tienen tipos explícitos; `record_json` conserva todos los campos de la fila JSONL original. Para reconstruirlos, instalar `.[parquet]` y ejecutar `python3 scripts/export_parquet.py`. Parquet no añade una licencia nueva a los textos.

```python
import pyarrow.parquet as pq
catalog = pq.read_table('data/derived/catalog.parquet')
assert catalog.num_rows == 225
```

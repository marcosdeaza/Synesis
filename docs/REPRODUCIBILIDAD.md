# Reproducir Synesis · v0.2.0

## Entorno

Python 3.11 o posterior; CI usa3.12. Extracción fijada en pypdf 6.10.0, Parquet en PyArrow 26.0.0 y figuras en Matplotlib 3.9.4/NumPy 2.0.2. Instalar únicamente lo necesario:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[corpus,parquet,figures]'
make reproduce
```

`make reproduce` no consulta universidades: valida los 225 originales y sus hashes, reproduce el piloto histórico10, calcula señales de metadatos225 y cola sin etiquetas, valida el ledger de adquisición completo y ejecuta pruebas con fixtures sintéticos separados de los datos científicos. CI comprueba que los informes versionados no cambien. Los PDFs no se descargan en CI.

Sin `make`, ejecutar `python -m synesis.cli check`, `python scripts/check_research_snapshot.py`, `python scripts/prepare_research.py`, `python scripts/check_fulltext.py` y `python -m unittest discover -s tests -v` después de instalar el paquete.

## Descargar y reconstruir

```sh
python scripts/download_release.py --tag v0.2.0 --pdfs
python scripts/check_fulltext.py --require-files
python scripts/build_corpus.py
python scripts/export_parquet.py
python scripts/render_collection.py
python scripts/search_corpus.py 'inteligencia artificial' --limit 5
```

El corpus se reconstruye en `data/derived/` con caché por SHA del PDF, versión de extractor y normalización. Cada página conserva localizador y hash; cada chunk conserva offsets Unicode `[inicio,fin)`, sin cruzar página u obra. Se reemplazan las salidas al finalizar, sin insertar duplicados en un índice previo. El resumen registra los hashes de entradas y salidas. La validación con `--require-files` verifica todos los archivos declarados; el modo predeterminado permite validar el ledger sin descargar los assets.

JSONL conserva objetos completos; Parquet tiene columnas tipadas y `record_json` para el objeto completo. SQLite incluye metadatos, documentos, páginas, chunks y búsqueda FTS5 cuando está disponible. Si falta FTS5, el buscador informa de su modo literal alternativo.

`make figures` regenera tanto las figuras históricas del piloto 10 como las nuevas de cobertura 225. Las tablas numéricas y denominadores se mantienen separados. Los binarios de figuras pueden variar con fuentes y renderizadores; no se presentan como prueba de identidad del corpus.

## Volver a las universidades

```sh
python scripts/acquire_spain.py
python scripts/acquire_global.py
```

Las adquisiciones son operaciones con red, separadas de la reproducción offline. Revisan robots, identifican el proyecto, espacian solicitudes y preservan los estados de restricción; se reanudan mediante manifiestos por registro. Documentación: [España](ADQUISICION_ESPANA.md), [comparadores](ADQUISICION_GLOBAL.md). Las fichas pueden cambiar; reconstruir desde originales con hashes no equivale a recuperar otra vez bytes idénticos de una fuente dinámica.

El cosechador OAI `synesis harvest` sigue disponible para nuevos snapshots bajo `data/harvests/` ignorado. Exige institución, set, contacto y límites explícitos. `--metadata-prefix dim` conserva calificadores de fecha; filtros OAI `from`/`until` se refieren a modificación, no a defensa. La muestra original225 permanece sin sobrescribir.

## Revisión y límites

Las pruebas protegen hashes, rutas, restricciones, duplicados, filtros, Unicode, offsets, citas y separación de obras; los fallos de extracción no se convierten en texto vacío supuesto. Estados `ocr_needed` o parciales se conservan; esta versión no ejecuta OCR ni inventa texto.

M0 detecta menciones léxicas en título y materias; no acredita uso. Los225 siguen siendo una muestra de conveniencia, con fechas de repositorio heterogéneas. Para comparar antes/después se necesitan cobertura y fechas académicas verificadas, anotación humana y el [plan de análisis](PLAN_ANALISIS.md). No hay pesos entrenados, conclusiones causales ni un dataset supervisado de uso real de IA.

# Synesis · continuidad pública

**Estado actual:** repositorio público [marcosdeaza/Synesis](https://github.com/marcosdeaza/Synesis), rama `main`. Publicada y verificada la carpeta `data/research_225/` por petición expresa del responsable, que confirma disponer de permiso para publicarla y para investigación y eventual entrenamiento. Se conserva aparte el piloto CC0 de diez registros.

La auditoría contiene 225 registros reales. La carpeta `data/research_225/` publica el snapshot completo (UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10, USP 5), con el permiso confirmado por el responsable en `PERMISSIONS.json`. `data/pilot/` conserva el subconjunto de diez registros con CC0 y evidencia verificable. Los diez están incluidos entre los 225; la unión no es 235.

La memoria operativa completa del origen se denomina `CONTEXTO.md`; deliberadamente no se incluye en esta distribución. Este archivo conserva el contexto necesario para continuar con los materiales públicos, sin afirmar acceso al inventario local completo.

## Decisiones que deben mantenerse

- Español principal. Universidad Europea de Valencia obligatoria en el diseño; UEV y UPV prioritarias para el trabajo de campo local. Sus 90 registros ahora están publicados en `data/research_225/spain.jsonl` por autorización confirmada del responsable.
- Metadatos, tesis, código y documentación tienen derechos distintos. CC0 de los metadatos seleccionados no se extiende a las obras ni a corpus de entrenamiento. Cada nueva fuente requiere evidencia y revisión por operación.
- No inferir uso de IA por estilo, detectores, fecha o menciones temáticas. No atribuir cambios a IA solo por proximidad temporal.
- No confundir emisión en repositorio, defensa, redacción o depósito. El subconjunto TU Berlin no tiene fecha académica confirmada y procede de trabajos seleccionados por nota y aval; no representa la producción total.
- Las auditorías históricas de `docs/FUENTES_*` describen el inventario local. `reports/PILOTO.md` y las figuras actuales describen el subconjunto CC0 de diez; `reports/research_225_validation.json` valida por separado los 225 registros de investigación.
- No incorporar datos de prueba al corpus; mantener autores, correos, abstracts y PDF fuera de la distribución actual.

## Cómo retomar

1. Leer `README.md`, `docs/PUBLICACION.md`, el protocolo y las fuentes.
2. Ejecutar `make reproduce`, sin red ni credenciales. Revisar el manifiesto y las incidencias.
3. Para ampliar, registrar licencia de metadatos, evidencia, condiciones técnicas, operación permitida y semántica de fechas antes de extraer o publicar datos.
4. Cambiar gráficos y denominadores según el corpus efectivamente distribuido. No reutilizar figuras del inventario local como si fueran resultados públicos.
5. Registrar cada decisión nueva en este archivo y mantener protocolo, diccionario, permisos y pruebas consistentes.

Pendientes: documentar nuevas operaciones sobre texto completo del núcleo valenciano, auditar fechas académicas, balancear cohortes/disciplinas, anotar evidencia humana y prerregistrar antes de análisis confirmatorio. No se han entrenado modelos con estos trabajos. El investigador confirmó visibilidad pública; la distribución remota está en https://github.com/marcosdeaza/Synesis. El exportador por sí solo no realiza publicación remota.


## Verificación de entrega · 16 de octubre de 2026

Exportación real completada: 10/10 registros TU Berlin, cero incidencias; 20/20 pruebas de software correctas. Figuras de composición, cobertura y cronología regeneradas para esta variante en PNG/SVG/PDF. Cero enlaces Markdown internos rotos. Cuaderno entregado sin outputs ni adjuntos.

En la entrega local anterior a la publicación, la carpeta estaba inicializada sin commit ni remoto, con autenticación e identidad por resolver; ese estado quedó superado por la publicación registrada abajo. La memoria local completa se conserva fuera de esta variante. El siguiente paso científico es documentar nuevas operaciones sobre texto completo del núcleo valenciano y verificar fechas; la publicación inicial ya se completó; su ampliación posterior se registra abajo.


## Publicación autorizada · 16 de octubre de 2026

- El usuario confirmó publicar código, documentación y únicamente el subconjunto de metadatos autorizado.
- Autenticación comprobada; cuenta efectiva `marcosdeaza`. Creado el repositorio público https://github.com/marcosdeaza/Synesis.
- Configurada identidad Git local con el nombre verificado de la cuenta y su dirección noreply de GitHub; no se atribuye con ello revisión o responsabilidad científica institucional.
- Alcance de datos conservado: diez registros TU Berlin, metadatos CC0 con evidencia. Los otros 215 registros locales no se incorporan al historial público.
- Actualizados README, cita y guía de publicación. Primer commit y push completados. La visibilidad pública y la rama `main` se verificaron mediante API de GitHub. Reproducción remota confirmada: [ejecución correcta](https://github.com/marcosdeaza/Synesis/actions/runs/38865478996), 20 pruebas y cero incidencias. Siguiente paso científico: cerrar permisos y semántica temporal del núcleo valenciano.

- Comprobación final de publicación: GitHub Actions completó correctamente el primer commit. Código y dataset publicados; no quedan pasos de autenticación o visibilidad pendientes.


## Ampliación pública a 225 registros · 16 de octubre de 2026

- Petición directa del investigador: subir los 225 registros en una carpeta para investigación y posible entrenamiento; confirma que dispone de permiso. No se solicitó otra aprobación.
- Incorporados `data/research_225/spain.jsonl` (190) y `global.jsonl` (35), idénticos byte a byte a los snapshots originales. `manifest.json` registra hashes, composición y solapamiento; `PERMISSIONS.json` conserva la declaración y su alcance sin asignar una licencia abierta nueva.
- Sin PDFs, resúmenes, campos de autoría ni emails. No se ha entrenado un modelo. Los 225 son metadatos reales, no 225 documentos completos.
- `make reproduce` ahora valida ambas colecciones por separado: hashes, 225 identidades únicas, recuentos, minimización y solapamiento exacto de los diez CC0. Las figuras y el análisis del piloto CC0 siguen sobre diez; no se presentan como resultados de 225.
- Las restricciones iniciales de distribución a solo diez corresponden a la entrega histórica anterior. La decisión posterior del responsable amplía el alcance publicado a 225 mediante una autorización documentada distinta de CC0.
- Publicación completada en el commit `21d4955`. GitHub verificó los 225 registros, las 20 pruebas existentes y la reproducción del piloto sin diferencias: [ejecución correcta](https://github.com/marcosdeaza/Synesis/actions/runs/38866772837). Se descargaron los dos archivos desde la API de GitHub y sus hashes y recuentos coinciden con los originales.
- Siguiente paso: definir el experimento que vaya a usar estos metadatos; no se ha iniciado entrenamiento en esta petición.


## Fase v0.2 · recopilación y reutilización · 20 de octubre de 2026

El investigador pide terminar Synesis como paquete muy reutilizable, incluyendo PDFs, más datasets y mecanismos para proyectos. La petición amplía explícitamente el trabajo a texto completo y recopilación de documentos, manteniendo la procedencia y las condiciones de cada fuente. Los snapshots `research_225` siguen congelados e idénticos; la capa nueva está en `data/fulltext/` y sus derivados en `data/derived/`.

La carpeta de trabajo anterior ya no estaba presente en el equipo. Se recuperó el repositorio público desde GitHub; los 225 registros sí estaban publicados y se restauraron íntegros. La identidad Git se configuró solo para este repositorio con el perfil y noreply verificados.

Trabajo en paralelo:
- España: revisar los 190 registros UEV/UPV, recuperar PDF principal y anexos públicos y registrar restricciones reales sin eludir accesos.
- Internacional: revisar los 35 comparadores, resolver especialmente los títulos HKUST a registros/PID y recuperar documentos institucionales disponibles.
- Corpus: extracción readonly por página, fragmentos con offsets y hashes, catálogo de 225, SQLite/FTS y CLI de búsqueda, con caché y errores explícitos.
- Integración: cliente HTTP común con robots/demoras/redirecciones, validación, documentación, paquetes de descarga y publicación versionada.

Criterio de entrega: cada uno de los 225 debe tener un estado documentado; los documentos obtenidos deben validarse por firma, hash y parser. Un acceso cerrado o un enlace no encontrado no se presenta como PDF recuperado. Los PDFs originales y los derivados voluminosos se distribuirán en paquetes versionados, fuera del historial Git del código; los manifiestos permiten reconstruir y comprobar el corpus. No se inventan declaraciones de uso de IA, no se han entrenado pesos y no se afirma causalidad.

Siguiente paso en curso: adquisición completa, integración del corpus y comprobación de cobertura/calidad antes de empaquetar. Actualizar esta sección con cifras medidas y enlaces de entrega al cerrar.


## Cierre de la v0.2.0 · 20 de octubre de 2026

La sesión anterior se interrumpió por límite de uso con España a medias (137 de 190). Se reanudó con `scripts/acquire_spain.py` (reanudable por registro) hasta completar los 190; `scripts/acquire_global.py` ya había cerrado los 35 comparadores.

Cifras medidas (fuente: `reports/fulltext_coverage.json` y `reports/corpus_summary.json`):

| Institución | Registros | Con PDF | Otros estados |
|---|---:|---:|---|
| UEV | 90 | 86 | 1 restringido, 1 PDF inválido, 1 no encontrado, 1 error HTTP |
| UPV | 100 | 47 (114 archivos con anexos) | 53 restringidos en origen |
| MIT | 10 | 10 | |
| TU Berlin | 10 | 10 | |
| USP | 5 | 5 | |
| HKUST | 10 | 0 | 10 `robots_disallowed` |
| **Total** | **225** | **158** | 225 archivos, 2.409.858.880 bytes |

Corpus: 13.558 páginas, 20.204 chunks (1800 caracteres, solape 200), 22.231.767 caracteres; 153 documentos con texto, 40 con texto parcial y 32 `ocr_needed` (no se ejecutó OCR). Cero incidencias de extracción. Búsqueda FTS5 con cita de página comprobada con consultas reales. 54 pruebas de software correctas (se cerraron conexiones SQLite en `tests/test_corpus.py`).

Paquetes de la release v0.2.0: metadatos, corpus (JSONL, SQLite FTS5, Parquet), PDFs por institución en partes de unos 250 MiB (UPV en 10), `SHA256SUMS` y `synesis-release-manifest.json`. Se verificó `shasum -c` local antes de publicar. Los derivados y PDFs no están en el historial Git (`data/derived/`, `data/fulltext/pdf/`, `release/`, `work/` ignorados).

Observación para quien reutilice: muchos trabajos UEV llevan licencia CC BY-NC-ND y otros tienen derechos reservados o licencia desconocida; la licencia queda por archivo en `data/fulltext/sources_*.jsonl`. La declaración del responsable (`data/fulltext/PERMISSIONS.json`) no la sustituye.

Pendientes: OCR de los 32 documentos escaneados (decidir motor y registrar versión), reintentar los 53 UPV restringidos solo si el repositorio cambia su política, HKUST solo con autorización explícita o API permitida, auditoría de fechas académicas, anotación humana usando `reports/annotation_queue.csv`, y prerregistro antes de cualquier análisis confirmatorio. No se han entrenado modelos ni se han creado etiquetas de uso de IA.

Corrección de empaquetado (20/10/2026, antes de difundir la release): el primer `synesis-v0.2.0-metadata.zip` se generó antes de añadir esta sección y contenía una versión anterior de este archivo, por lo que `download_release.py` rechazó la extracción con `existing_file_conflict`. Se regeneraron y sustituyeron los assets afectados (metadatos, manifiesto y `SHA256SUMS`); la comprobación de integridad funcionó como debe. Regla para el futuro: empaquetar siempre después de cerrar la documentación.

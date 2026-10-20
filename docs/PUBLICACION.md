# Publicación y paquetes · v0.2.0

El código, documentación, 225 metadatos y manifiestos de adquisición están en [GitHub](https://github.com/marcosdeaza/Synesis). Los PDFs y derivados se entregan como archivos de la [release v0.2.0](https://github.com/marcosdeaza/Synesis/releases/tag/v0.2.0), fuera del historial Git para mantener una clonación ligera.

## Elegir una descarga

| Paquete | Contenido | Destino al extraer desde la raíz |
|---|---|---|
| Metadatos | Snapshot225, manifiestos, permisos, informes y documentación | `data/research_225/`, `data/fulltext/`, `reports/`, `docs/` |
| Corpus | Catálogo225, documentos, texto por página, chunks, SQLite FTS5 y Parquet | `data/derived/` |
| PDFs por institución y parte | Originales principales y anexos recuperados, sin alterar sus bytes | `data/fulltext/pdf/<institución>/` |
| Manifiesto y SHA256SUMS | Nombre, tamaño y SHA-256 de cada paquete | Verificación antes de extraer |

Los nombres exactos se consultan en `synesis-release-manifest.json`. Todos los paquetes conservan rutas relativas a la raíz. Se puede descargar solo el corpus para buscar; los originales permiten verificar visualmente los pasajes y reconstruir la extracción.

```sh
python3 scripts/download_release.py --tag v0.2.0
python3 scripts/download_release.py --tag v0.2.0 --pdfs
```

Los dos comandos verifican tamaño y SHA-256 y rechazan rutas inseguras en ZIP. También es posible descargar manualmente los assets de GitHub y comprobar `SHA256SUMS` antes de extraerlos. No se necesitan credenciales para la release pública.

## Qué se ha recopilado

225 referencias únicas: UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10 y USP 5. Los diez del piloto CC0 ya están incluidos: no hay 235 obras. Las cifras finales de trabajos con PDF, archivos, bytes y estados están en [`fulltext_coverage.json`](../reports/fulltext_coverage.json); las páginas, extracción y chunks están en [`corpus_summary.json`](../reports/corpus_summary.json).

Cada uno de los 225 tiene un estado de consulta. Un trabajo puede tener varios PDFs, y una adquisición puede ser parcial si algún anexo está restringido: revisar `notes`. Una restricción real se registra, sin inventar una descarga. HKUST mantiene una prohibición explícita de robots para este cliente. El inventario documentado de faltantes no se sustituye por PDFs de otros trabajos.

## Autorización, derechos y privacidad

La publicación pública y los 225 metadatos se solicitaron por el responsable, quien confirmó disponer de permiso para investigación y eventual entrenamiento. La petición del 20/10/2026 amplía el trabajo a PDFs y derivados reutilizables. Las declaraciones se conservan separadas en [`research_225/PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) y [`fulltext/PERMISSIONS.json`](../data/fulltext/PERMISSIONS.json). No se inventan contratos ni verificación institucional.

Las licencias de origen permanecen por archivo. La declaración del responsable no asigna CC0 ni MIT a obras ajenas, y no concede a cualquier tercero todos los usos posibles. [RIGHTS.md](../RIGHTS.md) explica las capas. Los PDFs pueden identificar autores y contener contactos aunque el snapshot de metadatos omita esos campos. No se ha entrenado un modelo ni se publican etiquetas verificadas de uso de IA.

## Mantener una versión

1. Mantener congelados los dos JSONL de `research_225`; una nueva muestra necesita su propio snapshot.
2. Completar/adaptar los manifiestos por documento y comprobar con `python3 scripts/check_fulltext.py --require-files`.
3. Construir corpus y Parquet; ejecutar `make reproduce`, comprobar cobertura y búsquedas con páginas reales.
4. Ejecutar `python3 scripts/package_release.py --help` y generar los paquetes de una versión nueva. No sobrescribir assets publicados sin registrar una corrección.
5. Publicar código, tag y archivos de la release, verificar su lectura pública y registrar enlaces/cambios en `CONTEXTO_PUBLICO.md`.

El exportador histórico `scripts/export_public.py` selecciona únicamente una base de metadatos CC0. No es el empaquetador v0.2 ni debe usarse para actualizar el repositorio actual o copiar automáticamente toda una carpeta local. Cachés, páginas brutas, ZIP de trabajo, credenciales y anotaciones privadas permanecen ignorados.

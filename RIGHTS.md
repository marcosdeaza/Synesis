# Derechos por material

| Material | Condición de esta versión |
|---|---|
| Código propio en `src/`, `scripts/`, pruebas y configuración de software | MIT, texto en `LICENSE` |
| Protocolo, documentación, instrumentos y figuras analíticas propios | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); atribuir a Synesis y enlazar la versión utilizada |
| Banner | Generado con ImageGen el 16/10/2026; procedencia y prompt en `assets/PROVENANCE.md`. Ilustración editorial, no dato científico |
| Colección pública `data/research_225/` | 225 metadatos publicados por solicitud y permiso confirmado por el responsable; declaración y origen en [PERMISSIONS.json](data/research_225/PERMISSIONS.json), sin validación independiente ni autorización institucional verificada |
| Piloto `data/pilot/rights_cleared.jsonl` | 10 metadatos de TU Berlin con evidencia institucional CC0-1.0; ya incluidos entre los 225 |
| Metadatos de terceros en ambas colecciones | Derechos por fuente/campo; no se relicencian bajo MIT o CC BY por estar aquí. La declaración del responsable no se transforma en CC0 |
| PDFs originales y anexos recuperados | Paquetes de la release v0.2.0, a petición del responsable; licencia y evidencia por archivo en `data/fulltext/sources_*.jsonl` y declaración en `data/fulltext/PERMISSIONS.json` |
| Texto por página, chunks, SQLite y Parquet | Derivados de los PDFs; conservan la procedencia y condiciones de las obras, sin licencia abierta universal nueva |
| Marcas y nombres de universidades/proveedores | Identificación de fuentes; no afiliación, patrocinio ni licencia de marcas |

`license` se refiere a una licencia explícita de la obra cuando el registro la aporta; `metadata_license` se refiere a metadatos. Un enlace de colección, un aviso InC o `openAccess` no son una licencia abierta. Un valor nulo significa desconocido.

Se publican dos colecciones: los 225 metadatos de investigación según la autorización confirmada por el responsable, y el piloto de 10 con licencia explícita de metadatos CC0 verificada. Los 10 se solapan íntegramente con los 225; no son 235 trabajos distintos. El permiso declarado se registra sin inventar emisor institucional, documento contractual, condiciones de sublicencia ni otros detalles no aportados. Las licencias observadas en las fuentes permanecen en sus campos originales. Esta declaración no concede por sí misma una licencia abierta universal a terceros ni se extiende a PDFs, resúmenes o textos completos ausentes del paquete.

El [manifiesto de la colección completa](data/research_225/manifest.json) corresponde a 225 registros. `PUBLIC_EXPORT_MANIFEST.json` describe la exportación base CC0, y `reports/manifest.json` identifica las 10 entradas del pipeline. Las notas de auditoría y los hashes se publican sin distribuir las respuestas brutas. No se ha entrenado un modelo con los trabajos; cualquier modelo posterior deberá documentar qué colección y campos utilizó y con qué alcance.

No se incluyen campos de autoría o contacto en la salida, pero un título o Handle puede llevar al autor. La minimización de datos no es anonimización. Las peticiones de corrección o retirada deben canalizarse mediante los mecanismos del repositorio cuando se publique, sin exponer información sensible en issues públicos.

## Ampliación a texto completo · 20 de octubre de 2026

La petición posterior del responsable amplía la distribución a los documentos universitarios públicos recuperables y sus derivados reutilizables. La declaración separada en [`data/fulltext/PERMISSIONS.json`](data/fulltext/PERMISSIONS.json) registra esa instrucción, sin inventar contratos ni conceder licencias nuevas. Las limitaciones a PDFs del párrafo histórico anterior describían la colección inicial de metadatos; la capa `fulltext` y los paquetes v0.2.0 documentan la ampliación.

`source_license` conserva la condición de obra observada por documento; los metadatos CC0 de TU Berlin no convierten sus tesis en CC0. Hay obras con condiciones NC/ND, derechos reservados o licencia desconocida. La posibilidad de descargar esta release no concede automáticamente a terceros cualquier reutilización comercial, entrenamiento o redistribución de derivados. El software MIT sigue siendo reutilizable conforme a su licencia.

Los originales pueden incluir nombres, firmas, direcciones o información que la extracción conserve. El snapshot de metadatos sigue minimizado; los PDFs y el texto completo no se presentan como anónimos. Mantener hashes, enlace de fuente, licencia y localizador de página al reutilizar. No se eluden acceso restringido ni prohibiciones explícitas de robots; los estados y faltantes se publican con el denominador de 225.

Esta clasificación describe el alcance de esta versión y las condiciones observadas en las fuentes; no sustituye una revisión institucional específica para un nuevo uso.

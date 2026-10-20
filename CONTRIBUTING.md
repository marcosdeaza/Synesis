# Contribuir a Synesis

Antes de proponer cambios, leer [CONTEXTO.md](CONTEXTO.md), el [protocolo](docs/PROTOCOLO.md) y la ficha de la fuente afectada. Un fork debe mantener las distinciones entre fecha académica y depósito, mención y uso declarado, acceso y derechos de reutilización.

Cada nueva fuente necesita URL institucional, alcance de niveles, cobertura y selección, endpoint verificado o mecanismo de consulta permitido, condiciones de acceso y permisos por operación. Una respuesta HTTP 403 o una restricción de robots se documenta; no se elude. No recoger autores o correos electrónicos cuando no sean necesarios para las preguntas del estudio.

Los datos nuevos deben ser reales y guardar identificador persistente, procedencia y fecha de consulta. Conservar originales en almacenamiento local ignorado y añadir hashes al manifiesto. No completar campus, nivel, año, licencia o declaración de IA con suposiciones. Documentar las exclusiones y el método de selección antes de comparar grupos.

La distribución actual contiene dos colecciones: `data/research_225/` publica 225 metadatos con permiso confirmado por el responsable, registrado en su `PERMISSIONS.json`; `data/pilot/rights_cleared.jsonl` conserva diez metadatos CC0 para el análisis reproducible. Los diez ya están incluidos entre los 225. Mantener ambas procedencias y sus manifiestos, sin convertir la declaración del responsable en una licencia CC0 ni cambiar las licencias observadas de origen. No añadir PDFs, resúmenes o campos personales como si formaran parte de ese alcance.

Desde v0.2.0 hay una capa separada de PDFs y derivados, expresamente solicitada por el responsable y documentada en `data/fulltext/PERMISSIONS.json`. Los originales se empaquetan en releases; no se añaden al snapshot ni al historial Git. Cada archivo conserva fuente, hash, tamaño y condiciones. No publicar materiales restringidos ni convertir los permisos de la colección en una licencia universal.

Una contribución revisable explica el problema, la evidencia, el cambio y su validación. Instalar `.[corpus]` y ejecutar `make reproduce`, que valida los 225, el ledger PDF, las señales de metadatos y por separado el piloto de diez. Si cambian datos o figuras, indicar qué colección afecta el cambio, actualizar su manifiesto y regenerar las salidas correspondientes. No añadir tests que simplemente repitan una expresión: comprobar errores que puedan cambiar la interpretación o comprometer la minimización.

Etiquetas de trabajo sugeridas: `source-audit`, `date-semantics`, `rights-review`, `annotation`, `analysis`, `reproducibility`, `translation`. No publicar tesis completas o incidencias que expongan información sensible en una issue.

No hay todavía responsables científicos identificados, afiliación institucional, aprobación ética ni revisión por pares. Esas atribuciones se completarán cuando las personas e instituciones correspondientes las confirmen. Registrar cada nueva decisión en `CONTEXTO.md`.

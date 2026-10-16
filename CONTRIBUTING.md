# Contribuir a Synesis

Antes de proponer cambios, leer [CONTEXTO.md](CONTEXTO.md), el [protocolo](docs/PROTOCOLO.md) y la ficha de la fuente afectada. Un fork debe mantener las distinciones entre fecha académica y depósito, mención y uso declarado, acceso y derechos de reutilización.

Cada nueva fuente necesita URL institucional, alcance de niveles, cobertura y selección, endpoint verificado o mecanismo de consulta permitido, condiciones de acceso y permisos por operación. Una respuesta HTTP 403 o una restricción de robots se documenta; no se elude. No recoger autores o correos electrónicos cuando no sean necesarios para las preguntas del estudio.

Los datos nuevos deben ser reales y guardar identificador persistente, procedencia y fecha de consulta. Conservar originales en almacenamiento local ignorado y añadir hashes al manifiesto. No completar campus, nivel, año, licencia o declaración de IA con suposiciones. Documentar las exclusiones y el método de selección antes de comparar grupos.

Una contribución revisable explica el problema, la evidencia, el cambio y su validación. Ejecutar `make reproduce`; si cambian datos o figuras, regenerar tablas y gráficos y actualizar la ficha. No añadir tests que simplemente repitan una expresión: comprobar errores que puedan cambiar la interpretación o comprometer la minimización.

Etiquetas de trabajo sugeridas: `source-audit`, `date-semantics`, `rights-review`, `annotation`, `analysis`, `reproducibility`, `translation`. No publicar tesis completas o incidencias que expongan información sensible en una issue.

No hay todavía responsables científicos identificados, afiliación institucional, aprobación ética ni revisión por pares. Esas atribuciones se completarán cuando las personas e instituciones correspondientes las confirmen. Registrar cada nueva decisión en `CONTEXTO.md`.

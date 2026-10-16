# Verificación de entrega v0.1.0

16 de octubre de 2026. Python 3.12.14, biblioteca estándar.

- `make reproduce`: correcto; 20 pruebas automatizadas correctas.
- Validación de registros: cero incidencias; ver el recuento y los hashes de esta variante en `manifest.json`.
- Enlaces Markdown internos: cero destinos ausentes.
- Figuras: renderizadas desde los datos de esta variante e inspeccionadas visualmente; PNG, SVG y PDF.
- No hay etiquetas humanas finalizadas, modelos entrenados, efectos causales ni revisión por pares.
- Publicación pública comprobada en https://github.com/marcosdeaza/Synesis.
- Reproducción remota correcta: https://github.com/marcosdeaza/Synesis/actions/runs/38865478996 (20 pruebas y reconstrucción sin cambios).


## Snapshot completo de investigación

- Añadida la carpeta `data/research_225/` por instrucción del responsable, que confirma permiso.
- Validación local completa: 225 registros únicos, cero incidencias, hashes idénticos a los dos snapshots originales.
- Los diez registros del piloto CC0 son un subconjunto idéntico; unión de 225 trabajos, sin doble contabilización.
- `make reproduce` valida también este snapshot; el informe está en `research_225_validation.json`.
- Comprobación negativa de integridad: un cambio de bytes fue rechazado por discrepancia de checksum.

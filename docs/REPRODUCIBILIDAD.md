# Reproducción y procedencia técnica

## Operaciones y colecciones distintas

| Operación | Red | Resultado |
|---|---|---|
| Validar la colección completa | No | 225 metadatos en `data/research_225/` → comprobación de esquema, unicidad, recuentos y hashes; informe `reports/research_225_validation.json` |
| Reproducir el análisis piloto | No | Diez metadatos CC0 de `data/pilot/rights_cleared.jsonl` → señales, tablas, informes y manifiesto del pipeline |
| Volver a consultar una fuente | Sí, respetando condiciones | Captura nueva, potencialmente distinta por migraciones, correcciones y orden del servidor |
| Publicar colecciones | No se activa por consultar | Los 225 ya están autorizados por el responsable y se distribuyen con permiso y manifiesto propios; el piloto CC0 conserva su evidencia institucional |

## Entorno

Python 3.11+ para el paquete; prueba principal realizada con Python 3.12.14 y biblioteca estándar. Figuras exportadas con Matplotlib 3.9.4 y NumPy 2.0.2 (renderizador disponible Python 3.9 en el entorno de creación). Las versiones de las dependencias de figuras están fijadas en `pyproject.toml`. PNG/SVG/PDF pueden variar en metadatos binarios o fuentes entre sistemas, aunque sus tablas no cambien.

```bash
make reproduce
python3 -m pip install -e '.[figures]'
make figures
```

`make reproduce` ejecuta ambas comprobaciones: reconstruye el análisis del piloto de diez y valida por separado los 225 mediante `scripts/check_research_snapshot.py`, además de las pruebas. Las figuras analíticas siguen usando exclusivamente las tablas del piloto. Los diez se solapan con la colección completa; no se concatenan para contar 235 trabajos.

Para verificar únicamente la carpeta completa:

```bash
python3 scripts/check_research_snapshot.py
```

El comprobador contrasta [`data/research_225/manifest.json`](../data/research_225/manifest.json), los archivos y la procedencia del permiso en [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json). La validación de integridad no se presenta como validación independiente del permiso declarado por el responsable. Los campos de licencias de origen permanecen intactos.

En Windows sin `make`, usar los dos comandos Python del README y `python scripts/render_figures.py`, configurando `PYTHONPATH=src` según la terminal. Las pruebas usan fixtures marcados como tales; no entran en el corpus.

## Cosechador OAI

`synesis harvest` solo acepta una institución registrada con endpoint verificado, un set explícito y un contacto público real. Comprueba robots, respeta intervalos de consulta, limita 20 páginas por ejecución y no sigue tokens repetidos. Reintenta errores transitorios de manera acotada y registra cada página y su SHA-256. La salida debe estar bajo `data/harvests/`, en un directorio que aún no exista, ignorado por Git.

`--metadata-prefix dim` conserva calificadores de DSpace y es la opción para reproducir el mecanismo usado en UEV/UPV. `oai_dc` pierde calificadores de fechas; el conector conserva esa ambigüedad. Los filtros `from`/`until` se aplican a la modificación OAI, no a defensa. Un endpoint Identify verificado no garantiza que cualquier set o prefijo funcione: comprobar `ListSets` y `ListMetadataFormats` antes de ampliar.

No todos los comparadores tienen el mismo mecanismo: MIT/TU usan API de DSpace para campos cualificados; USP usa fichas HTML verificadas tras problemas de paginación; HKUST usa un listado oficial de departamento tras restricciones del portal. Las peticiones de origen y las reglas están documentadas en las fichas. Esta versión no promete un conector automático general para esos cuatro mecanismos.

El piloto minimizado de diez permite repetir las transformaciones analíticas entregadas; la carpeta de 225 permite verificar la integridad de la colección completa publicada. No se atribuyen a los 225 las señales o figuras calculadas únicamente sobre diez. La captura original no se declara reproducible byte a byte desde Internet: las fuentes son dinámicas y los brutos contienen campos que no se redistribuyen.

## Verificación y revisión

Las pruebas protegen contra inferir autoría de una coincidencia léxica, convertir desconocidos en negativos, aceptar duplicados o fechas imposibles y filtrar mal niveles de titulación. Los informes no excluyen silenciosamente filas inválidas: registran incidencias y la comprobación falla si las hay.

La integración automática reproduce el piloto y valida la carpeta de 225 sin red ni claves, comprobando los resultados y la integridad de archivos versionados. No automatiza scraping periódico ni publicación de datos nuevos. Antes de ampliar las pruebas, debe existir un cambio o riesgo concreto que las justifique.

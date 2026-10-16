# Índice de fuentes y operaciones

Fecha de auditoría: **16 de octubre de 2026**. Se consultaron directamente repositorios, servicios OAI, fichas de biblioteca, normativa y listados oficiales. El inventario reúne 13 instituciones: 9 españolas y 4 comparadores. Seis aportan los **225 registros publicados** en [`research_225`](../data/research_225/). Los detalles de peticiones, selección y hashes están en [España](FUENTES_ESPANA.md) e [internacionales](FUENTES_GLOBALES.md).

La publicación de los 225 y su uso investigacional o entrenamiento posterior sobre esos metadatos cuentan con confirmación del responsable, registrada en [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json). Es una declaración del responsable, sin validación independiente ni documentos institucionales de permiso en el repositorio. No altera las licencias observadas de la tabla. El piloto de diez metadatos CC0 de TU Berlin se mantiene separado para el pipeline; esos diez ya están incluidos entre los 225.

## Matriz resumida

`Verificado` describe una evidencia observada en la fuente. `Pendiente` no equivale a una prohibición ni a un permiso. Una API accesible no concede todas las reutilizaciones. La columna de entrenamiento se refiere a las tesis y contenido documental; la confirmación del responsable sobre los metadatos publicados se registra por separado. Esta versión no descarga PDFs.

| Fuente | Captura inicial | Metadatos / reutilización observada en la fuente | Contenido documental | Entrenamiento sobre tesis |
|---|---:|---|---|---|
| TITULA · UEV | 90 | OAI DIM verificado, comunidad UEV explícita; licencia general de metadatos sin verificar | Acceso y licencia de obra por registro; se publican metadatos minimizados, sin textos | Pendiente |
| RiuNet · UPV | 100 | OAI DIM verificado; licencia de metadatos general sin verificar | Accesos abiertos/cerrados y licencias por obra; se publican metadatos minimizados, sin textos | Pendiente |
| MIT DSpace | 10 | Política CC0 para metadatos creados por biblioteca; campos de autor pueden diferir | Resúmenes omitidos; el alcance sobre cada campo requiere revisión | Pendiente |
| TU Berlin DepositOnce | 10 | Ayuda institucional declara CC0 para metadatos; evidencia en cada fila | Derechos de tesis separados; restricciones de aplicaciones IA sobre contenidos | No se infiere permiso para entrenar sobre tesis |
| USP BDTD | 5 | OAI/listados y HTML verificados; sin licencia general de metadatos confirmada | Condiciones de documento para investigación/enseñanza y atribución; `publico` es acceso | Pendiente |
| HKUST SOSC | 10 | Listado oficial de títulos/años; licencia de metadatos sin verificar | Portal 403/OAI con bucle; no se eluden. Sin abstracts/PDF | Pendiente |
| UAB DDD | 0 | Identify declara CC0 para metadatos | Licencia del texto por obra; expansión pendiente | Revisión por material |
| UPM Archivo Digital | 0 | Identify permite cosecha OAI de metadatos | Prohíbe cosecha de texto completo | No habilitado |
| UJI | 0 | OAI verificado, sin cosecha de registros | Revisión pendiente | Pendiente |
| UV, UPC, UAM, UCM | 0 | Fuentes oficiales identificadas; endpoint o acceso por resolver | No se amplía hasta completar auditoría | Pendiente |

La selección automática del **piloto CC0** exige `metadata_license=CC0-1.0` y enlace explícito de evidencia: diez registros de TU Berlin. La política de MIT es condicional al origen de los campos y no se usa para incorporarlo automáticamente a ese piloto. Sus diez registros sí forman parte de la colección completa de 225, publicada mediante la confirmación del responsable. El código y la documentación propios tienen una licencia independiente. [Publicación](PUBLICACION.md) · [Derechos](../RIGHTS.md).

## Tres niveles que no deben confundirse

1. **Colección de investigación:** los 225 metadatos minimizados ya publicados, con procedencia, derechos observados y declaración del responsable preservados; respuestas brutas solo en almacenamiento local.
2. **Resultados propios:** protocolo, código, manifiestos, descripciones de cobertura y bibliografía; no incluyen por defecto los contenidos capturados.
3. **Operación y material concretos:** el permiso confirmado para publicación e investigación/entrenamiento posterior de esos metadatos no se extrapola a tesis, resúmenes o PDFs. La licencia de una tesis y la de sus metadatos son distintas; no se ha entrenado un modelo en esta versión.

## Otras webs universitarias útiles

Además de los registros de tesis, se leyeron las [guías de TFG/TFM de UPV](https://upv-es.libguides.com/recursos-tfg-tfm/riunet), la [normativa institucional de Universidad Europea](https://universidadeuropea.com/conocenos/normativa/), la [FAQ de TITULA](https://titula.universidadeuropea.es/page/faq?locale-attribute=es), la [política de metadatos MIT](https://libraries.mit.edu/about/policies/open-metadata-policy/) y la [ayuda de DepositOnce](https://depositonce.tu-berlin.de/info/help). Estas fuentes describen selección, fechas, acceso y permisos; no se interpretan como declaraciones de uso de IA de cada estudiante.

La siguiente expansión incorporará versiones históricas de normas de IA y calendarios académicos para estudiar los incentivos de declaración. Una página vigente en 2026 no se atribuirá retrospectivamente a 2021. Los hitos de proveedores y la bibliografía metodológica se registran separadamente en [CRONOLOGIA.md](CRONOLOGIA.md) y [BIBLIOGRAFIA.bib](BIBLIOGRAFIA.bib).

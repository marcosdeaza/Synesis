# Índice de fuentes y operaciones

Fecha de auditoría: **16 de octubre de 2026**. Se consultaron directamente repositorios, servicios OAI, fichas de biblioteca, normativa y listados oficiales. El inventario reúne 13 instituciones: 9 españolas y 4 comparadores. Solo 6 aportan registros al piloto local. Los detalles de peticiones, selección y hashes están en [España](FUENTES_ESPANA.md) e [internacionales](FUENTES_GLOBALES.md).

## Matriz resumida

`Verificado` describe una evidencia observada. `Pendiente` no equivale a una prohibición ni a un permiso. Una API accesible no concede todas las reutilizaciones. Esta versión no descarga PDFs.

| Fuente | Captura piloto | Metadatos / reutilización observada | Texto y redistribución | Entrenamiento |
|---|---:|---|---|---|
| TITULA · UEV | 90 | OAI DIM verificado, comunidad UEV explícita; licencia general de metadatos sin verificar | Acceso y licencia de obra por registro; corpus local minimizado, fuera de exportación pública por ahora | Pendiente |
| RiuNet · UPV | 100 | OAI DIM verificado; licencia de metadatos general sin verificar | Accesos abiertos/cerrados y licencias por obra; corpus local minimizado | Pendiente |
| MIT DSpace | 10 | Política CC0 para metadatos creados por biblioteca; campos de autor pueden diferir | Resúmenes omitidos; el alcance sobre cada campo requiere revisión | Pendiente |
| TU Berlin DepositOnce | 10 | Ayuda institucional declara CC0 para metadatos; evidencia en cada fila | Derechos de tesis separados; restricciones de aplicaciones IA sobre contenidos | No se infiere permiso para entrenar sobre tesis |
| USP BDTD | 5 | OAI/listados y HTML verificados; sin licencia general de metadatos confirmada | Condiciones de documento para investigación/enseñanza y atribución; `publico` es acceso | Pendiente |
| HKUST SOSC | 10 | Listado oficial de títulos/años; licencia de metadatos sin verificar | Portal 403/OAI con bucle; no se eluden. Sin abstracts/PDF | Pendiente |
| UAB DDD | 0 | Identify declara CC0 para metadatos | Licencia del texto por obra; expansión pendiente | Revisión por material |
| UPM Archivo Digital | 0 | Identify permite cosecha OAI de metadatos | Prohíbe cosecha de texto completo | No habilitado |
| UJI | 0 | OAI verificado, sin cosecha de registros | Revisión pendiente | Pendiente |
| UV, UPC, UAM, UCM | 0 | Fuentes oficiales identificadas; endpoint o acceso por resolver | No se amplía hasta completar auditoría | Pendiente |

La selección automática para el paquete público exige `metadata_license=CC0-1.0` y enlace explícito de evidencia: actualmente 10 registros de TU Berlin. La política de MIT es condicional al origen de los campos; no se incluye automáticamente. El código y la documentación propios pueden publicarse con su licencia independiente. [Publicación](PUBLICACION.md) · [Derechos](../RIGHTS.md).

## Tres niveles que no deben confundirse

1. **Inventario de investigación local:** referencias y metadatos mínimos para auditar fuentes, con derechos y desconocidos preservados.
2. **Resultados propios:** protocolo, código, manifiestos, descripciones de cobertura y bibliografía; no incluyen por defecto los contenidos capturados.
3. **Dataset redistribuido o de entrenamiento:** campos y obras cuyo fundamento y alcance se han revisado específicamente. La licencia de una tesis y la de sus metadatos son distintas.

## Otras webs universitarias útiles

Además de los registros de tesis, se leyeron las [guías de TFG/TFM de UPV](https://upv-es.libguides.com/recursos-tfg-tfm/riunet), la [normativa institucional de Universidad Europea](https://universidadeuropea.com/conocenos/normativa/), la [FAQ de TITULA](https://titula.universidadeuropea.es/page/faq?locale-attribute=es), la [política de metadatos MIT](https://libraries.mit.edu/about/policies/open-metadata-policy/) y la [ayuda de DepositOnce](https://depositonce.tu-berlin.de/info/help). Estas fuentes describen selección, fechas, acceso y permisos; no se interpretan como declaraciones de uso de IA de cada estudiante.

La siguiente expansión incorporará versiones históricas de normas de IA y calendarios académicos para estudiar los incentivos de declaración. Una página vigente en 2026 no se atribuirá retrospectivamente a 2021. Los hitos de proveedores y la bibliografía metodológica se registran separadamente en [CRONOLOGIA.md](CRONOLOGIA.md) y [BIBLIOGRAFIA.bib](BIBLIOGRAFIA.bib).

# Adquisición de documentos completos · España

Capa de trabajo local iniciada el **20 de octubre de 2026** por petición expresa del investigador. Amplía la operación a documentos completos sin modificar los 190 metadatos españoles de `data/research_225/spain.jsonl` ni el snapshot histórico de 225 registros. Los originales PDF no se incorporan automáticamente a Git ni se publican desde este módulo.

El objetivo operativo es examinar **todos los 190 registros**: 90 de Universidad Europea de Valencia y 100 de Universitat Politècnica de València. «Examinado» no significa «PDF obtenido». Cada registro termina con un estado verificable y, cuando lo hay, uno o varios originales con SHA-256, tamaño, URL solicitada, URL final y evidencia de licencia. No se entrenan modelos ni se infiere uso de IA a partir de estos documentos.

## Vías oficiales comprobadas

- **UEV / TITULA, DSpace 6:** la ficha institucional de cada Handle ofrece enlaces `/bitstream/handle/…/archivo.pdf?sequence=…`. Se leen los enlaces visibles y `citation_pdf_url`; se prefiere el enlace visible para evitar duplicar el mismo archivo por dos alias. La ficha y sus metadatos explicitan la condición de acceso y, cuando consta, una URI Creative Commons.
- **UPV / RiuNet, DSpace 7:** los Handles redirigen a `/entities/publication/UUID`. La página pública proporciona enlaces de signposting `<link rel="item" type="application/pdf">` y enlaces visibles `/bitstreams/UUID/download`. Se consideran los PDF principales y anexos. La resolución pública `https://riunet.upv.es/server/api/pid/find?id=10251%2F…` también se comprobó como vía oficial de identificación; no es un acceso privado ni elude políticas de archivo.
- Cuando una memoria solo se ofrece en un **ZIP público**, se recupera ese archivo y se inspeccionan sus miembros PDF. Los bytes de cada PDF se extraen intactos a un nombre local generado; el manifiesto conserva `archive_member` y `archive_sha256`. No se extraen rutas arbitrarias, ejecutables ni archivos ajenos a PDF. Se limita el tamaño y la expansión de miembros.

Las [reglas de TITULA](https://titula.universidadeuropea.es/robots.txt) y de [RiuNet](https://riunet.upv.es/robots.txt) se verifican mediante el cliente compartido antes de solicitar recursos. Se identifica el proyecto y se aplica una espera mínima de tres segundos por origen, ampliada por `Crawl-delay` y `Request-rate`. Hay dos trabajadores, uno por institución; dentro de cada institución se procesan los registros secuencialmente. Los errores transitorios admiten reintentos limitados y se respeta `Retry-After`.

## Acceso y límites

Un valor `openAccess` en el snapshot antiguo no sustituye un GET actual. Solo se registra `downloaded` cuando se ha obtenido un PDF real; respuestas HTML, formularios de inicio de sesión o errores no se guardan como PDF. Una ficha que declara actualmente `restrictedAccess`, `closedAccess` o `embargoedAccess` queda restringida, aunque incluya un enlace técnico a un bitstream. Los enlaces `request-a-copy` tampoco se solicitan: no se envían peticiones a autores ni se usan credenciales, cookies de sesión o rutas adivinadas.

Esta distinción se comprobó expresamente: el UEV `20.500.12880/4071` conserva un enlace técnico y declara `restrictedAccess`; RiuNet presenta las memorias cerradas como solicitudes de copia, en ocasiones en formato ZIP. El programa mantiene la restricción y su evidencia. Si un mismo trabajo tiene un PDF público y un anexo restringido, el estado puede ser `downloaded`, pero `notes` declara cobertura parcial y los candidatos pendientes. No se presenta como adquisición completa de todos los anexos.

`source_license` conserva únicamente una licencia de obra observada en la ficha; `null` significa desconocida. Una declaración de reserva de derechos no se convierte en licencia abierta. Descargar un documento público para investigación no concede por sí mismo permiso de redistribución, entrenamiento, publicación de datos personales o cambio de licencia. Los originales pueden contener autoría y otros datos: esta capa no se presenta como una colección anonimizada. Los nombres locales usan identificadores de registro y hashes, mientras que las URL conservan la procedencia original.

Los PDF corresponden a los archivos ofrecidos por el repositorio en la fecha de adquisición. El año del metadato histórico no demuestra que esos mismos bytes estuvieran presentes en la defensa original: puede haber correcciones, versiones o depósitos posteriores. El hash fija la versión recuperada; no acredita su fecha de redacción. Las marcas `retrieved_at` usan UTC y pueden caer en el día anterior al 20 de octubre en el calendario UTC, mientras que la sesión del investigador está en Europe/Madrid.

## Ejecución y reanudación

Desde la raíz del repositorio, con Python y las dependencias del proyecto disponibles:

```sh
python scripts/acquire_spain.py
```

El comando lee el snapshot español y escribe `data/fulltext/sources_spain.jsonl`. Después de **cada registro** reemplaza atómicamente el manifiesto; una interrupción no elimina las filas ya cerradas. Los ficheros se descargan primero a `.part` y se renombran al finalizar. Los PDF completos quedan en modo de solo lectura bajo `data/fulltext/pdf/uev/` y `data/fulltext/pdf/upv/`, separados de los metadatos históricos.

La reanudación omite filas ya finalizadas; para `downloaded` comprueba existencia, tamaño y SHA-256. Se puede limitar una comprobación o volver a revisar errores concretos:

```sh
python scripts/acquire_spain.py --institution upv --limit 1
python scripts/acquire_spain.py --retry-status http_error --retry-status invalid_pdf --retry-incomplete
```

`--retry-incomplete` vuelve a examinar candidatos públicos fallidos de un registro que ya obtuvo otros PDF. La integridad de un archivo existente se comprueba con el hash del checkpoint; si no coincide, se conserva como sospechoso en el área de trabajo y se solicita de nuevo, sin bendecir los bytes alterados con un hash nuevo.

No es necesario reintentar restricciones conocidas para completar el inventario de estados. Una revisión posterior de una restricción requiere volver a comprobar la ficha actual; nunca presupone que haya desaparecido. La opción `--retry-status restricted` permite esa nueva comprobación legítima, sin intentar eludirla.

Los estados son `downloaded`, `restricted`, `not_found`, `robots_disallowed`, `http_error` e `invalid_pdf`. El manifiesto contiene una fila por identificador; `files` puede incluir varios PDF. Los aliases con bytes idénticos se deduplican por SHA-256 dentro del registro. Las copias brutas de las páginas y los ZIP se mantienen en el material de trabajo local `work/spain_fulltext_*`, sin mezclarlas con la distribución de metadatos.

## Resultado de esta ejecución

La adquisición está en curso. Los recuentos finales y las incidencias se añadirán al terminar los 190 registros. La fuente de verdad es `data/fulltext/sources_spain.jsonl`: no se afirma recuperación de un archivo antes de que exista una fila con su hash y tamaño.

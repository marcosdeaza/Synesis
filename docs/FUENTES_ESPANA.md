# Fuentes españolas de Synesis

Auditoría: **16 de octubre de 2026**. La captura española inicial contiene **190 registros reales de metadatos**: 90 de la Universidad Europea de Valencia (UEV, obligatoria) y 100 de la Universitat Politècnica de València (UPV). Ya se publican en [`data/research_225/spain.jsonl`](../data/research_225/spain.jsonl), dentro de la colección completa de 225. Los títulos proceden de respuestas OAI-PMH institucionales; no son ejemplos sintéticos. No se descargaron PDFs ni se exportaron autores, directores, correos o campos `contributor`. Se omiten los textos completos de los resúmenes.

El responsable confirmó permiso para publicar los 225 metadatos y usarlos en investigación y eventual entrenamiento; [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) registra esa declaración sin validación independiente ni autorización institucional verificada. Las licencias observadas abajo se conservan como evidencia de origen y no se convierten en CC0. El pipeline público sigue utilizando por separado diez registros CC0 de TU Berlin; este documento describe la captura española, no las entradas de ese pipeline.

## Qué demuestra este piloto

Demuestra que es viable recoger, normalizar y auditar metadatos públicos de las dos instituciones prioritarias. Es una **muestra de conveniencia de la primera página OAI**, sin aleatorización, sin paginar los `resumptionToken` y sin seleccionar por vocabulario de IA. No mide el uso real de IA, la calidad académica, el total de trabajos defendidos ni la prevalencia de ninguna práctica. La ausencia de una mención a IA en el título no prueba que no se utilizase IA durante el trabajo.

| Institución | Registros incluidos | Grado según metadatos | Máster según metadatos | Años declarados válidos | Fechas desconocidas |
|---|---:|---:|---:|---|---:|
| Universidad Europea de Valencia (`uev`) | 90 | 49 | 41 | 2022–2025 | 2 |
| Universitat Politècnica de València (`upv`) | 100 | 73 | 27 | 2011–2026 | 0 |
| **Total** | **190** | **122** | **68** | 2011–2026 | **2** |

La primera página de UEV devolvió 100 cabeceras OAI: se excluyeron 4 TFC explícitos, ajenos al ámbito TFG/TFM, y 6 registros borrados (`status=deleted`) sin metadatos. No se convirtieron en trabajos de nivel desconocido. La página de UPV devolvió 100 trabajos con `bachelorThesis` o `masterThesis`; no había tesis doctorales en ella. En UPV la etiqueta `bachelorThesis` puede incluir proyectos anteriores al EEES: un análisis de TFG modernos deberá revisar titulación y normativa, sin homologación automática.

## UEV: comunidad institucional verificada

La [comunidad 20 de TITULA](https://titula.universidadeuropea.es/handle/20.500.12880/20) se titula expresamente **Universidad Europea de Valencia**. [ListSets](https://titula.universidadeuropea.com/oai/request?verb=ListSets) confirma el set `com_20.500.12880_20` con nombre `2. Universidad Europea de Valencia`. El [Identify OAI](https://titula.universidadeuropea.com/oai/request?verb=Identify) identifica el repositorio como TITULA y declara la base `https://titula.universidadeuropea.com/oai/request`. El servicio también respondió en el dominio `.es`; se conserva la base canónica declarada en `.com` para el protocolo y el dominio `.es` para páginas legibles.

La [FAQ de TITULA](https://titula.universidadeuropea.es/page/faq?locale-attribute=es) indica que recoge TFG, TFM y TFC que cumplen criterios de calidad de la universidad y cuentan con permiso de sus autores. **El repositorio no equivale a un censo de todos los trabajos.** La comunidad 20 acredita la institución UEV, no el campus físico. La [página institucional de UEV](https://universidadeuropea.com/conocenos/valencia/) incluye Valencia y Alicante. Por ello todos los campos `campus` y `campus_evidence_url` del piloto permanecen `null`: no se infiere Valencia por dominio, nombre de universidad, temática o geografía estudiada.

La comunidad permite analizar facultades y titulaciones en fases posteriores. No debe sustituirse el set institucional por una única subcomunidad o colección y presentar el resultado como representativo de toda UEV.

## UPV: RiuNet y las fechas

[Identify](https://riunet.upv.es/server/oai/request?verb=Identify) confirmó la base `https://riunet.upv.es/server/oai/request`. [ListSets](https://riunet.upv.es/server/oai/request?verb=ListSets) identificó `com_10251_11261` como **Trabajos académicos**. La [guía bibliotecaria de TFG/TFM](https://upv-es.libguides.com/recursos-tfg-tfm/riunet) explica que RiuNet alberga trabajos académicos y que existen diferentes derechos y tipos de acceso.

El problema temporal más importante aparece en el propio piloto: **99 de 100 valores `dc.date.issued` de UPV coinciden con el día de `dc.date.accessioned`; los 100 difieren de `dc.date.created`.** Por tanto `year` se interpreta únicamente como **año declarado por el campo de publicación del repositorio**. No acredita fecha de defensa, inicio del trabajo o exposición a un producto de IA. Se conservan `created_raw` y `accessioned_raw` para análisis de sensibilidad posterior y revisión manual de la semántica institucional. Tampoco se declara un campus UPV por pertenencia a la institución, ubicación del objeto estudiado o nombre de la colección.

En UEV las 88 fechas válidas tienen precisión mensual. Un registro declara `No consta` y otro carece de `dc.date.issued`; ambos conservan `year=null`, `date_precision=unknown`. La precisión de día en UPV expresa precisión del metadato, no exactitud demostrada de la fecha de defensa.

## Registro de instituciones candidatas

Las siete instituciones adicionales se auditan como candidatas; sus registros no forman parte de estos 190 trabajos. `oai_base=null` significa **no verificado**, sin afirmar que la universidad carezca de OAI. Las ciudades describen la institución y nunca rellenan automáticamente el campus de un trabajo.

| ID | Institución / zona | Fuente oficial y alcance | Estado el 16/10/2026 |
|---|---|---|---|
| `uv` | Universitat de València / Valencia | [RODERIC](https://roderic.uv.es/items/4a2cd791-4287-437d-82ef-2d6183067643), [orientaciones de TFM que remiten a RODERIC](https://www.uv.es/mastermagis/tfm/Orientaciones_TFM.pdf) | Repositorio y TFM confirmados; prueba OAI `/rest/oai/request?verb=Identify`: HTTP 404. Base pendiente. |
| `uji` | Universitat Jaume I / Castellón | [Trabajos académicos](https://repositori.uji.es/handle/10234/158176), [TFG](https://repositori.uji.es/handle/10234/71324), [Identify](https://repositori.uji.es/server/oai/request?verb=Identify) | OAI verificado: `https://repositori.uji.es/server/oai/request`; sin cosecha piloto. |
| `upc` | Universitat Politècnica de Catalunya / Barcelona | [Bibliotècnica: trabajos de fin de estudios](https://bibliotecnica.upc.edu/colleccions/treballs-fi-estudis-upc) | TFG/TFM y proyectos anteriores al EEES confirmados; prueba OAI `/oai/request?verb=Identify`: tiempo de espera agotado. Base pendiente. |
| `uab` | Universitat Autònoma de Barcelona / Bellaterra | [TFG/TFM UAB](https://www.uab.cat/es/aprendizaje-servicio/tfg-tfm-en-curs), [Identify](https://ddd.uab.cat/oai2d?verb=Identify) | OAI verificado en HTTPS: `https://ddd.uab.cat/oai2d` (Identify declara base HTTP). Sin registros piloto. |
| `upm` | Universidad Politécnica de Madrid / Madrid | [Biblioteca: Archivo Digital](https://www.upm.es/biblioteca/archivo-digital-upm), [Identify](https://oa.upm.es/cgi/oai2?verb=Identify) | OAI verificado: `https://oa.upm.es/cgi/oai2`; sin registros piloto. |
| `uam` | Universidad Autónoma de Madrid / Madrid | [Biblos-e: depósito y licencias](https://www.uam.es/uam/vida-universitaria/bibliotecas/apoyo-investigacion/repositorio-institucional-deposito) | TFG/TFM confirmados; endpoint candidato `/server/oai/request?verb=Identify`: HTTP 403. No se eludió la respuesta. |
| `ucm` | Universidad Complutense de Madrid / Madrid | [Docta, TFG y TFM](https://biblioteca.ucm.es/inf/tfg-tfm), [normativa de depósito](https://biblioteca.ucm.es/fsl/normativa-tfg) | Docta es el repositorio actual. Endpoint candidato `/server/oai/request?verb=Identify`: HTTP 404. Base pendiente. |

No se utiliza `earliestDatestamp` de OAI como año de inicio de la producción académica: puede reflejar migraciones o indexaciones. UJI declara septiembre de 2026 y UPM febrero de 2023 en Identify, mientras que sus colecciones contienen trabajos anteriores.

## Acceso, licencias y reutilización

Se distinguen tres cosas: acceso a una página de metadatos, derechos sobre el trabajo y licencia de reutilización de los metadatos. **Acceso abierto no equivale por sí mismo a licencia abierta.** `license` contiene solamente una URI explícita Creative Commons hallada en el registro; puede referirse a la obra. `rights_statement` conserva declaraciones como InC por separado y `access_rights` conserva la condición de acceso del repositorio. Una licencia `null` significa desconocida, no dominio público.

TITULA publica [reglas de robots](https://titula.universidadeuropea.es/robots.txt) con demora de 3 segundos y exclusiones para búsqueda, navegación y estadísticas. Se utilizaron páginas de comunidad y el protocolo OAI, sin automatizar esas rutas excluidas. Las peticiones al mismo repositorio se espaciaron; no se paginaron miles de registros. [RiuNet robots](https://riunet.upv.es/robots.txt) también distingue páginas públicas de búsqueda, administración y procesos.

En el piloto hay 185 registros con algún campo de resumen en origen, pero **todos los valores `abstract` están a `null`**. `abstract_available` informa de la presencia del campo en origen; `abstract_omitted_by_policy=true` deja constancia de la omisión. Esa presencia no garantiza calidad: algunas descripciones son avisos administrativos o de confidencialidad. No hay bibliografías, citas completas con nombres, documentos adjuntos o PDFs en el dataset público. Los títulos conservan su naturaleza de metadatos; el esquema no publica campos de autoría. Un título y su enlace público pueden permitir encontrar al autor, de modo que esta minimización no se presenta como anonimización irreversible.

De los 90 registros UEV, 89 declaran `openAccess` y 1 `restrictedAccess`. De los 100 UPV, 47 declaran `openAccess` y 53 `closedAccess`. Esta diferencia no mide calidad ni intención de uso de IA y puede sesgar cualquier ampliación basada solo en textos completos disponibles.

Dos políticas verificadas facilitan una expansión responsable:

- [DDD UAB, Identify](https://ddd.uab.cat/oai2d?verb=Identify) declara metadatos con dedicación de dominio público [CC0](https://creativecommons.org/publicdomain/zero/1.0/) y licencias individuales para el texto completo.
- [Archivo Digital UPM, Identify](https://oa.upm.es/cgi/oai2?verb=Identify) permite cosechar metadatos a través de OAI y prohíbe la cosecha de texto completo. Esa prohibición debe conservarse al desarrollar cualquier conector.

No se aplica la licencia del código de Synesis a obras o metadatos de terceros. El permiso confirmado por el responsable incluye la publicación e investigación/entrenamiento futuro sobre los metadatos entregados, sin que se haya entrenado un modelo. No se extiende a resúmenes o textos completos: incorporarlos requeriría documentar un alcance distinto por repositorio y registro.

## Procedencia exacta y manifiesto

Las peticiones usaron `metadataPrefix=dim` para conservar calificadores como `dc.date.issued`, `dc.date.created`, `dc.type` y `dc.rights.accessRights`. El valor `retrieved_at` conserva `responseDate` de la respuesta OAI. Ambas respuestas incluyeron un `resumptionToken`: **solo se incorporó la primera página** y no se afirma cobertura exhaustiva. El orden de devolución del servidor no se interpreta como cronológico.

| Institución | Petición exacta | Respuesta UTC | Bytes | SHA-256 de la respuesta XML completa |
|---|---|---|---:|---|
| UEV | [ListRecords DIM, comunidad UEV](https://titula.universidadeuropea.com/oai/request?verb=ListRecords&metadataPrefix=dim&set=com_20.500.12880_20) | `2026-10-16T06:37:00Z` | 437943 | `b71be8692388b0c76a87c99ddb4fa5ce2b4c340f938d66da43aa00ce4ce4ac37` |
| UPV | [ListRecords DIM, Trabajos académicos](https://riunet.upv.es/server/oai/request?verb=ListRecords&metadataPrefix=dim&set=com_10251_11261) | `2026-10-16T06:37:05Z` | 842143 | `cfb804fbc8b2133bbb41e3fc9a23c46d58a452a0db7a7656c947016913d4823b` |

Las respuestas XML brutas se conservaron únicamente como material de trabajo local; contienen campos de autoría que se descartaron en la salida minimizada. No se incluyen como dataset público. El hash deja constancia de los bytes utilizados, pero una consulta futura puede producir una página distinta por cambios o reindexación. Repetir la consulta no garantiza reproducir esos mismos 190 trabajos; cada fila conserva su identificador OAI y un enlace de evidencia `GetRecord` para auditoría individual.

Exclusiones UEV por identificador local (todos bajo `oai:titula.universidadeuropea.com:20.500.12880/`):

| Motivo | Identificadores |
|---|---|
| TFC explícito | `5146`, `1592`, `5322`, `1438` |
| Cabecera OAI borrada, sin metadatos | `8845`, `1561`, `4156`, `8859`, `10039`, `10739` |

## Reglas de normalización y verificación

`degree_level` se obtiene exclusivamente de `TFG`/`bachelorThesis` o `TFM`/`masterThesis`; `degree_evidence` conserva el valor y, en UEV, la titulación declarada. No se deduce máster de la palabra «tesis». Las fechas conservan `issued_raw`; el normalizador acepta fecha ISO y variante año/mes, verifica el calendario y no completa un mes o un día faltante. `date_semantics=dc_date_issued` identifica el campo observado, sin atribuirle una fecha de defensa confirmada. Los metadatos inválidos o ausentes mantienen `year=null` y `date_semantics=unknown`.

Los títulos y materias se descodifican de entidades HTML y se normalizan en espacios; no se traducen ni se reescriben. Se conserva el título principal y no se mezclan sus traducciones alternativas como trabajos independientes. `subjects` elimina duplicados exactos manteniendo el orden del registro. `id` se construye con la institución y el identificador Handle, sin nombres personales. No se eliminan trabajos distintos solo por compartir título.

Comprobaciones del piloto: 190 IDs únicos, 190 identificadores OAI únicos, esquema consistente, ausencia de campos `contributor`, de correos en la salida y de resúmenes redistribuidos; 188 años válidos y 2 desconocidos. La siguiente fase necesita muestreo por universidad, disciplina, titulación y año; auditoría manual de fechas; denominadores de cobertura; y clasificación de menciones explícitas de herramientas. Comparar universidades sin esos controles mezclaría difusión institucional, selección de depósito y cambios reales en prácticas académicas.

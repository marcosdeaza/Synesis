# Auditoría internacional de fuentes de Synesis

> Auditoría histórica del 16/10. La adquisición posterior de PDFs y sus resultados se documentan en [ADQUISICION_ESPANA.md](ADQUISICION_ESPANA.md), [ADQUISICION_GLOBAL.md](ADQUISICION_GLOBAL.md) y los manifiestos de v0.2.0.

Consulta: **16 de octubre de 2026**. Esta auditoría identifica cuatro comparadores y aporta **35 registros bibliográficos reales**, publicados en [`data/research_225/global.jsonl`](../data/research_225/global.jsonl). La muestra prueba extracción, trazabilidad y diferencias entre fuentes. Es intencional y pequeña: sus proporciones **no estiman producción universitaria, prevalencia de IA ni efectos causales**. Se conservaron títulos, fechas, materias y evidencia de grado; no se descargaron PDF ni se publicaron autores, correos o resúmenes.

La colección completa de 225, incluidos estos 35, se publica por solicitud del responsable, quien confirmó que cuenta con permiso para publicación y uso investigacional o entrenamiento posterior de esos metadatos. [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) registra la declaración y su origen sin presentarla como validación independiente o autorización institucional verificada. Las licencias observadas de cada fuente se preservan. El piloto CC0 automatizado contiene por separado diez registros de TU Berlin, ya incluidos entre los 225.

| Comparador | Cobertura verificada | Piloto | Vía que respondió | Limitación principal |
|---|---|---:|---|---|
| MIT, Estados Unidos | bachelor y master | 10 | API JSON; OAI Identify y metadatos | Colección seleccionada, cobertura bachelor desigual; cambio de escaneo a recepción electrónica en 2020 |
| TU Berlin, Alemania | Bachelor Thesis y Master Thesis | 10 | API JSON; OAI Identify/ListSets | Sólo tesis estudiantiles con nota «very good» y aval; no es una muestra media de titulados |
| HKUST, Hong Kong SAR, China | master, Social Science | 10 | Listado anual oficial de departamento | Un solo departamento; año sin semántica de publicación; no representa China continental |
| USP, Brasil | dissertação de mestrado | 5 | Metadatos HTML; OAI Identify/ListSets | Mestrado de investigación distinto del TFM profesional; no incluye bachelor/TCC |

## Estados Unidos: MIT

[MIT Theses](https://dspace.mit.edu/communities/6fc02cc2-0d14-4023-8a6f-d9900d0c4302) declara que su colección no es completa y documenta la incorporación de nuevos máster/doctorado desde 2004, con recepción electrónica desde 2020. Se filtró grado mediante el campo `dc.description.degree`, excluyendo `Ph.D.`; `S.M.`/`M.Eng.`/`M.B.A.` se mapearon a master y `S.B.` a bachelor. Es una equivalencia operativa de nivel, no una homologación curricular.

El [Identify OAI](https://dspace.mit.edu/server/oai/request?verb=Identify) respondió XML válido; [ListMetadataFormats](https://dspace.mit.edu/server/oai/request?verb=ListMetadataFormats) anuncia, entre otros, `oai_dc` y `dim`. El lote OAI inicial mezclaba fechas no cualificadas de acceso y emisión. Para el piloto se usó la API con campos cualificados: cinco máster de 2019 y cuatro máster/un bachelor de 2024, seleccionados en orden de respuesta.

Consultas reproducibles:

```text
https://dspace.mit.edu/server/api/discover/search/objects?query=dc.date.issued%3A2019%20AND%20dc.type%3AThesis&size=20
https://dspace.mit.edu/server/api/discover/search/objects?query=dc.date.issued%3A2024%20AND%20dc.type%3AThesis&size=15
```

La [política Open Metadata](https://libraries.mit.edu/about/policies/open-metadata-policy/) distingue metadatos creados por la biblioteca, bajo CC0, de los creados por autores, que pueden conservar derechos. No se aplica una licencia CC0 indiscriminada a todos los campos ni a las tesis. Los abstracts se omiten.

## Alemania: TU Berlin

La [colección Publications](https://depositonce.tu-berlin.de/collections/da16560b-bd8b-4c34-a200-b139f21d9416/browse/dateissued) admite bachelor/master estudiantiles con nota «very good» y aval. Este filtro introduce un sesgo de selección que debe modelarse; el repositorio no permite inferir por sí solo la calidad media de los trabajos de la universidad.

[Identify](https://api-depositonce.tu-berlin.de/server/oai/request?verb=Identify) y [ListSets](https://api-depositonce.tu-berlin.de/server/oai/request?verb=ListSets) respondieron XML válido. El piloto usa cinco registros `Bachelor Thesis` y cinco `Master Thesis` de la API pública. Se excluyeron del muestreo de máster resultados históricos anteriores a 2018 que requerirían revisar equivalencia de titulaciones.

```text
https://api-depositonce.tu-berlin.de/server/api/discover/search/objects?query=dc.type%3A%28%22Master%20Thesis%22%20OR%20%22Bachelor%20Thesis%22%29&size=10
https://api-depositonce.tu-berlin.de/server/api/discover/search/objects?query=dc.type%3A%22Master%20Thesis%22%20AND%20dc.date.issued%3A%5B2018%20TO%202026%5D&size=5
```

La [ayuda oficial](https://depositonce.tu-berlin.de/info/help) publica los metadatos bajo CC0 y permite recuperarlos por interfaces abiertas. También explica medidas para reducir accesos de aplicaciones IA al contenido. Esta auditoría utilizó únicamente consultas limitadas de metadatos, sin PDF ni evasión de bloqueos. `metadata_license` registra CC0; `license` conserva únicamente una URI Creative Commons inequívoca de la obra, que puede ser distinta. Otras declaraciones de derechos se conservan en `rights_statement` y sus enlaces en `rights_reference_url`.

## Asia: HKUST, Hong Kong SAR, China

Se seleccionó HKUST como comparador asiático en **Hong Kong, Región Administrativa Especial de China**. No es una universidad de China continental ni un sustituto estadístico de ese sistema universitario. La extensión a China continental sigue pendiente.

La [biblioteca de HKUST](https://libguides.hkust.edu.hk/e-thesis/find) describe sus fondos de máster y doctorado. El [portal de investigación](https://researchportal.hkust.edu.hk/en/studentTheses/) devolvió 403 y la ruta OAI ensayada redirigió en bucle; no se eludieron esas respuestas ni se declara un endpoint OAI validado.

El [listado oficial de Master Theses de Social Science](https://sosc.hkust.edu.hk/research_n_facilities/master_theses) respondió y organiza títulos por años de 1994 a 2025. Se tomaron cinco títulos de 2019 y cinco de 2025. Todos enlazan a la sección anual correspondiente; `record_identifier` usa un hash local del título/año, **no un identificador persistente del repositorio**. No se observan abstracts en ese listado. `language=null` evita inferir un idioma catalogado a partir del título.

El [acuerdo de depósito](https://library.hkust.edu.hk/files/forms/thesis-agreement.pdf) conserva copyright de los autores. No se verificó licencia abierta de los metadatos de este listado: `metadata_license` y `license` permanecen en `null`.

## LATAM: USP, Brasil

La [BDTD de USP](https://www.teses.usp.br/index.php) incluye disertaciones de máster y tesis doctorales. [Identify](https://teses.usp.br/cgi-bin/oai.pl?verb=Identify) y [ListSets](https://teses.usp.br/cgi-bin/oai.pl?verb=ListSets) respondieron XML válido; este último declara `dissertations` como «Master's dissertations». Los intentos acotados de `ListRecords` sufrieron timeout o transferencia incompleta, por lo que no se presenta una cosecha OAI completa.

Se extrajeron metadatos Dublin Core embebidos de cinco fichas HTML públicas, entre ellas [una disertación de software de 2019](https://teses.usp.br/teses/disponiveis/55/55134/tde-21082019-164932/pt-br.html) y [una de educación de 2024](https://teses.usp.br/teses/disponiveis/48/48138/tde-05022025-113402/pt-br.html). El tipo explícito es `dissertação de mestrado`. `dc.date.issued` coincide con **Data de Defesa** y `dc.date.available` con disponibilidad/publicación: se conserva esta distinción en `date_evidence`. No se extrae el año del DOI ni de la URL, pues podría referir al depósito.

No se verificó una licencia abierta general de metadatos. `dc.rights=publico` expresa acceso, no licencia. Las fichas incluyen condiciones de uso y atribución para el documento; el piloto conserva únicamente metadatos breves y enlaces. El TCC/bachelor requerirá otra colección y una auditoría independiente.

## Semántica del piloto y siguiente cosecha

Este snapshot se distribuye como parte de la **colección pública de 225 metadatos**, según la confirmación del responsable registrada en `PERMISSIONS.json`. La minimización y esa declaración no se presentan como una licencia abierta universal ni como permiso sobre las tesis o materiales ausentes. Cada release registra campos, fuentes, cambios y fundamento; la licencia del código Synesis no relicencia estos metadatos y no se ha entrenado un modelo con ellos.

- `date_semantics=dc_date_issued`: en MIT y TU Berlin se verificó el campo cualificado `dc.date.issued`, sin confirmar que represente defensa o entrega. `academic_date_verified=false` impide tratarlo automáticamente como fecha académica.
- `date_semantics=defense_date_explicit`: en USP, el valor de `dc.date.issued` coincide con la fecha rotulada **Data de Defesa** en la ficha. Estos cinco registros tienen `academic_date_verified=true`; la disponibilidad/publicación es otra fecha y se conserva en `date_evidence`.
- `date_semantics=annual_list_heading`: en HKUST se observa únicamente un encabezado anual del listado. No prueba emisión, defensa o publicación; `academic_date_verified=false`. El detalle está en `date_evidence`. Excluir estos registros del análisis principal que exija fechas académicas comparables.
- `abstract_available` indica presencia en la **fuente consultada**; `false` en HKUST no prueba que la tesis carezca de resumen. Todos los registros publican `abstract=null` y `abstract_omitted_by_policy=true`.
- `license` contiene solamente una URI Creative Commons inequívoca hallada en el registro; puede corresponder a la obra. `rights_statement` conserva otras declaraciones como InC e InC-EDU; `rights_reference_url` conserva esos enlaces o referencias a colecciones que aparecían en campos de derechos, sin presentarlas como licencias. `metadata_license` describe derechos de metadatos cuando están verificados. Estos campos son independientes; `null` significa desconocido.
- `campus=null`: no se infiere el campus del país, ciudad de la institución o título. Se requerirá evidencia por registro.
- Los recuentos del piloto reflejan decisiones de selección. No crear tasas internacionales, rankings ni una estimación antes/después con esta muestra. Los tamaños, disciplinas, niveles y años no están balanceados.
- En una siguiente cosecha: estratificar por institución, disciplina, nivel y año académico; separar defensa, publicación y depósito; registrar latencia y faltantes; auditar cambios de cobertura y políticas. Los registros de 2026 están censurados por fecha de consulta y no constituyen un año completo.

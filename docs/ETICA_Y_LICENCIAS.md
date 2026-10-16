# Ética, acceso y licencias · Synesis

**Política operativa v0.1 · revisada el 16-10-2026.** El proyecto está en fase inicial. Esta política establece condiciones de trabajo; no afirma que se hayan obtenido permisos de universidades ni que exista aprobación de un comité de ética.

**Estado de esta distribución:** se publican los 225 metadatos de [`research_225`](../data/research_225/) con el permiso confirmado por el responsable, tanto para publicación como para investigación y eventual entrenamiento sobre ese snapshot. [`PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) registra la instrucción directa y el origen de la declaración: `independently_verified_by_project=false` e `institutional_permission_documents_in_repository=false`. No se inventan autorización institucional, documento contractual ni condiciones no aportadas. Las licencias observadas de origen se conservan sin convertir el conjunto en CC0 o MIT. La publicación ya está autorizada y no requiere reconfirmación. Se mantiene separado el piloto de diez metadatos CC0, incluido entre los 225; no se ha entrenado un modelo con los trabajos.

## 1. Finalidad y límites

Synesis estudia proyectos finales de grado y máster y prácticas documentales agregadas. No identifica «autores de IA», no puntúa honestidad académica, no contacta a autores/supervisores sin un procedimiento autorizado y no publica rankings de sospecha. Los detectores de texto generado quedan excluidos como medida de uso. Las etiquetas se refieren a evidencia documental, con incertidumbre y revisión humana.

Los datos reales se obtienen únicamente de repositorios institucionales mediante acceso legítimo y respetando condiciones verificadas. No se eluden cuentas, captchas, controles de acceso, embargos, límites de consulta o bloqueos. Se prefieren API/exportación/OAI-PMH cuando la institución los habilita y sus reglas permiten la operación. El soporte técnico de OAI-PMH no concede por sí solo una licencia sobre metadatos o documentos ni permiso para cualquier reutilización.

Se distinguen tres capas: **captura y almacenamiento local** para verificar fuentes y cobertura; **publicación del trabajo propio** —código, protocolo, manifiesto minimizado y referencias—; y **colecciones de metadatos publicadas**, con las condiciones específicas descritas arriba. La recuperación legítima de una ficha por sí sola no determina su reutilización; en esta colección de 225 se documenta además la confirmación del responsable. Los PDFs, resúmenes y textos completos permanecen fuera del paquete. El permiso sobre esos metadatos no se extrapola a materiales ausentes ni a otras capturas futuras.

## 2. Matriz obligatoria por fuente y operación

Antes de activar cada operación sobre una fuente se completa una fila por `source_id` y versión de sus condiciones. La [matriz de fuentes](FUENTES.md) enlaza los registros [`institutions_spain.json`](../config/institutions_spain.json) e [`institutions_global.json`](../config/institutions_global.json), además de la evidencia en [España](FUENTES_ESPANA.md) y [casos globales](FUENTES_GLOBALES.md). El registro debe conservar fecha, URL, evidencia mínima y responsable de revisión. El fundamento puede ser licencia, permiso u otra base documentada aplicable al actor, finalidad, jurisdicción y alcance; no se exige necesariamente Creative Commons. Cuando varía por ítem, la decisión final se toma por documento y se registran sus condiciones específicas. Una fuente puede estar activa para inventario local y pendiente para publicación, PDF o entrenamiento.

| Operación | Campo | Evidencia mínima | Valor inicial |
|---|---|---|---|
| Consultar/recuperar metadatos para inventario local minimizado | `metadata_access` | Acceso legítimo y condiciones de API/repositorio; campos, finalidad y alcance de captura documentados | `unknown` |
| Descargar texto/PDF | `fulltext_download` | Acceso legítimo, política y estado de embargo del ítem | `unknown` |
| Analizar texto localmente | `text_mining` | Licencia, permiso o base aplicable revisada para actor/finalidad/jurisdicción | `unknown` |
| Publicar metadatos de terceros o derivados | `metadata_redistribution` | Licencia, permiso u otra base documentada aplicable a esos campos/alcance, más revisión de privacidad y base de datos | `unknown` |
| Redistribuir texto/PDF | `fulltext_redistribution` | Licencia, permiso u otra base documentada que cubra reproducción y difusión en ese alcance | `unknown` |
| Publicar fragmentos o imágenes | `excerpt_redistribution` | Alcance permitido, atribución y terceros incluidos | `unknown` |
| Construir corpus de entrenamiento | `model_training` | Permiso revisado para finalidad, método, proveedor y material concreto | `unknown` |
| Publicar pesos/embeddings | `model_release` | Revisión de licencia, privacidad, memorización y extracción | `unknown` |

Para fuentes y operaciones nuevas, los valores de revisión posibles son `allowed`, `restricted`, `denied`, `unknown`, más fundamento, alcance y condiciones. `restricted` exige satisfacer condiciones documentadas. La ausencia de licencia indicada se registra como tal y no se traduce automáticamente a `denied`; puede existir otro fundamento aplicable. Deben constar también `basis_type`, `basis_evidence_url`, `scope`, `license_url` si existe, `terms_url`, `robots_url`, `checked_at`, `reviewer`, límite de peticiones y próxima revisión. Para los 225 actuales, la decisión de publicación e investigación/entrenamiento posterior de los metadatos está registrada como `confirmed_by_project_owner` en `PERMISSIONS.json`; no se sustituye ese origen por una verificación institucional. La recuperación por OAI-PMH y la declaración del responsable se documentan como evidencias distintas.

Un documento público no equivale a permiso de redistribución ni de entrenamiento. Una licencia del software Synesis no relicencia tesis, metadatos, figuras, datasets, fotografías o código de terceros. «Sin licencia indicada» no significa dominio público. Una licencia que permite leer o citar no cubre automáticamente un dataset masivo; los materiales de terceros dentro de una tesis pueden tener condiciones propias.

## 3. Minería de textos: revisión del caso concreto

En la UE, la Directiva 2019/790 distingue minería para investigación por organismos que cumplan sus condiciones y una excepción general con posibilidad de reserva de derechos. En España se revisará el artículo 67 del Real Decreto-ley 24/2021, junto con el marco aplicable. El proyecto no presupone ser un «organismo de investigación» elegible ni que llamarse investigación baste para acogerse a una excepción. La minería autorizada tampoco concede por sí misma derecho a redistribuir el corpus. Fuentes: [Directiva 2019/790, artículos 3–4](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32019L0790), [RDL 24/2021, artículo 67](https://www.boe.es/buscar/act.php?id=BOE-A-2021-17910&p=20211103&tn=0).

Antes de procesar textos se revisan acceso legítimo, quién investiga, finalidad, reservas/opt-outs, jurisdicción, almacenamiento y medidas del repositorio. El corpus internacional requiere revisión independiente del marco local y de las condiciones de cada institución; no se exporta automáticamente una regla española a China, EE. UU., Latinoamérica o Alemania. Ante incertidumbre se mantiene la operación en `unknown` y se sigue con metadatos permitidos o se solicita permiso concreto.

Respetar `robots.txt` es una regla de acceso del proyecto; su ausencia o un `Allow` no autoriza copyright ni tratamiento de datos. También se registran reservas legibles por máquina y otras reservas publicadas. El scraping usa identificación de proyecto/contacto cuando se configure, baja concurrencia, caché, recuperación incremental y pausa ante errores o respuestas 429. Una fuente retirada no se sustituye por un espejo que eluda su restricción.

## 4. Privacidad y responsabilidad

Los nombres, correos, firmas, expedientes y combinaciones de título/fecha pueden identificar personas. Que consten públicamente no elimina obligaciones de tratamiento. Antes de ampliar el corpus se documentan responsable, finalidad, base jurídica aplicable, información a interesados y necesidad de evaluación ética/impacto, según el contexto real. El [RGPD](https://www.boe.es/buscar/doc.php?id=DOUE-L-2016-80807) exige, entre otros principios, finalidad y minimización; la pseudonimización no equivale a anonimización.

Reglas de minimización del proyecto:

- No extraer correos, firmas, DNI, teléfonos o direcciones personales para el dataset analítico.
- Mantener texto original y claves de correspondencia fuera del repositorio público, con control de acceso. Los identificadores pseudónimos de supervisor solo se usan si son necesarios y legítimos para evitar fugas entre particiones.
- Publicar análisis agregados y campos estrictamente necesarios. Títulos, URLs persistentes y fragmentos textuales pueden permitir reidentificación; revisar su necesidad por release y excluirlos si el riesgo no es proporcional.
- Excluir o redactar datos sensibles y materiales de participantes de las tesis. No inferir salud, etnia, ideología o condiciones personales de los autores.
- Evitar celdas públicas de menos de 10 trabajos cuando puedan señalar personas; considerar agrupación adicional y ataques por diferencia entre tablas. Este umbral es una salvaguarda de proyecto, no una garantía de anonimato.
- No cargar tesis o datos personales en APIs externas sin revisar permiso, contrato, retención, ubicación, transferencias y configuración de uso de datos. Priorizar extracción local cuando cubra la tarea.

## 5. Conservación, retirada y publicación

La conservación se documenta por capa: evidencias de acceso/licencia, originales locales, metadatos publicados, texto procesado si lo hubiera, anotaciones y salidas. Propuesta para originales permitidos: hasta finalizar validación/publicación, con revisión anual y eliminación cuando deje de ser necesaria su conservación, salvo obligación documentada de preservar para verificación. No se afirma haber establecido una política institucional ni un canal de contacto operativo hasta configurarlos. Esta tarea de mantenimiento no suspende la publicación ya autorizada de los 225 metadatos.

Las solicitudes legítimas de corrección/retirada se registran con fecha, material y acción. Se propagan a nuevas versiones, derivados y modelos cuando proceda; un modelo que memoriza contenido requiere evaluación específica. Se mantiene un registro mínimo de retirada sin conservar innecesariamente el contenido. Una publicación en GitHub puede quedar en forks y cachés: por ello la revisión de datos se hace antes de publicar, y se explica ese límite en la ficha de dataset.

| Capa | Publicación por defecto del proyecto |
|---|---|
| Colección `research_225` | 225 metadatos publicados por instrucción y permiso confirmado del responsable; declaración en `PERMISSIONS.json`, licencias de origen preservadas |
| Piloto CC0 | Diez metadatos de TU Berlin con evidencia institucional CC0; incluidos entre los 225 y separados para reproducción |
| Respuestas brutas y originales locales | Permanecen fuera del paquete; no se copian automáticamente al publicar metadatos |
| Código/configuración propia | Publicable con licencia explícita elegida para Synesis; sin incorporar corpus de terceros por defecto |
| Protocolo, manual, manifiesto minimizado y referencias | Publicables tras revisión de fuentes, necesidad de campos y privacidad |
| Figuras propias | Publicables cuando existen datos y fundamento para la salida concreta; indicar denominadores y alcance |
| Metadatos de nuevas fuentes | Documentar campos, operación, alcance y fundamento antes de incorporarlos; conservar la evidencia y los desconocidos |
| Originales, PDFs, OCR y texto completo | Fuera del repositorio público salvo fundamento revisado que cubra la difusión concreta |
| Anotaciones/fragmentos | Revisar licencia y reidentificación; preferir códigos/localizadores mínimos |
| Entrenamiento futuro sobre los 225 metadatos | Permiso confirmado por el responsable y registrado; tarea, particiones y evaluación todavía no ejecutadas |
| Embeddings y pesos derivados | No existen en esta versión; cualquier publicación posterior documentará datos utilizados, evaluación y alcance |

La atribución registra institución, autor cuando sea necesario y admisible, título, URL persistente, licencia y fecha de consulta. Las imágenes de portada deben ser propias, generadas o con permiso documentado, con procedencia y términos. La identidad Synesis no debe sugerir afiliación o aval de universidades o proveedores.

## 6. Corpus para modelos y síntesis futura

Cada derivado tiene ficha propia: origen, permisos por ítem, idiomas, niveles, periodos, exclusiones, anotación, particiones, usos admitidos y límites. Un dataset de declaraciones no es un dataset de «uso real de IA»; una etiqueta sobre reproducibilidad no mide calidad global del estudiante.

Se permite preparar la mecánica de entrenamiento con fixtures claramente separados; los resultados científicos usan trabajos reales. El responsable confirmó el permiso para investigación y eventual entrenamiento con los 225 metadatos publicados. Todavía deben definirse y registrarse tarea, campos, anotación y particiones; no se ha entrenado un modelo. Ese permiso se refiere a este snapshot y no incluye por extensión tesis, PDFs o resúmenes ausentes. Evaluar memorización, recuperación de fragmentos e información personal antes de publicar pesos o vectores. La síntesis de ejemplos a partir de datos protegidos también requiere revisión: «sintético» no garantiza ausencia de copia o reidentificación.

Seguir los principios [FAIR](https://www.nature.com/articles/sdata201618) significa documentar localización, acceso, interoperabilidad y reutilización; admite acceso restringido justificado. Documentar un recurso puede ser más apropiado que redistribuirlo. La apertura científica de Synesis se apoya en procedencia, código y decisiones auditables, además de los datos que legalmente puedan compartirse.

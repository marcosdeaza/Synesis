# Protocolo de investigación · Synesis

**Versión de diseño:** 0.1 · **Fecha de corte documental:** 16 de octubre de 2026.  
**Estado:** protocolo preparado para pilotaje; no prerregistrado, sin resultados inferenciales. Las decisiones propuestas deben congelarse tras la auditoría de viabilidad y antes del análisis confirmatorio.

Synesis estudia la evolución de trabajos finales de grado y máster y la evidencia documental del uso de IA generativa. Su núcleo es Valencia, con presencia obligatoria de la **Universidad Europea de Valencia (UEV)** y la Universitat Politècnica de València (UPV); se amplía a Madrid, Barcelona y otros centros españoles, y a casos de China, Estados Unidos, Latinoamérica y Alemania. El conjunto es una muestra documental de repositorios institucionales, no una muestra representativa de todos sus estudiantes.

## 1. Dos líneas de evidencia

| Línea | Pregunta | Observación admisible | Conclusión que no permite |
|---|---|---|---|
| A · Transformación observable | ¿Cambian los temas, métodos, bibliografías, artefactos y mecanismos de reproducibilidad entre cohortes? | Metadatos, texto accesible legalmente y enlaces verificables | Atribuir el cambio a IA por coincidencia temporal |
| B · Uso documentado | ¿Qué usos de IA se declaran y con qué trazabilidad? | Declaración explícita del trabajo, anexos de prompts, modelo o herramientas identificados, documentación vinculada atribuible al trabajo | Inferir uso no declarado por estilo, calidad, fecha, una cita o un detector |

Se analizarán por separado **IA como objeto de estudio**, **uso instrumental declarado** y **contexto tecnológico disponible**. Un TFG sobre ChatGPT puede no haberlo usado como asistente; un trabajo que no menciona IA puede haberla usado. Ausencia de declaración significa **uso desconocido**. Una política universitaria describe la institución, no prueba el comportamiento individual.

## 2. Preguntas y estimandos

1. **RQ1, cobertura:** ¿Qué proporción de los registros identificados permite observar resumen, texto y artefactos, según institución, año, idioma, disciplina y nivel? El denominador es el inventario recuperable de cada fuente, nunca matrículas o egresados no observados.
2. **RQ2, cambios:** ¿Cómo evoluciona, dentro de estratos comparables, la proporción de trabajos con datos/código enlazados y con descripción reproducible de sus métodos? Estimandos: diferencias y razones de proporciones en el corpus elegible, con incertidumbre e información de cobertura.
3. **RQ3, IA documentada:** ¿Qué proporción contiene declaración explícita de uso, qué tareas se declaran y qué precisión tienen las declaraciones? Se informa sobre trabajos con secciones realmente auditables. El resultado mide **declaración observada**, no prevalencia real de uso.
4. **RQ4, diversidad:** ¿Cambian diversidad temática, distribución de métodos, variedad de fuentes o similitud textual tras controlar plantillas, idioma, disciplina y composición del corpus? «Homogeneización» es una hipótesis operacional; no se presupone.
5. **RQ5, gobernanza:** ¿Cómo coinciden normas institucionales documentadas y prácticas de declaración? Análisis exploratorio con versiones y fechas de las normas; sin equiparar ausencia de política pública a ausencia de política.
6. **RQ6, comparabilidad internacional:** ¿Qué similitudes y diferencias persisten al restringir a proyectos de grado/máster equivalentes y estratos con cobertura suficiente? Los casos internacionales contextualizan; un centro no representa un país o continente.

El resultado primario propuesto para la línea A es `artefacto_reproducible_enlazado`: datos o código con enlace que resuelve, acompañado de instrucciones o descripción suficiente para localizar el artefacto. Se preservan sus componentes para no confundir existencia, accesibilidad y reproducibilidad ejecutada. El resultado primario propuesto para B es `declaracion_uso_ia_explicita`, restringido a texto auditable. Ambos se ratifican o modifican, con justificación fechada, antes del prerregistro.

## 3. Población, alcance y selección

**Población objetivo conceptual para la comparación temporal:** trabajos finales universitarios de grado y máster, defendidos aproximadamente entre 2018 y 2026. **Población documental accesible:** registros de esa clase verificables en repositorios institucionales y recuperados mediante acceso legítimo. El inventario puede conservar trabajos cuya fecha académica o campus todavía no estén determinados: sirven para auditar cobertura, sin asignarlos a una cohorte o campus por conjetura. El año 2026 y las cohortes con depósito todavía abierto son provisionales.

La inclusión obligatoria de UEV se registra como decisión de diseño. Si sus textos no son accesibles o sus licencias no permiten una operación, se mantiene la institución en la matriz de cobertura con esa limitación. No se sustituye por otra Universidad Europea, sede o campus ni se interpreta un repositorio general del grupo como corpus de UEV sin identificación del centro.

El panel se selecciona primero por relevancia territorial e institucional y después por viabilidad documentada: UEV y UPV; centros públicos/privados, politécnicos, autónomos y generalistas de Valencia, Barcelona y Madrid; casos internacionales de las cuatro regiones requeridas. La selección es intencional. Para evitar elegir centros por resultados llamativos, el orden de prioridad y los motivos de exclusión se cierran antes de examinar resultados.

| Decisión | Regla |
|---|---|
| C1 · Elegible para inventario documental | Trabajo único de grado o máster, con registro, nivel e institución verificables. No exige PDF, fecha académica validada ni campus informado |
| Campus | Solo se asigna o se afirma pertenencia a un campus cuando existe evidencia. Un campo nulo permanece desconocido; la sede de la universidad no se imputa como campus del trabajo |
| C3 · Elegible para comparación temporal | Subconjunto con fecha académica de semántica verificada, precisión suficiente para la ventana y estratos comparables. Sin esa evidencia el registro permanece en C1, fuera de C3 |
| Equivalencia internacional | Conservar denominación original; asignar nivel mediante evidencia institucional. `Bachelor thesis`, `master thesis`, `capstone` o proyecto de título no son equivalentes automáticamente |
| Excluir | Doctorado, artículos, memorias docentes, proyectos no finales, registros duplicados y tipos no determinables; conservar motivo en log |
| Acceso | Embargo y restricción son estados de cobertura; nunca se eluden. Una ficha accesible no autoriza descargar, redistribuir ni entrenar |
| Unidad de análisis | Trabajo; anexos y versiones forman un grupo. Una obra no se cuenta dos veces por aparecer en varias colecciones |
| Muestreo | Inventario local minimizado de registros accesibles legítimamente, con procedencia y condiciones documentadas; selección aleatoria estratificada para texto cuando esa operación tenga fundamento revisado. Conservar semilla y lista congeladas |
| Estratos | Institución × grado/máster × familia disciplinar × curso/cohorte × idioma; campus solo cuando esté verificado y se analice a ese nivel. Reducir granularidad solo con regla registrada |

La extensión internacional no debe reducir la profundidad del núcleo valenciano. Si los recursos no alcanzan, la secuencia es Valencia → Madrid/Barcelona → casos internacionales; se publica cada gate y su cobertura, sin completar celdas con documentos inventados o repositorios ajenos.

La elegibilidad científica y los derechos para una operación son ejes independientes. Un registro puede formar parte del inventario local C1 y no ser redistribuible. El código, protocolo, manifiesto minimizado y referencias verificables pueden prepararse para publicación mientras los metadatos de terceros, texto, corpus o pesos permanecen fuera del paquete público hasta revisar fundamento y alcance por fuente. Ese fundamento puede ser licencia, permiso u otra base documentada aplicable; no se exige necesariamente una licencia Creative Commons. Un endpoint OAI-PMH acredita una vía de recuperación, sin conceder todas las reutilizaciones posibles.

## 4. Fechas y fases tecnológicas

Guardar por separado defensa/entrega, curso académico, publicación del registro, depósito y recuperación. Prioridad analítica: defensa o entrega documentada; si falta, curso académico como intervalo; depósito solo como aproximación explícita y en sensibilidad. Un depósito tardío no convierte una tesis antigua en exposición reciente.

Los nombres de campos no garantizan su significado: `dc.date.issued` puede reflejar publicación o carga del repositorio. Para cada fuente se contrastan muestras de ficha, PDF y otros campos (`created`, `accessioned`, curso) antes de asignar `academic_date`. Si varios campos coinciden sistemáticamente con carga o migración, se marca `date_semantics_unverified` y esos registros no se usan para cortes temporales académicos hasta resolverlo. Se conserva siempre el valor original y la regla de mapeo.

La comparación principal propone **2018–2021 como referencia anterior al acceso masivo a chat generativo** y **2023–2025 como periodo posterior**. No se llama al periodo anterior «sin IA»: existían correctores, traductores y herramientas generativas. 2022 es transición cuando no se conocen meses y 2026 permanece provisional. COVID-19, cambios curriculares, plantillas, políticas y cobertura son explicaciones alternativas.

La [cronología](CRONOLOGIA.md) y [`config/ai_milestones.csv`](../config/ai_milestones.csv) separan ChatGPT (30-11-2022), GPT-3.5 Turbo por API (01-03-2023), herramientas, abaratamiento específico e integración de agentes. Son **fechas de oferta tecnológica**, no fechas de adopción estudiantil ni tratamientos exógenos. No se dividirá una serie corta en doce «eras» para ajustar doce efectos.

Cuando existan fechas precisas, usar ventanas de 6 y 12 meses de exclusión o rezago alrededor de hitos como sensibilidad al tiempo de elaboración. Si solo hay curso académico, expresar exposición como ambigua o intervalo; no imputar una fecha diaria exacta. La cronología incluye Opus 5.5 (22-09-2026) mediante fuente primaria; su proximidad al corte impide una comparación de resultados académicos madura.

## 5. Variables y evidencia

| Familia | Variables mínimas | Precaución |
|---|---|---|
| Identificación/procedencia | Identificador persistente, fuente, campus si está verificado, URL, recuperado en, versión, hash | Los identificadores públicos y títulos pueden reidentificar autores; campus desconocido se conserva nulo |
| Contexto | Nivel original/normalizado, disciplina, idioma, curso y precisión de fecha | Versionar el mapeo; revisar categorías «otros» y desconocidos |
| Acceso/calidad | Metadatos/texto, embargo, licencia, OCR, páginas, errores, parser | Calidad de OCR no es calidad del trabajo |
| Métodos | Cuantitativo, cualitativo, mixto, ingeniería/artefacto, revisión; muestra y evaluación declaradas | Permitir multietiqueta y desconocido |
| Reproducibilidad | Datos/código enlazados, disponibilidad comprobada, licencia, entorno y pasos | Un enlace GitHub no prueba que el experimento se reproduzca |
| Bibliografía | Referencias extraídas, año, tipo, identificador, resolución | Cita no resuelta no equivale a cita falsa; validar extracción manualmente |
| IA temática | Tema principal/secundario, modelos discutidos | No equivale a uso instrumental |
| IA instrumental | Declaración explícita, tarea, herramienta/modelo/versión, prompts/logs mencionados, límites | Descripción ambigua se etiqueta como tal; no se convierte en positivo |
| Textual exploratoria | Longitud, secciones, diversidad léxica, similitud y temas | Separar por idioma y retirar portadas, plantillas, bibliografía y texto legal |

Jerarquía de evidencia: **E1**, declaración directa auditable del trabajo; **E2**, anexo/artefacto vinculado con procedencia clara; **E3**, metadatos o resumen explícitos; **E4**, contexto institucional/tecnológico. E3 puede demostrar que IA es tema; la etiqueta de uso requiere que el texto describa uso instrumental. E4 nunca acredita uso individual. La evidencia sostiene afirmaciones acotadas; ni una declaración garantiza exhaustividad ni un log garantiza calidad.

## 6. Anotación humana y calidad

El pilotaje propuesto es de 60 trabajos, estratificados por periodos, idiomas, niveles e instituciones accesibles, con al menos dos anotadores y sin usar el conjunto futuro de evaluación. Es un objetivo operativo, no un tamaño de muestra suficiente para inferencia. Si una fuente carece de documentos se registra la ausencia y no se rellena artificialmente.

Cada etiqueta guarda definición, fragmento mínimo/localizador, fuente, versión, anotador y confianza. Se ocultan, cuando sea viable, fecha e institución durante anotación de métodos y reproducibilidad. Los anotadores no verán puntuaciones de detectores ni predicciones del modelo.

El 100 % del piloto y al menos el 20 % de la muestra analítica reciben doble anotación independiente. Para etiquetas nominales se informa matriz de desacuerdo, acuerdo bruto y kappa de Cohen; para ordinales, kappa ponderada predefinida; para medidas continuas, ICC con variante y diseño declarados. Con clases raras, no interpretar kappa aislada: informar prevalencia y acuerdo por clase. El consenso posterior no reemplaza la medida anterior a adjudicación.

Gate de anotación propuesto: acuerdo bruto ≥0,85 y kappa ≥0,70 cuando sea interpretable; si falla, revisar manual y volver a anotar una muestra nueva. Estos umbrales son reglas del proyecto, no garantías universales. Un tercer revisor adjudica discrepancias. Los idiomas requieren competencia humana o revisión bilingüe; la traducción automática conserva original, herramienta y fecha, y no se toma como verdad del texto.

## 7. Sesgos y límites que deben acompañar cada resultado

- **Selección y depósito:** repositorios pueden contener solo algunos trabajos o trabajos con autorización. Informar el flujo identificado → elegible → texto accesible → anotable y motivos por cohorte.
- **Panel desequilibrado:** entradas/salidas de fuentes, años vacíos y migraciones no son ceros de producción. Publicar panel completo y subconjunto estable; ponderar solo si existen probabilidades o denominadores defendibles.
- **Composición:** disciplina, nivel, idioma y universidad cambian con el tiempo; presentar estratos y estandarización sobre un soporte común, además de agregados.
- **Medición de uso:** declaración depende de normas, plantillas y voluntad de declarar. El cambio en declaraciones puede reflejar cambio normativo, sin cambio en uso.
- **Tiempo:** las tesis tardan meses en elaborarse y depositarse; el corte reciente sufre censura y rezago. Mostrar fecha original y criterio de madurez de cohorte.
- **Confusión:** pandemia, acceso a software, cambios de evaluación y expansión de repositorios coinciden con avances de IA. El diseño inicial es observacional y descriptivo.
- **Transferencia internacional:** diferencias de grado, duración, idioma, evaluación y acceso limitan comparación. Mantener casos contextuales fuera de estimaciones españolas si no hay soporte común.

Se excluyen detectores de «texto generado por IA» como medida de uso y como etiquetas de entrenamiento. Sus errores y sesgos están documentados, por ejemplo en [Liang et al.](https://arxiv.org/abs/2304.02819). Synesis no evalúa integridad de personas ni produce listas de «sospechosos».

## 8. Gates y trazabilidad

| Gate | Evidencia necesaria para avanzar | Salida si no se alcanza |
|---|---|---|
| G0 · Diseño | Panel candidato, responsables, preguntas y operaciones definidas | Protocolo con pendientes explícitos |
| G1 · Acceso/derechos | Matriz por fuente/operación con acceso legítimo, fundamento y alcance documentados, límites técnicos y privacidad | Inventario local minimizado y referencias admisibles; publicación de corpus, PDF y entrenamiento siguen desactivados si falta fundamento para esa operación |
| G2 · Piloto | Procedencia auditada; extracción revisada; manual estable y acuerdo medido; fechas verificadas para el subconjunto temporal | Corregir medición y repetir piloto; mantener C1 documental aunque no pueda constituirse C3 temporal |
| G3 · Prerregistro | Preguntas primarias, muestra, cortes, exclusiones, análisis, criterios de suficiencia y snapshot congelados; depósito público con fecha cuando esté aprobado | Documento de diseño aún modificable, sin afirmar prerregistro |
| G4 · Análisis | Calidad, cobertura y tamaño adecuados; ejecución reproducible y revisión humana | Informe descriptivo con limitaciones y resultados no estimables |
| G5 · Publicación | Revisión científica, de licencias, privacidad y paquetes; claims ligados a figuras/tablas | Solo artefactos aprobados; ningún PDF o peso se publica por defecto |

Todo cambio posterior a G3 se registra como enmienda fechada; se distingue confirmatorio de exploratorio. Código, configuraciones, entorno, semillas, manifiestos y figuras quedan versionados. Las fuentes pueden retirarse o cambiar: un hash acredita una captura concreta, no una autorización de reutilización.

## English abstract

Synesis is an observational, repository-based study of bachelor and master final projects, centred on Valencia and mandatorily including Universidad Europea de Valencia. It separates observable changes in scholarly work from explicit, traceable evidence of generative AI use. Release dates represent technological availability rather than adoption. Coverage, deposit delay, language, degree equivalence and disciplinary composition are measured before comparisons. Public access does not imply redistribution or model-training rights. Confirmatory analyses require a frozen snapshot and a dated preregistration; insufficient data lead to descriptive reporting rather than fabricated findings.

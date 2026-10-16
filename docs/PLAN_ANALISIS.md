# Plan de análisis · Synesis

**Estado:** propuesta v0.1, 16-10-2026. No se han estimado efectos ni entrenado modelos con este plan. Su finalidad es fijar decisiones revisables antes del prerregistro descrito en el [protocolo](PROTOCOLO.md).

## 1. Orden de ejecución

1. Congelar lista de fuentes y auditoría por operación. Crear inventario local minimizado de registros reales recuperados legítimamente, con consulta, cursores/paginación, fechas, estado de acceso y hashes cuando proceda. Este snapshot no se convierte automáticamente en dataset público.
2. Auditar elegibilidad, duplicados/versiones, mapeo de disciplinas, campus, nivel y fechas. Exportar diagrama de flujo y tabla de datos faltantes.
3. Realizar piloto de extracción/anotación, fijar manual, estimar acuerdo y medir cuántos casos y positivos existen realmente.
4. Especificar potencia o precisión mediante simulaciones sobre tamaños y dependencia plausibles del piloto. Registrar efecto mínimo relevante, error tolerado y coste. El piloto no se añade silenciosamente a una prueba confirmatoria que ya ha orientado.
5. Congelar preguntas primarias, muestra, etiquetas, análisis y reglas de no estimación. Solo después, prerregistrar y ejecutar la parte confirmatoria.
6. Publicar resultados con intervalos, denominadores, fallos, sensibilidad y código; explorar mecanismos y nuevos modelos en apartados separados.

## 2. Conjuntos analíticos y denominadores

| Conjunto | Unidad/denominador | Uso |
|---|---|---|
| C0 · Registros identificados | Registros recuperados por fuente y ejecución, incluidos tipos o niveles pendientes | Inventario local minimizado y flujo, incluyendo descartes |
| C1 · Inventario documental verificable | Trabajos únicos de grado/máster con registro, nivel e institución verificables | Descripción documental; no exige PDF, campus ni fecha académica validada |
| C2 · Texto auditable | Trabajos de C1 cuyo texto puede procesarse y auditarse legítimamente | Declaración, métodos, referencias y artefactos |
| C3 · Panel temporal estable | Subconjunto de C1 con fecha académica de semántica verificada, precisión suficiente y estratos presentes con medición comparable en ambos periodos; intersectar con C2 si el resultado requiere texto | Comparaciones temporales condicionadas a viabilidad; no se exige campus si no se afirma ni estratifica por campus |
| C4 · Corpus permitido para modelos | Subconjunto con fundamento y alcance revisados por fuente/ítem para la operación concreta | Modelos de extracción o clasificación documental, con ficha propia |

No usar C2 como si fuera C1. No describir C1 como todos los TFG/TFM de una universidad sin comprobar exhaustividad. Publicar `n` observado por resultado; una sección no disponible, un OCR fallido y una declaración ausente son estados distintos. La media entre universidades no se pondera por número de depósitos sin justificar qué población representa.

El campus desconocido permanece nulo y no excluye del inventario C1 ni de un análisis institucional. Solo una afirmación o comparación por campus exige verificarlo. De igual forma, una fecha de depósito puede describir la captura, pero no sustituye la fecha académica necesaria para C3. La pertenencia a C1 es una decisión documental; la redistribución de sus campos depende de otra revisión, por fuente y alcance. No se presenta el inventario local como corpus abierto cuando falta ese fundamento.

**Gate de fechas:** verificar la semántica de fechas por fuente antes de cualquier gráfico «antes/después». Si `issued` reproduce `accessioned`, una migración o una carga masiva, no se toma como defensa. Los registros con semántica sin verificar sirven para cobertura de la captura, pero quedan fuera de la comparación por fecha académica; no se corrige el problema cambiando solo el título del eje.

## 3. Descripción que precede a cualquier modelo

Entregar al menos: mapa de fuentes con estados de acceso; matriz institución × cohorte de trabajos/porcentaje auditable; distribución de rezago defensa–depósito; idiomas, disciplinas y niveles; flujo de exclusiones; tabla de permisos; proporción de declaraciones y enlaces con sus denominadores. Celdas con menos de 10 trabajos se agrupan o suprimen en visuales públicas cuando exista riesgo de señalamiento; se indican las supresiones.

Para proporciones de un estrato se proponen intervalos de Wilson al 95 %. Si hay dependencia por colección, supervisor o grupo de trabajos, usar bootstrap por grupo o un modelo apropiado; los intervalos describen variación bajo supuestos del muestreo, no eliminan sesgo de cobertura. Diferencias y razones se presentan con intervalos y magnitud sustantiva, evitando que un `p < 0,05` sea la única conclusión.

Todos los gráficos declaran fuente, fecha de corte, unidad, denominador, filtros y carácter observado/exploratorio. Las filas sintéticas de pruebas de software nunca entran en figuras de investigación. Un mapa colorea **instituciones observadas**, no todo un país como si fuera representativo.

## 4. Comparación temporal principal

Ventana candidata: 2018–2021 frente a 2023–2025; 2022 en transición y 2026 provisional. Las fechas de defensa/entrega tienen prioridad. La ventana final depende de cobertura real y se congela en G3. No seleccionar el corte que produzca la mayor diferencia.

La comparación A estima el cambio de `artefacto_reproducible_enlazado` en C3. La B estima el cambio de **declaración explícita** en el subconjunto con secciones auditables. La variación se descompone por institución, nivel, disciplina e idioma. Se publican resultados crudos y, si hay soporte común, estandarizados a una composición fija predefinida. No extrapolar a estratos que no existen en ambos periodos.

Un modelo exploratorio posible para un resultado binario es:

```text
logit[P(Y_i = 1)] = intercepto + periodo_i + año_i
                     + institución_i + nivel_i + disciplina_i + idioma_i
```

El periodo y la tendencia anual pueden ser colineales; se revisan identificabilidad y parametrización antes de ajustar. Se ajustan pocas variables predefinidas, sin buscar automáticamente todas las interacciones. Los coeficientes expresan asociaciones en el corpus. Un término `post_ChatGPT` no identifica un efecto causal de ChatGPT.

**Gate de suficiencia del modelo:** evaluación de precisión/potencia por simulación y tamaños por clase/estrato; comprobación de separación, colinealidad y estabilidad. Como mínimo operativo inicial, exigir 200 casos auditables y al menos 50 observaciones de cada clase para un baseline binario pequeño, además de no superar 1 parámetro libre por cada 15 observaciones de la clase minoritaria. Estos números son una salvaguarda del proyecto, no una garantía estadística; si fallan o la simulación muestra imprecisión, reducir complejidad o limitarse a descripción. Penalización no crea información ausente.

## 5. Hitos, series y precios

La [cronología](CRONOLOGIA.md) organiza oferta tecnológica en ejes: acceso conversacional, coste, contexto/capacidades y herramientas/agentes. Los eventos se solapan. No existe un grupo universal «no expuesto»: las diferencias entre universidades no constituyen por sí mismas un control válido.

Una regresión segmentada es **exploratoria** y solo procede si hay fechas precisas, numeradores/denominadores comparables, suficientes puntos antes/después y cobertura estable. Regla preliminar: al menos 12 periodos mensuales o trimestrales no vacíos a cada lado, con evaluación adicional de potencia y autocorrelación. No convertir ocho cursos académicos en 96 meses ficticios. Si el cambio es gradual, usar un rezago o rampa fijados antes de mirar resultados. Elegir un hito principal; no ajustar todas las interrupciones simultáneamente.

```text
g(E[Y_t]) = β0 + β1·t + β2·I(t ≥ T0)
                 + β3·max(0, t − T0) + estacionalidad + composición
```

Para conteos, usar offset del número de trabajos observables y valorar sobredispersión; para proporciones, modelo binomial con denominador. Comprobar residuales, autocorrelación, estacionalidad y simultaneidad de cambios. Consultar [Lopez Bernal et al.](https://pubmed.ncbi.nlm.nih.gov/27283160/) y su [corrección](https://pubmed.ncbi.nlm.nih.gov/32879971/). La aplicación aquí no hereda automáticamente la interpretación causal de una intervención controlada.

Las figuras de precio comparan tarifas fechadas de modelos y modalidades concretas: USD por millón de tokens de entrada/salida y, por separado, caché, lotes y herramientas. Registrar impuestos/moneda si procede, contexto y versión. Una bajada de una familia no representa todo el mercado; tokens por tarea y calidad varían. Coste de suscripción ChatGPT/Claude, coste API y coste final de un agente son magnitudes distintas.

## 6. Mini modelos útiles y evaluables

El propósito es hacer reutilizable la investigación, sin construir un «detector de trampas».

| Modelo | Baseline | Evaluación | Condición de uso |
|---|---|---|---|
| Extracción de enlaces/citas/modelos mencionados | Reglas y expresiones regulares documentadas | Precisión, recall y F1 por campo contra anotación humana | Distinguir coincidencia de palabra y evidencia de uso |
| Clasificación de método o temática IA | Regresión logística regularizada con TF-IDF frente a clase mayoritaria | Macro-F1, por clase, matriz de confusión e intervalos por trabajo | Texto/licencia permitidos; no dar etiquetas de autoría IA |
| Clasificación de declaración explícita | Reglas/lexicón revisados frente a logit pequeño | Sensibilidad, precisión y calibración sobre evaluación ciega | Solo apoyar búsqueda; toda cifra publicada requiere validación humana |
| Agrupación temática | TF-IDF y reducción/clustering con semillas fijas | Estabilidad entre semillas, coherencia humana y ejemplos autorizados | Exploratorio; nombres de temas asignados por revisión humana |
| Asociación temporal | Proporciones estratificadas antes de regresión | Ajuste, sensibilidad, incertidumbre y tamaño efectivo | Superar gates de calidad y precisión |

Se registran versión, configuración, recursos y limitaciones en una ficha de modelo inspirada en [Model Cards](https://arxiv.org/abs/1810.03993). Un modelo grande externo puede asistir anotación solo tras resolver permiso, privacidad y retención; guardar modelo exacto, fecha, prompt y revisión humana. No es necesario enviar tesis a una API para ejecutar el baseline local.

## 7. Particiones, contaminación y evaluación

La partición se hace por **trabajo completo antes de fragmentar**: todas sus páginas, anexos y versiones quedan juntas. Duplicados casi idénticos, plantillas y artefactos derivados no se reparten entre entrenamiento y test. Si la misma obra está en dos repositorios, se conserva como un grupo.

Para validación temporal, entrenar en cohortes antiguas, seleccionar en una posterior y reservar la última cohorte madura para una evaluación única. Como ejemplo a ratificar por cobertura: entrenamiento ≤2022, validación 2023 y test 2024–2025. Si la clase positiva no existe en entrenamiento, no se disimula: ajustar tarea/ventana y dejar la enmienda registrada, o no entrenar. Aplicar agrupación adicional por supervisor/grupo cuando esa información sea legítima y disponible; guardar su identificador pseudónimo en área restringida, sin publicar nombres. Si falta, declarar riesgo de fuga sin inventar identificadores.

Todo vocabulario, normalización, selector de variables y ajuste se aprende con entrenamiento. Los umbrales se fijan en validación. La evaluación incluye holdout de institución cuando el tamaño permite medir transferencia; la traducción y OCR se evalúan por idioma. Informar baseline mayoritario y rendimiento por estrato. La exactitud global aislada puede ocultar fallos en clases raras.

## 8. Análisis de sensibilidad y no estimación

- Comparar panel completo y panel estable; excluir migraciones de repositorio y cohortes inmaduras.
- Comparar fecha de defensa, curso y depósito; excluir ±6/±12 meses de transición cuando la precisión de fecha lo permita.
- Separar grado/máster, idioma y disciplina; retirar un centro cada vez para identificar dominancia.
- Repetir con metadatos mínimos comunes frente a texto completo; describir selección de C2 respecto de C1.
- Repetir similitud sin portadas/plantillas y con longitud comparable; no atribuir convergencia a IA.
- Auditar manualmente enlaces y citas que no resuelven antes de calificarlos como error del trabajo.
- Informar resultados primarios y todos los exploratorios ejecutados; si hay muchas pruebas, fijar familia y corrección, por ejemplo Benjamini–Hochberg, en G3.

Si faltan datos, se informa `no estimable`. No imputar uso IA no declarado, fechas exactas desde el nombre del archivo ni licencias ausentes. La imputación de covariables, si se propone, exige supuesto explícito y sensibilidad; nunca convierte falta de acceso a PDF en ausencia de rasgo. Una asociación temporal robusta sigue necesitando evidencia adicional para estudiar mecanismos o causalidad.

## 9. Paquete de resultados y reutilización

Cada release identifica qué capas incluye y cuáles conserva únicamente en el inventario local. Código propio, protocolo, criterios de elegibilidad, diccionario, manifiesto minimizado y referencias verificables pueden publicarse tras su revisión sin redistribuir el corpus de terceros. Las tablas, datos, figuras y fichas de modelos se añaden cuando existen y su publicación está cubierta; no se anuncian anotaciones o modelos todavía no realizados. Separar archivos de ejemplo técnico de resultados reales. La ficha de dataset sigue [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) y documenta composición, fundamento de uso, exclusiones, retirada y usos admitidos. Para distribuir metadatos de terceros, corpus o pesos se documenta una licencia, permiso u otra base aplicable por fuente y alcance; no se exige necesariamente Creative Commons ni se interpreta OAI-PMH como permiso total.

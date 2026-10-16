# Minimodelos · estado y límites

## M0 · baseline léxico, ejecutable

Implementado en `src/synesis/core.py`, sin llamadas a modelos externos ni coste de API. Busca señales de asistentes nombrados, IA generativa, modelos de lenguaje, RAG y agentes en título, materias y cualquier resumen cuya presencia esté autorizada. La distribución actual omite todos los resúmenes; por tanto el piloto analiza título y materias solamente.

Salida: cinco indicadores, `any_ai_cue`, longitud del metadato y disponibilidad de resumen. Un positivo es una coincidencia léxica, no uso de IA. Puede fallar por siglas ambiguas, Gemini/Copilot en otros contextos, expresiones nuevas, traducciones, puntuación y escasez de metadatos. Las reglas están adaptadas de forma parcial a español, inglés, portugués, alemán y chino; no tienen sensibilidad equivalente por idioma.

**Validación actual:** invariantes de software y trazabilidad del corpus. **Evaluación semántica pendiente:** anotación independiente, precisión/recobrado por lengua e institución e inspección de falsos positivos/negativos. No está validado para clasificar personas, plagio, integridad ni autoría. Nunca utilizarlo para sanciones o rankings.

## M1 · acuerdo de anotadores, ejecutable cuando haya etiquetas

`scripts/annotation_agreement.py` mide acuerdo observado y kappa para dos anotadores en `topic_ai`, preservando `uncertain` como categoría. Informa el número de tesis emparejadas y las etiquetas excluidas, y no produce una cifra cuando los datos faltan o el denominador de kappa es degenerado. Una cifra de kappa no demuestra la verdad de las etiquetas ni elimina el sesgo del instrumento.

No se ha ejecutado sobre anotaciones reales: el formulario aún está vacío. Los ejemplos de las pruebas automatizadas son fixtures, nunca se mezclan con el corpus real.

## M2 · modelo estadístico de cambio, diseño preparado

La familia de modelos de panel o series interrumpidas está especificada en `PLAN_ANALISIS.md`. No se ajusta sobre este piloto de conveniencia. Requiere marco de cobertura, fechas armonizadas, suficientes observaciones por celda y una variable de resultado validada; la disponibilidad de un producto no identifica un efecto causal.

## Reutilización y entrenamiento posterior

No hay pesos entrenados, ni dataset etiquetado certificado, ni autorización general para entrenar con tesis. El corpus futuro necesita una ficha de derechos por fuente/obra, deduplicación entre particiones, particiones temporales e institucionales, evaluación externa y ficha de modelo revisada. Las expresiones regulares y el instrumento de anotación sí son aportaciones propias reutilizables bajo la licencia del código/documentación.

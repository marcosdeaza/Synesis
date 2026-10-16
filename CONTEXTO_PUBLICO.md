# Synesis · continuidad pública

**Estado actual:** repositorio público [marcosdeaza/Synesis](https://github.com/marcosdeaza/Synesis), rama `main`. Publicada y verificada la carpeta `data/research_225/` por petición expresa del responsable, que confirma disponer de permiso para publicarla y para investigación y eventual entrenamiento. Se conserva aparte el piloto CC0 de diez registros.

La auditoría contiene 225 registros reales. La carpeta `data/research_225/` publica el snapshot completo (UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10, USP 5), con el permiso confirmado por el responsable en `PERMISSIONS.json`. `data/pilot/` conserva el subconjunto de diez registros con CC0 y evidencia verificable. Los diez están incluidos entre los 225; la unión no es 235.

La memoria operativa completa del origen se denomina `CONTEXTO.md`; deliberadamente no se incluye en esta distribución. Este archivo conserva el contexto necesario para continuar con los materiales públicos, sin afirmar acceso al inventario local completo.

## Decisiones que deben mantenerse

- Español principal. Universidad Europea de Valencia obligatoria en el diseño; UEV y UPV prioritarias para el trabajo de campo local. Sus 90 registros ahora están publicados en `data/research_225/spain.jsonl` por autorización confirmada del responsable.
- Metadatos, tesis, código y documentación tienen derechos distintos. CC0 de los metadatos seleccionados no se extiende a las obras ni a corpus de entrenamiento. Cada nueva fuente requiere evidencia y revisión por operación.
- No inferir uso de IA por estilo, detectores, fecha o menciones temáticas. No atribuir cambios a IA solo por proximidad temporal.
- No confundir emisión en repositorio, defensa, redacción o depósito. El subconjunto TU Berlin no tiene fecha académica confirmada y procede de trabajos seleccionados por nota y aval; no representa la producción total.
- Las auditorías históricas de `docs/FUENTES_*` describen el inventario local. `reports/PILOTO.md` y las figuras actuales describen el subconjunto CC0 de diez; `reports/research_225_validation.json` valida por separado los 225 registros de investigación.
- No incorporar datos de prueba al corpus; mantener autores, correos, abstracts y PDF fuera de la distribución actual.

## Cómo retomar

1. Leer `README.md`, `docs/PUBLICACION.md`, el protocolo y las fuentes.
2. Ejecutar `make reproduce`, sin red ni credenciales. Revisar el manifiesto y las incidencias.
3. Para ampliar, registrar licencia de metadatos, evidencia, condiciones técnicas, operación permitida y semántica de fechas antes de extraer o publicar datos.
4. Cambiar gráficos y denominadores según el corpus efectivamente distribuido. No reutilizar figuras del inventario local como si fueran resultados públicos.
5. Registrar cada decisión nueva en este archivo y mantener protocolo, diccionario, permisos y pruebas consistentes.

Pendientes: documentar nuevas operaciones sobre texto completo del núcleo valenciano, auditar fechas académicas, balancear cohortes/disciplinas, anotar evidencia humana y prerregistrar antes de análisis confirmatorio. No se han entrenado modelos con estos trabajos. El investigador confirmó visibilidad pública; la distribución remota está en https://github.com/marcosdeaza/Synesis. El exportador por sí solo no realiza publicación remota.


## Verificación de entrega · 16 de octubre de 2026

Exportación real completada: 10/10 registros TU Berlin, cero incidencias; 20/20 pruebas de software correctas. Figuras de composición, cobertura y cronología regeneradas para esta variante en PNG/SVG/PDF. Cero enlaces Markdown internos rotos. Cuaderno entregado sin outputs ni adjuntos.

En la entrega local anterior a la publicación, la carpeta estaba inicializada sin commit ni remoto, con autenticación e identidad por resolver; ese estado quedó superado por la publicación registrada abajo. La memoria local completa se conserva fuera de esta variante. El siguiente paso científico es documentar nuevas operaciones sobre texto completo del núcleo valenciano y verificar fechas; la publicación inicial ya se completó; su ampliación posterior se registra abajo.


## Publicación autorizada · 16 de octubre de 2026

- El usuario confirmó publicar código, documentación y únicamente el subconjunto de metadatos autorizado.
- Autenticación comprobada; cuenta efectiva `marcosdeaza`. Creado el repositorio público https://github.com/marcosdeaza/Synesis.
- Configurada identidad Git local con el nombre verificado de la cuenta y su dirección noreply de GitHub; no se atribuye con ello revisión o responsabilidad científica institucional.
- Alcance de datos conservado: diez registros TU Berlin, metadatos CC0 con evidencia. Los otros 215 registros locales no se incorporan al historial público.
- Actualizados README, cita y guía de publicación. Primer commit y push completados. La visibilidad pública y la rama `main` se verificaron mediante API de GitHub. Reproducción remota confirmada: [ejecución correcta](https://github.com/marcosdeaza/Synesis/actions/runs/38865478996), 20 pruebas y cero incidencias. Siguiente paso científico: cerrar permisos y semántica temporal del núcleo valenciano.

- Comprobación final de publicación: GitHub Actions completó correctamente el primer commit. Código y dataset publicados; no quedan pasos de autenticación o visibilidad pendientes.


## Ampliación pública a 225 registros · 16 de octubre de 2026

- Petición directa del investigador: subir los 225 registros en una carpeta para investigación y posible entrenamiento; confirma que dispone de permiso. No se solicitó otra aprobación.
- Incorporados `data/research_225/spain.jsonl` (190) y `global.jsonl` (35), idénticos byte a byte a los snapshots originales. `manifest.json` registra hashes, composición y solapamiento; `PERMISSIONS.json` conserva la declaración y su alcance sin asignar una licencia abierta nueva.
- Sin PDFs, resúmenes, campos de autoría ni emails. No se ha entrenado un modelo. Los 225 son metadatos reales, no 225 documentos completos.
- `make reproduce` ahora valida ambas colecciones por separado: hashes, 225 identidades únicas, recuentos, minimización y solapamiento exacto de los diez CC0. Las figuras y el análisis del piloto CC0 siguen sobre diez; no se presentan como resultados de 225.
- Las restricciones iniciales de distribución a solo diez corresponden a la entrega histórica anterior. La decisión posterior del responsable amplía el alcance publicado a 225 mediante una autorización documentada distinta de CC0.
- Publicación completada en el commit `21d4955`. GitHub verificó los 225 registros, las 20 pruebas existentes y la reproducción del piloto sin diferencias: [ejecución correcta](https://github.com/marcosdeaza/Synesis/actions/runs/38866772837). Se descargaron los dos archivos desde la API de GitHub y sus hashes y recuentos coinciden con los originales.
- Siguiente paso: definir el experimento que vaya a usar estos metadatos; no se ha iniciado entrenamiento en esta petición.

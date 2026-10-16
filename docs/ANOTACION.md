# Anotación humana y evidencia

La tabla `config/annotations_template.csv` está vacía deliberadamente: aún no hay anotación humana ni verdad de referencia. No se sustituyen esos datos por etiquetas generadas.

## Variables y valores

| Campo | Regla |
|---|---|
| `record_id` | Identificador real existente en `data/pilot/`; una tesis por unidad |
| `annotator_id` | Seudónimo interno estable, sin nombre ni email |
| `topic_ai` | `yes`, `no`, `uncertain`; el tema aborda IA generativa, no simplemente tecnología |
| `declared_use_status` | `explicit_use`, `explicit_nonuse`, `unclear`, `not_observed`, `not_accessible` |
| `evidence_source` | URL del registro/documento autorizado o referencia interna permitida |
| `evidence_location` | Página/sección o campo exacto; el enlace debe poder auditarse |
| `evidence_note` | Paráfrasis breve, sin texto personal ni copia extensa |
| `date_checked` | Fecha ISO de revisión |
| `rights_reviewed` | Referencia a la decisión de permisos de esa fuente/obra |

`not_observed` significa que se revisó el material disponible sin encontrar una declaración. Nunca se interpreta como no uso. `explicit_nonuse` sigue siendo una declaración, no una verificación forense. Un trabajo cuyo tema sea ChatGPT puede tener cualquier estado de uso declarado.

Dos personas anotan independientemente el mismo subconjunto estratificado por idioma, nivel, institución y periodo, tras un ejercicio de calibración separado de evaluación. Medir acuerdo observado, matrices de confusión y kappa por variable; documentar la prevalencia y los casos inciertos. Resolver discrepancias con una tercera lectura registrada, preservando las dos etiquetas originales y la adjudicación.

Para ampliar al texto completo, cerrar antes los permisos de acceso y minería. Mantener las citas breves o notas de evidencia en almacenamiento restringido cuando corresponda. No publicar información sensible, nombres o evaluaciones individuales.

El plan de análisis define los mínimos y la política para desconocidos; ningún script debe convertir cadenas vacías en `no` ni fusionar `not_accessible` con `not_observed`.

# Preparación de experimentos sin entrenamiento

```sh
python3 scripts/prepare_experiment.py --seed 42
```

Se generan `data/derived/experiments/split_assignments.csv` y `manifest.json`. El CSV contiene **una fila por cada uno de los 225 `record_id`** del snapshot de investigación, incluidos los que carecen de PDF. El piloto CC0 de diez no se suma de nuevo. Esto prepara asignaciones; no añade etiquetas de uso de IA ni entrena un modelo.

Antes de repartir, el script agrupa transitivamente los trabajos que comparten el SHA-256 exacto de cualquier PDF registrado en `sources_*.jsonl`: si A comparte un archivo con B y B otro con C, A/B/C forman un único grupo. Todas las páginas, fragmentos y anexos de un trabajo deben heredar su asignación. La regla evita separar copias exactas entre entrenamiento y evaluación; no detecta por sí sola duplicados de contenido con bytes distintos, plantillas compartidas o datos derivados relacionados.

El identificador de grupo es el SHA-256 de sus miembros ordenados. Se combina con la semilla, se vuelve a calcular SHA-256 y se asigna según el entero módulo 10.000: posiciones 0–7.999 a `train`, 8.000–8.999 a `validation` y 9.000–9.999 a `test`. **80/10/10 son proporciones aproximadas por grupo**, sin cuotas exactas por registro: grupos de tamaños diferentes pueden cambiar mucho las proporciones observadas.

Esta partición **no está estratificada y no es temporal**. No garantiza comparabilidad entre universidades, ausencia de otras fugas ni interpretación causal. Para un estudio longitudinal se debe diseñar y congelar otra partición según el protocolo, sin renombrar esta como si separase cohortes. La falta de PDF no se convierte en una etiqueta negativa ni autoriza a tratar metadatos como texto completo.

El manifiesto registra semilla, regla, recuentos, SHA-256 de ambos archivos de metadatos, manifiestos de adquisición y documentos de control disponibles, además del hash del CSV. `acquisition_complete=false` indica que todavía faltan resultados de adquisición: repetir después de completar o cambiar los manifiestos, pues nuevos PDF idénticos pueden unir grupos y modificar asignaciones. Congelar los inputs y el resultado antes de ajustar modelos.

La ejecución es local, determinista para los mismos archivos y semilla, y usa exclusivamente la biblioteca estándar. Las pruebas de `tests/test_experiment.py` usan fixtures sintéticos independientes: verifican cohesión transitiva por PDF idéntico, conservación de 225 identidades, estabilidad ante reordenación y rechazo de identidades desconocidas o duplicadas.

# Distribución pública y auditoría local

Synesis mantiene dos alcances distintos. La **auditoría local inicial comprende 225 registros reales**: UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10 y USP 5. Sirve para auditar fuentes y preparar la investigación; sus permisos no son uniformes. La **variante pública inicial distribuye únicamente 10 registros de TU Berlin** con `metadata_license` exactamente `CC0-1.0` y una URL concreta que documenta esa licencia. El número efectivo siempre se comprueba en `PUBLIC_EXPORT_MANIFEST.json` y `reports/manifest.json` de la variante exportada.

La [ayuda de DepositOnce](https://depositonce.tu-berlin.de/info/help) declara sus metadatos bajo CC0. Esta selección se limita a metadatos bibliográficos minimizados: **no extiende CC0 a las tesis, PDF, imágenes o materiales de terceros**, ni deduce derechos de entrenamiento sobre esas obras. La licencia del código y los términos de los documentos propios se consultan en `RIGHTS.md` y `LICENSE`. Este documento registra decisiones operativas del proyecto y su evidencia; no ofrece asesoría legal general.

## Qué permanece y qué se excluye

UEV continúa siendo obligatoria en el diseño, el registro institucional y la investigación local. Sus 90 registros **no se redistribuyen todavía**, porque no se ha cerrado el alcance de publicación de sus metadatos. La misma separación se aplica a los demás registros sin evidencia suficiente para esta variante. La exclusión pública no elimina las instituciones de la investigación ni convierte derechos desconocidos en una prohibición universal.

Un inventario local de referencias con derechos pendientes puede conservar la procedencia y los desconocidos sin presentarse como corpus abierto. Cada futura distribución debe registrar fuente, campos, evidencia y operación revisada. El acceso OAI, la visibilidad pública y una licencia de la obra no sustituyen esa decisión. No se publica automáticamente un subconjunto solo por omitir resúmenes o autoría.

El exportador usa una lista cerrada de rutas:

- Código `src/`, pruebas `tests/`, herramientas `scripts/`, documentos `docs/`, configuración `config/`, notebooks y automatización `.github/`.
- Identidad propia `assets/banner.png`, licencia, derechos, contribución, cita del proyecto y archivos de construcción/configuración de la raíz.
- Un nuevo `data/pilot/rights_cleared.jsonl`, seleccionado con la regla de metadatos CC0 y evidencia URL, mediante una proyección explícita de campos sin autoría ni correos. `abstract` se mantiene en `null`.
- Un `README.md` propio de la variante, `CONTEXTO_PUBLICO.md` y un manifiesto de exportación. La memoria local completa no se incluye: `CONTEXTO.md` se sustituye por un índice a `CONTEXTO_PUBLICO.md`.

No copia los datasets originales `spain.jsonl`/`global.jsonl`, respuestas brutas, cosechas, cachés, datos privados, `.git`, informes/features anteriores ni las figuras de la auditoría de 225 registros. Los outputs y adjuntos de notebooks se eliminan. Los fixtures sintéticos de las pruebas sirven exclusivamente para verificar el software y no se incorporan al corpus científico.

Las auditorías de `FUENTES_ESPANA.md` y `FUENTES_GLOBALES.md` conservan su significado histórico y pueden describir 225 registros. En cambio, los informes de `reports/` de la variante pública se reconstruyen sin red utilizando exclusivamente `rights_cleared.jsonl`. Las figuras deberán generarse después para ese mismo subconjunto, con denominadores y rótulos revisados. El exportador no transporta imágenes de resultados anteriores.

## Cómo preparar una variante nueva

Desde la raíz de la auditoría local, con Python 3.11 o posterior:

```sh
python3 scripts/export_public.py --output ../synesis-public
```

`--output` es obligatorio. El destino debe ser nuevo y estar fuera del repositorio de origen. El script rechaza rutas existentes, incluso enlaces simbólicos, y nunca mezcla contenido con una carpeta previa. La lectura y selección se validan antes de crear el destino. Si la reconstrucción posterior falla, la carpeta incompleta se conserva para inspección; no se presenta como exportación terminada ni se sobrescribe en un reintento.

El exportador y el pipeline usan solo la biblioteca estándar. No realizan consultas de red, autenticación, operaciones Git ni publicación remota. La regla exacta de selección es:

```text
metadata_license == "CC0-1.0"
AND metadata_license_evidence_url es una URL HTTP(S) no vacía
```

Esta regla mecánica aplica la evidencia que ya se revisó en las fuentes; no determina por sí misma los derechos de una fuente nueva. El manifiesto conserva recuentos e identificadores/hash de archivos de origen, sin incluir sus filas excluidas. Cada registro distribuido conserva el enlace a su fuente y a la evidencia de licencia.

Después de exportar:

```sh
cd ../synesis-public
make reproduce
```

Comprobar los 10 registros y la ausencia de originales, cachés y figuras heredadas. Si se quieren imágenes, instalar las dependencias opcionales de figuras y regenerarlas sobre los informes públicos; esa fase no forma parte de la exportación mínima. La memoria pública debe actualizarse con decisiones posteriores, sin asumir que quien descarga esta variante dispone de la auditoría local completa.

## GitHub: publicación pública

El investigador confirmó visibilidad **pública** el 16 de octubre de 2026. Repositorio: [marcosdeaza/Synesis](https://github.com/marcosdeaza/Synesis).

La distribución remota contiene código, documentación propia y los diez registros de metadatos CC0 verificados. El inventario local de 225 registros y sus respuestas brutas permanecen fuera de esa distribución. La elección de visibilidad no amplía derechos sobre contenidos de terceros.

Los cambios se versionan en la rama `main` y las comprobaciones automáticas reproducen el subconjunto publicado. La memoria para continuar se mantiene en `CONTEXTO_PUBLICO.md`; la memoria completa local está en el directorio de investigación original. No almacenar credenciales en archivos, commits ni manifiestos.

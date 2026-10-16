# Distribución pública: colección de 225 y piloto CC0

Synesis publica **225 registros reales y únicos de metadatos**: UEV 90, UPV 100, MIT 10, TU Berlin 10, HKUST 10 y USP 5. Se encuentran en [`data/research_225/`](../data/research_225/), repartidos entre [`spain.jsonl`](../data/research_225/spain.jsonl) y [`global.jsonl`](../data/research_225/global.jsonl), junto con su [README](../data/research_225/README.md), [manifiesto](../data/research_225/manifest.json) y [registro de permiso](../data/research_225/PERMISSIONS.json).

El responsable confirmó que cuenta con permiso y pidió expresamente publicar esta carpeta para su posible uso en investigación y entrenamiento posterior. `PERMISSIONS.json` conserva el origen y alcance de esa declaración. **No es una verificación independiente del permiso ni una autorización institucional verificada**; no se inventan documentos, emisores, condiciones de sublicencia ni otros detalles no aportados. La publicación solicitada se realiza sin convertir la declaración en una licencia CC0, MIT o CC BY para los metadatos.

## Dos colecciones con funciones distintas

| Colección | Alcance | Fundamento registrado | Reproducción |
|---|---|---|---|
| `data/research_225/` | 225 metadatos de las seis fuentes, incluidos 90 de UEV | Permiso confirmado por el responsable; licencias observadas por fuente conservadas | Su manifiesto identifica archivos, recuentos y hashes |
| `data/pilot/rights_cleared.jsonl` | 10 metadatos de TU Berlin | Evidencia institucional de metadatos CC0-1.0 por fila | `make reproduce`, `reports/` y figuras analíticas |

Los diez registros del piloto están incluidos en la colección completa. **Hay 225 trabajos únicos, no 235.** UEV sigue siendo obligatoria en el diseño y sus 90 registros ya se distribuyen en la carpeta de investigación.

La [ayuda de DepositOnce](https://depositonce.tu-berlin.de/info/help) declara sus metadatos bajo CC0. Esa evidencia corresponde al piloto y a las filas pertinentes de la colección completa; no se extiende al resto de fuentes ni a tesis, PDF, imágenes u otras obras. La licencia del código y las condiciones de documentos propios se consultan en [RIGHTS.md](../RIGHTS.md) y `LICENSE`.

## Material incluido y excluido

La distribución contiene código `src/`, pruebas `tests/`, herramientas `scripts/`, documentación `docs/`, configuración `config/`, notebooks sin outputs, automatización `.github/`, identidad propia y archivos de construcción. Se añaden las dos colecciones descritas arriba. Se conservan títulos, identificadores, fechas, materias, evidencia de nivel, procedencia y condiciones de derechos observadas según el esquema minimizado.

**No se incluyen PDFs, texto completo, resúmenes, campos de autores/directores/correos, respuestas brutas, cosechas, cachés o datos privados.** Los títulos y enlaces pueden llevar a personas identificables: minimización no equivale a anonimización. Las peticiones de corrección o retirada deben preservar la privacidad de quienes las formulen. No se ha entrenado un modelo con estos trabajos ni se publican pesos derivados de ellos.

La declaración del responsable se refiere a la colección de metadatos entregada. No modifica los campos `license`, `metadata_license`, `rights_statement` o `access_rights`, y no se extrapola a contenido que no esté en la carpeta. La preparación para entrenamiento futuro deberá documentar la tarea, campos, particiones y alcance utilizados; no se convierte un corpus de títulos en un corpus de texto completo.

## Exportador base y ampliación autorizada

El exportador existente prepara una **base pública CC0 de 10 filas**. Desde la raíz de la auditoría local, con Python 3.11 o posterior:

```sh
python3 scripts/export_public.py --output ../synesis-public
```

`--output` es obligatorio. El destino debe ser nuevo y estar fuera del repositorio de origen. El script rechaza rutas existentes, incluso enlaces simbólicos, y no mezcla contenido con una carpeta previa. La lectura y selección se validan antes de crear el destino. Si la reconstrucción posterior falla, la carpeta incompleta se conserva para inspección y no se presenta como exportación terminada.

El exportador y el pipeline usan la biblioteca estándar. No realizan consultas de red, autenticación, operaciones Git ni publicación remota. Su regla mecánica sigue siendo:

```text
metadata_license == "CC0-1.0"
AND metadata_license_evidence_url es una URL HTTP(S) no vacía
```

Esa regla selecciona el piloto; **no genera automáticamente la carpeta `research_225`**. La versión actual incorpora esa carpeta mediante una adición específica autorizada por el responsable, con permiso y manifiesto propios. Una nueva exportación base no debe presentarse como copia completa de esta distribución hasta incluir también la colección autorizada y comprobar su manifiesto. No sustituirla silenciosamente por los archivos locales ni aplicar la regla CC0 como si describiera el permiso declarado sobre los 225.

El exportador base no copia los originales locales, respuestas brutas, cachés, `.git`, informes anteriores ni figuras de la auditoría completa. Elimina outputs y adjuntos de notebooks. Los fixtures sintéticos sirven únicamente para verificar el software y no se incorporan al corpus científico. La memoria local completa permanece fuera de la distribución; la continuidad pública se mantiene en `CONTEXTO_PUBLICO.md`.

## Manifiestos, informes y figuras

- [`data/research_225/manifest.json`](../data/research_225/manifest.json) identifica los archivos y 225 registros de la colección completa.
- [`data/research_225/PERMISSIONS.json`](../data/research_225/PERMISSIONS.json) registra la declaración del responsable y su origen, diferenciada de licencias institucionales observadas.
- `PUBLIC_EXPORT_MANIFEST.json` describe la selección de la exportación base CC0.
- `reports/manifest.json` y los informes analíticos corresponden únicamente al piloto de 10.
- [`reports/research_225_validation.json`](../reports/research_225_validation.json) contiene la comprobación separada de integridad, recuentos y unicidad de los 225 metadatos.

Las auditorías de [España](FUENTES_ESPANA.md) y [comparadores internacionales](FUENTES_GLOBALES.md) describen los 225 registros originales, ahora disponibles en `research_225`. Las figuras analíticas incluidas reflejan el piloto de 10; no se interpretan como gráficos de la colección completa. La cronología es una figura contextual de hitos tecnológicos, independiente de esos denominadores.

Para validar los 225 y reconstruir por separado el análisis piloto sin red:

```sh
make reproduce
```

`make reproduce` ejecuta `scripts/check_research_snapshot.py` para validar la colección completa, además de reconstruir y probar el pipeline analítico de diez. Comprobar 225 registros en el informe de validación y diez entradas en el manifiesto analítico. Para las figuras, instalar las dependencias opcionales `.[figures]` y ejecutar `make figures`. Un análisis futuro de los 225 tendrá salidas y denominadores identificados por separado, sin mezclar silenciosamente sus resultados con los del piloto.

## Publicación y continuidad

El investigador confirmó visibilidad pública y posteriormente solicitó la publicación de los 225 registros declarando que cuenta con permiso. Repositorio: [marcosdeaza/Synesis](https://github.com/marcosdeaza/Synesis). Las licencias y condiciones observadas se preservan por fuente; una decisión de visibilidad no las sustituye.

Los cambios se versionan en `main`. Las comprobaciones automáticas validan los 225 y reproducen por separado el análisis del piloto CC0; cada colección conserva su propio manifiesto. La memoria pública debe registrar los cambios de alcance y las versiones posteriores, sin asumir acceso al directorio local original. No almacenar credenciales en archivos, commits ni manifiestos.

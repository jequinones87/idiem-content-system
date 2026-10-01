# Librería de fotos IDIEM — guía para compilar

Objetivo: reunir y etiquetar las fotos (propias, stock licenciado, personas) para
que el motor pueda pedir una foto por post (disciplina + entorno + orientación) y
el equipo elija. Una foto puede servir a **varias células y subtemas**.

## 1. Cómo nombrar cada foto (lo que tú haces)

Nombra por **concepto**, en minúsculas, separando conceptos con `-` dentro de un
término y con `_` entre términos. Opcional al final: orientación `H`/`V`/`C`.

```
faena-minera_dron_H.jpg
triaxial_laboratorio_V.jpg
hospital_sustentabilidad_C.jpg
soldadura_end-soldadura.jpg        (sin orientación = se completa a mano)
```

- Usa los **conceptos del diccionario** (`concept_dictionary.json`). Si falta uno,
  agrégalo tú a la planilla y yo lo sumo al diccionario.
- Puedes poner **1 a 3 conceptos** por foto. La foto hereda la **unión** de células
  y subtemas de esos conceptos (por eso "faena-minera" sirve a IOM **y** LMD).

## 2. Qué llena el equipo vs. qué deriva el sistema

En la planilla (`photo_manifest_template.csv`, ábrela en Google Sheets):

| Campo | ¿Quién? |
|---|---|
| `archivo` | **Tú** (nombre del archivo) |
| `concepto` | **Tú** (los conceptos del nombre) |
| `orientacion` | **Tú** (H/V/C) |
| `tipo` | **Tú** (propia_idiem / stock_licenciada / persona) |
| `derechos` | **Tú** (propia / licencia_vigente / con_credito + caducidad si aplica) |
| `personas` / `consentimiento` | **Tú** (si hay personas identificables) |
| `fuente` | **Tú** (link de Drive, o proveedor de stock) |
| `notas` | **Tú** (opcional) |
| `celulas` · `subtemas` · `disciplina` · `entorno` | **Yo, automático** desde el concepto |

Es decir: tú nombras bien la foto + llenas derechos/fuente; yo completo el resto.

## 3. Estructura sugerida en Drive

```
IDIEM_Librería_Fotos/
  01_Propias/          fotos propias de IDIEM (obra, faena, laboratorio, personas)
  02_Stock/            stock licenciado (guardar comprobante de licencia)
  03_Personas/         relatores / equipo (con consentimiento)
  photo_manifest.csv   la planilla (esta guía)
```

## 4. Reglas importantes

- **Derechos primero:** si una foto no tiene licencia vigente o consentimiento, no
  entra a la selección automática (queda marcada para revisión).
- **La foto es complemento, no relleno:** el motor pedirá foto solo para subtemas
  "de terreno/obra/faena/laboratorio"; los conceptuales usan gráfica template.
- **Sin datos falsos:** las fotos no deben insinuar proyectos/clientes que no sean
  reales; para eso está la evidencia 2A.2/2A.3.

## Archivos
- `concept_dictionary.json` — conceptos → célula(s)/subtema(s)/disciplina/entorno.
- `photo_manifest.schema.json` — esquema de cada registro (validación futura).
- `photo_manifest_template.csv` — planilla para llenar (con ejemplos).

# QgisTreeBenefits — QGIS plugin

TUTORIAL Youtube: https://youtu.be/lXhd-kAPRpI?si=47gRPP1OnuTzTyJK

*Author: **ALIAS ATP** · alias@aliasinfo.it · aliasinfo.it · QGIS ≥ 3.22 · version 0.4*

🇮🇹 *Versione italiana: [README.md](README.md)*

A **Processing** plugin for QGIS that reproduces the calculations of the Orebla
webapp and applies them in batch to a layer of **tree points**, returning a new
layer with the estimated environmental benefits of every tree.

**New in 0.4**: the interface is available in **Italian and English**, and a
generic reference entry has been added for use **outside Italy**.

## What it computes (per tree)

- **Ecological value**: biomass / stored CO₂ (kg), CO₂ sequestered (kg/year),
  O₂ produced (kg/year), pollutants removed (kg/year), environmental value (EUR).
- **Amenity value**: RAM logistic curve on the provincial *valmax*, with health
  and structural reductions. Requires a reference area (or the generic `ZZ`).
- **Annual runoff** avoided (m³/year) + water saving (EUR) + class.
- **Storm-event runoff** (e.g. TR50) avoided (m³) + event class.
- **Summer cooling**: mean ΔT and ΔT for the four aspects (N/E/W/S), energy
  saved (kWh), CO₂ avoided (kg), saving (EUR), area and radius of influence.
- **(optional) Advanced CO₂**: branch biomass with a decay reduction factor.
- **(optional) Mobility simulations**: CO₂ of the home↔school/work commute and
  the number of equivalent trees needed to offset it.

The logic, coefficients, lookup tables and the datasets of **261 species** and
**107 Italian provinces** are a faithful port of `orebla_calc.js` and
`orebla_dati.js`.

## Interface language

The plugin starts in the language of the QGIS interface (Italian if QGIS is in
Italian, English otherwise) and can be switched at any time:

- from the **selector at the top right** of the assessment window;
- from **Plugins → QgisTreeBenefits → Language / Lingua**;
- per run, from the **Label language** parameter of the two Processing algorithms.

### What changes and what does not

| Changes with the language | Stays the same |
|---|---|
| field labels (aliases) | field **names** (`specie`, `dbh`, `ob_valgl`…) |
| drop-down entries | **stored values** (`albero adulto`, `codominante`…) |
| tab titles, messages, help | species and province names (proper nouns) |
| runoff class text in the output | every numeric value |

This is the central design choice: **an inventory created in English computes
correctly in Italian and vice versa**, projects are interchangeable and the
numeric results are identical in both languages. In practice you pick "Mature
tree" from the drop-down and the field stores `albero adulto` — the value the
calculation engine expects.

## Using the plugin outside Italy

The first entry of the reference-area list is the generic
**«Italy average (non-Italian use)»** — code **`ZZ`**. Its `valmax` is the
**arithmetic mean** of the Orebla maximum values of the 107 Italian provinces
(**EUR 112,399.79**), intended for users who have no local reference maximum.
The amenity value is then computed on an average Italian basis with the same RAM
logistic curve — treat it as an order of magnitude, and where a national or
local reference value exists, prefer it.

The `provincia` field also accepts the aliases `ZZ`, `INT`, `EXTRA-ITALIA`,
`OUTSIDE ITALY`, `Italy average (non-Italian use)`.

None of the other modules contains Italy-specific parameters:

- **latitude** is read from the point geometry (any latitude works);
- the suggested **UTM output CRS** follows the actual zone of the layer, in both
  hemispheres (e.g. EPSG:32721 Buenos Aires, EPSG:32756 Sydney);
- **climate data** must be entered with your local figures. In the **southern
  hemisphere**, fill the "summer" fields (`prec_giu_ago`, `n_eventi_giu_ago`,
  `rad_globale_giu_ago`, `tmax_media_estiva`…) with **December–February** data.

Monetary results stay in **EUR**, because the reference values and the unit costs
used in the models (energy, water) are European. Convert them afterwards.

## Installation

1. In QGIS: *Plugins → Manage and Install Plugins → Install from ZIP*, select
   `QgisTreeBenefits_v04.zip`.
2. The inventory tools appear in the **Processing Toolbox**, under
   **QgisTreeBenefits → Tree benefit assessment**:
   - **1 · Create tree inventory (empty tabbed layer)**
   - **2 · Import/adapt an existing tree layer**
3. The **benefit assessment** is in the **Plugins → QgisTreeBenefits** menu.

Upgrading from 0.3 requires no data conversion.

## 1) Create tree inventory (empty layer)

Creates an empty point layer with **all the parameter fields**: labels in the
chosen language, **drop-down menus** for categorical fields and an **attribute
form organised in TABS** (Basic / Advanced / Climate data). Pick the CRS (default:
project CRS), then start editing and digitise your trees.

## 2) Import/adapt an existing tree layer

Converts your own tree layer into one compatible with the calculator:

- you map the **species field** and the **biometric fields**;
- **species** are matched automatically against the library by closest name; the
  **log** reports every match with its similarity score (below 60% flagged with
  "CHECK");
- the resulting layer is already **tabbed with drop-downs**, with species and
  biometry pre-filled.

## 3) Benefit assessment (tabbed window)

Plugins → QgisTreeBenefits → "Benefit assessment". Tabs: Basic / Advanced /
Climate data / Options & Output / Info / Help. You map the fields (automatic when
the names match); **climate data** can come from the layer **or** be entered as a
single **constant** for every tree. Options: advanced CO₂, mobility, generation of
the **areas of influence** and **output CRS (UTM)**.

## UTM output and areas of influence

The output is reprojected into the chosen **UTM CRS** (in metres), so `ob_rinf`
(radius of influence, m) and `ob_area` (m²) can be used directly for buffers. The
**areas of influence** polygons can be produced automatically
(buffer = radius of influence).

## Conventional field names (identical in every language)

Identification: `cod_alb`, `specie`, `provincia`, `fito`
Biometry: `h`, `dbh`, `circonf`, `d_ch`, `inser_c`, `stadio`, `vital`,
`p_soc`, `cond_staz`, `chioma_tr`
Condition/context: `cast_p`, `strumenti`, `dimora`, `organizzazione`,
`fus_p`, `localizzazione`
Climate: `prec_annua`, `n_eventi_pioggia`, `prec_evento`, `rr_evento`,
`tmax_media_estiva`, `vento_medio_estivo`, `umidita_rel_estiva`, `prec_giu_ago`,
`n_eventi_giu_ago`, `rad_globale_giu_ago`, `latitudine`
Optional: `km_eco`, `riduzione`

### Field name glossary

| Field | Meaning |
|---|---|
| `cod_alb` | tree code |
| `specie` / `provincia` / `fito` | species / reference area / phytoclimatic match (A–E) |
| `h` / `dbh` / `circonf` | total height (m) / stem diameter (cm) / stem girth (cm) |
| `d_ch` / `inser_c` | crown diameter (m) / crown base height (m) |
| `stadio` / `vital` / `p_soc` | growth stage / vitality 1–7 / social position |
| `cond_staz` / `chioma_tr` | site conditions 1–7 / crown transparency |
| `cast_p` / `strumenti` | vegetative condition 1–13 / structural integrity 1–5 |
| `dimora` / `organizzazione` | planting site type / urban context |
| `fus_p` / `localizzazione` | legal protection / functional location |
| `prec_annua` / `n_eventi_pioggia` | annual rainfall (mm) / rain events per year |
| `prec_evento` / `rr_evento` | event rainfall (mm) / event rain rate (mm/h) |
| `tmax_media_estiva` | mean summer Tmax (°C) |
| `vento_medio_estivo` / `umidita_rel_estiva` | mean summer wind (m/s) / mean RH (%) |
| `prec_giu_ago` / `n_eventi_giu_ago` | warm-season rainfall (mm) / events, 3 months |
| `rad_globale_giu_ago` | warm-season global radiation (MJ/m²), 3 months |
| `km_eco` / `riduzione` | daily round-trip km / decay reduction factor |

## Categorical vocabularies (stored values, case-insensitive)

Stored values are **never translated**: in English you read "Mature tree" and the
field holds `albero adulto`.

- **stadio**: plantula (seedling) · pianta giovane (young plant) · albero giovane
  (young tree) · albero adulto (mature) · albero adulto avanzato (late-mature) ·
  albero senescente (senescent) · albero veterano (veteran)
- **vital** (1..7): 1 = worst … 7 = best
- **p_soc**: predominante · dominante interna · dominante margine · codominante ·
  intermedia · dominata (overtopped) · sottoposta (suppressed) ·
  libera (giovane) · isolata
- **chioma_tr**: scarsa (very sparse) · bassa (low) · media (medium) · alta (high)
- **organizzazione**: centro storico (historic centre) · centro città (city centre) ·
  periferia antica · periferia recente · luoghi villeggiatura · zone industriali ·
  aree rurali urbaniz. · aree rurali
- **fus_p**: nessuno · tutela comunale · rilevanza comunale · paesaggistico ·
  storico-architettonico · monumentale
- **localizzazione**: alberata stradale · parcheggio · piazza · plesso scolastico ·
  impianto sportivo · giardino/parco recente · giardino/parco storico · bosco ·
  cimitero · terreno agricolo
- **cast_p** (1..13) · **strumenti** (1..5) · **cond_staz** (1..7)

The drop-down menus present all of these in English; you never need to type the
Italian value by hand unless you are preparing a CSV outside QGIS.

## Output fields (prefix `ob_`)

Names are the same in every language; only the displayed label changes.

| Field | Meaning |
|---|---|
| ob_spec / ob_prov | matched species / reference area |
| ob_co2stoc | stored CO₂ / biomass (kg) |
| ob_co2seq | CO₂ sequestered (kg/year) |
| ob_o2 | O₂ produced (kg/year) |
| ob_inq | pollutants removed (kg/year) |
| ob_valeco | environmental value (EUR) |
| ob_valorn | net amenity value (EUR) |
| ob_qorn | base amenity index Q |
| ob_valgl | total value, eco + amenity (EUR) |
| ob_runmc / ob_runeur / ob_runcls | annual runoff m³ / EUR / class |
| ob_runevmc / ob_runevcl | storm-event runoff m³ / event class |
| ob_raffdt | mean cooling ΔT (°C) |
| ob_kwh / ob_raffco2 / ob_raffeur | energy / CO₂ / EUR saved through cooling |
| ob_area / ob_rinf | area / radius of influence |
| ob_dtN ob_dtE ob_dtO ob_dtS | ΔT per direction: North, East, West, South (°C) |
| ob_co2avf / ob_valecav / ob_valglav | advanced CO₂ / advanced eco value / advanced total |
| ob_mauto ob_mbus ob_mnauto ob_mnbus | mobility: car and bus CO₂, trees to offset |

Fields that cannot be computed (missing inputs) stay NULL, as in the webapp.

## Example datasets

- `esempio/alberi_esempio.csv` — 3 trees in the province of Vicenza, Italy
  (WKT, EPSG:4326).
- `esempio/trees_example_international.csv` — 6 trees in Lisbon, Lyon and Sydney
  with `provincia = ZZ`, to try the non-Italian workflow and the southern
  hemisphere.

In QGIS: *Layer → Add Delimited Text Layer*, WKT geometry, field `wkt`.

## Diagnostics

Optional operations (APIs that differ between Qt5 and Qt6, invalid geometries,
attribute-form configuration) never abort a run, but they are recorded in
*View → Panels → Log Messages*, tab **QgisTreeBenefits**. If something does not
behave as expected, that tab tells you what was skipped.

## Notes

- The plugin works from the Toolbox, the **Graphical Modeler** and in **batch**,
  like any Processing algorithm.
- Output can be GeoPackage, Shapefile, memory, etc. For Shapefile the `ob_*`
  names are already ≤ 10 characters.
- **Disclaimer**: demonstration and teaching tool. Results do not constitute an
  expert appraisal, an official technical assessment, or a document with legal or
  commercial standing. Orebla method: Luigi Sani. Cooling and runoff models:
  ALIAS ATP.

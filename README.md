# QgisTreeBenefits

**Stima dei benefici ambientali degli alberi urbani in QGIS.**

QgisTreeBenefits riproduce in ambito QGIS i calcoli della **piattaforma ARBOREO di ALIAS ATP**: a partire da un dataset di punti‑albero stima, per ogni esemplare, il valore ecologico, il valore ornamentale, il runoff evitato (annuo e da evento), il raffrescamento estivo e — opzionalmente — la CO₂ stoccata avanzata e alcune simulazioni di mobilità.

Il valore ornamentale ed ecologico segue il **metodo Orebla** (autore: *Luigi Sani*); i modelli di raffrescamento estivo e runoff evitato sono elaborati da **ALIAS ATP**.

> ⚠️ **Uso dimostrativo e didattico.** I risultati non costituiscono perizia, valutazione tecnica ufficiale o documento con valore legale o commerciale.

- **Autore:** ALIAS ATP — [aliasinfo.it](https://www.aliasinfo.it) — alias@aliasinfo.it
- **Versione:** 0.1
- **Compatibilità:** QGIS 3.22 → 4.99
- **Categoria:** Analysis · *Processing provider*

---

## Indice

- [Caratteristiche](#caratteristiche)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Strumenti del plugin](#strumenti-del-plugin)
  - [1 · Crea inventario alberi](#1--crea-inventario-alberi-layer-vuoto-a-schede)
  - [2 · Importa/adatta layer esistente](#2--importaadatta-layer-alberi-esistente)
  - [3 · Stima benefici](#3--stima-benefici-ambientali)
- [Parametri di input](#parametri-di-input)
- [Campi di output](#campi-di-output-ob_)
- [Output in UTM e aree di influenza](#output-in-utm-e-aree-di-influenza)
- [Dataset e metodologia](#dataset-e-metodologia)
- [Dati di esempio](#dati-di-esempio)
- [Struttura del repository](#struttura-del-repository)
- [Licenza e crediti](#licenza-e-crediti)

---

## Caratteristiche

- Calcolo dei benefici ambientali per ogni punto‑albero, fedele al modello ARBOREO/Orebla.
- **Inventario alberi** generato come layer vuoto con **menu a tendina** e **modulo attributi a schede** (Dati base / avanzati / climatici).
- **Importazione guidata** di un layer esistente, con **abbinamento automatico delle specie** alla libreria del plugin (nome più simile) e mappatura dei dati biometrici.
- **Stima benefici** disponibile sia come **finestra a schede** (menu Plugin) sia come **algoritmo Processing** (batch/modellatore).
- Dati climatici prelevabili **da un campo** del layer oppure inseribili come **costante** unica.
- **Fattore di riduzione** (per la CO₂ avanzata) da campo o valore predefinito.
- Output riproiettato in **UTM** (metri) e generazione opzionale dei **poligoni delle aree di influenza**.
- Libreria di **261 specie** e **107 province** italiane.

## Requisiti

- QGIS **3.22 o superiore** (testato fino alla serie 4.x).
- Nessuna dipendenza esterna: usa solo le librerie di QGIS/Qt e la libreria standard di Python.

## Installazione

1. Scarica l'archivio `QgisTreeBenefits.zip` (o crealo comprimendo la cartella `QgisTreeBenefits/`).
2. In QGIS: **Plugin → Gestisci e installa plugin → Installa da ZIP**, seleziona l'archivio e installa.
3. Dopo l'installazione trovi:
   - gli algoritmi nella **Cassetta degli strumenti di Processing → QgisTreeBenefits → Stima benefici alberi**;
   - la finestra a schede in **Plugin → QgisTreeBenefits → _Stima benefici (finestra a schede)…_**.

## Strumenti del plugin

Flusso consigliato: **crea o importa l'inventario → completa i parametri → esegui la stima benefici**.

### 1 · Crea inventario alberi (layer vuoto a schede)

Crea un layer di punti vuoto con **tutti i campi‑parametro** del modello. Il layer risultante ha:

- i **menu a tendina** (ValueMap) per i campi categoriali (specie, provincia, fascia fitoclimatica, stadio, vitalità, posizione sociale, condizioni, dimora, organizzazione, vincoli, localizzazione, fattore di riduzione…);
- il **modulo attributi organizzato in schede** (Dati base / Dati avanzati / Dati climatici);
- le **etichette dei campi** pronte per la stima.

Imposta il CRS (consigliato un **UTM** in metri se vuoi poi le aree di influenza), avvia l'editing e digitalizza gli alberi compilando i campi dalle tendine.

### 2 · Importa/adatta layer alberi esistente

Trasforma un layer‑alberi già in tuo possesso in un layer compatibile con il calcolatore (stessi nomi‑parametro → pesi corretti):

1. indica il **layer sorgente** e il **campo con la specie**;
2. la **specie** viene abbinata automaticamente alla **libreria del plugin** scegliendo il nome più simile (nome scientifico/comune); il log riporta ogni abbinamento con la percentuale di somiglianza (le voci sotto il 60 % sono segnalate da verificare);
3. **mappa i dati biometrici** (codice, altezza, DBH, circonferenza, diametro e inserzione chioma);
4. ottieni un nuovo layer **già a schede e con le tendine**, con specie e biometria precompilate; gli altri parametri si completano con lo stesso schema, e le specie dubbie si correggono dal campo a tendina.

### 3 · Stima benefici ambientali

Calcola, per ogni punto‑albero, le stime dei benefici. È disponibile in due modi con lo **stesso motore di calcolo**:

- **Finestra a schede** (menu Plugin → QgisTreeBenefits): più comoda per la compilazione, con schede **Dati base · Dati avanzati · Dati climatici · Opzioni & Output · ℹ Info · ❔ Guida**.
- **Algoritmo Processing** (`3 · Stima benefici ambientali alberi (Orebla)`): adatto a batch e Modellatore grafico; i parametri avanzati e climatici sono raccolti sotto *Parametri avanzati*.

Opzioni comuni: stima avanzata CO₂, simulazioni di mobilità, CRS di output (UTM) e generazione delle aree di influenza.

## Parametri di input

Per ogni parametro si indica il **campo del layer** che lo contiene; se i nomi coincidono con quelli dell'inventario, la mappatura è automatica. I parametri sono raggruppati in tre schede.

**Dati base** — codice albero, specie, provincia, fascia fitoclimatica (A…E), altezza, DBH, circonferenza, diametro chioma, inserzione chioma, stadio fenologico, vitalità (1–7), posizione sociale.

**Dati avanzati** — condizioni stazionali (1–7), trasparenza chioma, condizioni vegetative (1–13), integrità strutturale (1–5), tipo di dimora, organizzazione urbanistica, vincoli/tutele, localizzazione funzionale, fattore di riduzione (CO₂ avanzata), km percorsi al giorno (mobilità).

**Dati climatici** — precipitazioni annue, n° eventi pioggia/anno, precipitazione evento, rain rate evento, T max media estiva, vento medio estivo, umidità relativa media, precipitazioni giu–ago, n° eventi giu–ago, radiazione globale giu–ago. *Ogni voce climatica può provenire da un campo oppure da una costante.*

**Note:**

- **Specie**: id o nome (anche parziale, es. `Tilia cordata`).
- **Provincia**: sigla (`VI`) o nome (`Vicenza`); necessaria per il valore ornamentale.
- **Latitudine**: se non fornita, viene ricavata dalla geometria del punto.
- I confronti sui vocabolari categoriali sono *case‑insensitive*.

## Campi di output (`ob_`)

Il layer dei risultati conserva i campi originali e aggiunge i campi seguenti, con **etichette** e **modulo a schede** (Parametri albero · Riconoscimento · Valore & ecologia · Runoff · Raffrescamento · CO₂ avanzata & mobilità).

| Campo | Significato |
|---|---|
| `ob_spec` / `ob_prov` | specie / provincia riconosciute |
| `ob_co2stoc` | CO₂ stoccata / biomassa (kg) |
| `ob_co2seq` | CO₂ sequestrata (kg/anno) |
| `ob_o2` | O₂ prodotto (kg/anno) |
| `ob_inq` | inquinanti abbattuti (kg/anno) |
| `ob_valeco` | valore ambientale (€) |
| `ob_valorn` | valore ornamentale netto (€) |
| `ob_qorn` | Q ornamentale base |
| `ob_valgl` | valore globale (eco + orn) (€) |
| `ob_runmc` / `ob_runeur` / `ob_runcls` | runoff annuo: m³ / € / classe |
| `ob_runevmc` / `ob_runevcl` | runoff evento: m³ / classe |
| `ob_raffdt` | raffrescamento ΔT medio (°C) |
| `ob_kwh` / `ob_raffco2` / `ob_raffeur` | energia / CO₂ / € risparmiati (raffrescamento) |
| `ob_area` / `ob_rinf` | area / raggio di influenza (m² / m) |
| `ob_dtN` `ob_dtE` `ob_dtO` `ob_dtS` | ΔT per direzione (°C) |
| `ob_co2avf` / `ob_valecav` / `ob_valglav` | CO₂ avanzata / valore eco avanzato / globale avanzato |
| `ob_mauto` `ob_mbus` `ob_mnauto` `ob_mnbus` | mobilità: CO₂ auto/bus e alberi di compensazione |

I campi non calcolabili (input mancanti) restano `NULL`.

## Output in UTM e aree di influenza

L'output viene riproiettato nel **CRS UTM** scelto (in metri): così `ob_rinf` (raggio) e `ob_area` (m²) sono direttamente utilizzabili per i buffer. Spuntando l'apposita opzione, il plugin genera anche i **poligoni delle aree di influenza** (buffer pari al raggio di influenza di ogni albero).

## Dataset e metodologia

- **Valore ornamentale ed ecologico** — metodo **Orebla** (autore: *Luigi Sani*), descritto nell'articolo pubblicato su [arborete.it](https://arborete.it/download.html). L'opzione di calcolo ecologico in modalità avanzata è introdotta da ALIAS ATP (contributo del settore branche, ridotto per un *fattore di riduzione*).
- **Raffrescamento estivo e runoff evitato** — modelli di simulazione ambientale elaborati da **ALIAS ATP** ([aliasinfo.it](https://aliasinfo.it)).
- **Libreria specie:** 261 specie arboree (LAI, CRC, IRU base specie/urbano compatto/urbano aperto, gruppo funzionale).
- **Province italiane:** 107 province con fascia fitoclimatica Pavari e valori massimi Orebla (`valmax`) per il valore ornamentale.

Il plugin riproduce i calcoli della **piattaforma ARBOREO di ALIAS ATP**.

## Dati di esempio

Nella cartella `esempio/` è incluso `alberi_esempio.csv` (geometrie WKT, EPSG:4326). In QGIS: **Layer → Aggiungi layer → Testo delimitato**, geometria WKT sul campo `wkt`.

## Struttura del repository

```
QgisTreeBenefits/
├── __init__.py                 # entry point del plugin (classFactory)
├── metadata.txt                # metadati del plugin
├── orebla_plugin.py            # registra il provider + voce di menu
├── provider.py                 # provider Processing (3 algoritmi)
├── create_layer_algorithm.py   # 1 · crea inventario
├── import_algorithm.py         # 2 · importa/adatta layer
├── algorithm.py                # 3 · stima benefici (Processing)
├── dialog.py                   # finestra a schede della stima benefici
├── orebla_core.py              # motore di calcolo (porting del modello)
├── orebla_data.py              # 261 specie + 107 province
├── orebla_fields.py            # definizione campi, vocabolari, campi output
├── orebla_layer.py             # creazione/configurazione layer (tendine + schede)
├── orebla_about.py             # disclaimer, info e guida
├── icon.png
└── esempio/alberi_esempio.csv
```

## Licenza e crediti

- **Sviluppo plugin:** ALIAS ATP — [aliasinfo.it](https://www.aliasinfo.it) · alias@aliasinfo.it
- **Metodo Orebla (valore ornamentale ed ecologico):** Luigi Sani
- **Raffrescamento estivo e runoff evitato:** ALIAS ATP
- **Riferimento:** piattaforma ARBOREO di ALIAS ATP

Strumento a scopo **dimostrativo e didattico**: i risultati non costituiscono perizia o valutazione tecnica ufficiale.

© 2026 ALIAS ATP

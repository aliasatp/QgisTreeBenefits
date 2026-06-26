# QgisTreeBenefits — plugin QGIS

*Autore: **ALIAS ATP** · alias@aliasinfo.it · aliasinfo.it · QGIS ≥ 3.44*


Plugin **Processing** per QGIS che replica i calcoli della webapp Orebla e li
applica in batch a un layer di **punti-albero**, restituendo un nuovo layer con
le stime dei benefici ambientali per ogni albero.

## Cosa calcola (per ogni albero)

- **Valore ecologico**: biomassa / CO₂ stoccata (kg), CO₂ sequestrata (kg/anno),
  O₂ prodotto (kg/anno), inquinanti abbattuti (kg/anno), valore ambientale (€).
- **Valore ornamentale**: curva logistica RAM sul *valmax* provinciale, con
  riduzioni fitosanitarie. Richiede la provincia.
- **Runoff annuo** evitato (m³/anno) + risparmio idrico (€) + classe.
- **Runoff da evento** (es. TR50) evitato (m³) + classe evento.
- **Raffrescamento estivo**: ΔT medio e per le 4 direzioni (N/E/O/S), energia
  risparmiata (kWh), CO₂ evitata (kg), risparmio (€), area e raggio di influenza.
- **(opzionale) CO₂ avanzata**: biomassa branche/rami con riduzione patologica.
- **(opzionale) Simulazioni mobilità**: CO₂ del tragitto casa↔scuola/lavoro e
  numero di alberi equivalenti per compensarla.

La logica, i coefficienti, le tabelle di lookup e i dataset di **261 specie** e
**107 province** sono il porting fedele di `orebla_calc.js` e `orebla_dati.js`.

## Installazione

1. In QGIS (≥ 3.44): *Plugin → Gestisci e installa plugin → Installa da ZIP*,
   selezionare `QgisTreeBenefits.zip`.
2. Tutte le funzioni compaiono nella **Cassetta degli strumenti di Processing**,
   sotto **QgisTreeBenefits → Stima benefici alberi**:

   - **Crea inventario alberi (layer vuoto a schede)**
   - **Importa/adatta layer alberi esistente**

   Il disclaimer e la sezione informativa (metodo Orebla di Luigi Sani;
   raffrescamento/runoff di ALIAS ATP) sono riportati nel pannello *Guida* di
   ciascun algoritmo.

## 1) Crea inventario alberi (layer vuoto)

Crea un layer di punti vuoto con **tutti i campi-parametro**: etichette come nella
webapp, **menu a tendina** per i campi categoriali e **modulo attributi a TAB**
(Dati base / avanzati / climatici). Si sceglie il CRS (default: CRS di progetto).
Dopo l'esecuzione, avviare l'editing e digitalizzare gli alberi compilando i campi
dalle tendine, scheda per scheda.

## 2) Importa/adatta un layer alberi esistente

Trasforma un layer-alberi dell'utente in uno compatibile col calcolatore (stessi
nomi-parametro → pesi corretti):

- si indicano il **campo specie** e i campi **biometrici** (codice, h, DBH,
  circonferenza, diametro e inserzione chioma);
- la **specie** viene abbinata automaticamente alla libreria scegliendo il nome
  più simile; il **log** riporta ogni abbinamento con la percentuale di
  somiglianza (voci sotto il 60% segnalate con "VERIFICARE");
- il layer risultante è già **a TAB con le tendine**, con specie e biometria
  precompilate; gli altri parametri si completano nel modulo a schede e le specie
  dubbie si correggono dal campo specie a tendina.

## 3) Stima benefici ambientali (finestra a schede)

La stima benefici è una finestra a schede (menu Plugin → QgisTreeBenefits → "Stima benefici"), non un algoritmo batch. Schede: Dati base / avanzati / climatici / Opzioni & Output / Info / Guida. Si mappano i campi (auto se i nomi coincidono); i
**dati climatici** possono arrivare dal layer **oppure** essere indicati come
**costante** unica per tutti gli alberi. Opzioni: CO₂ avanzata, mobilità,
generazione delle **aree di influenza** e **CRS di output (UTM)**.

## Output in UTM e aree di influenza

L'output viene riproiettato nel **CRS UTM** scelto (in metri): così il campo
`ob_rinf` (raggio di influenza, m) e `ob_area` (m²) sono direttamente utilizzabili
per generare buffer. Le **aree di influenza** possono essere prodotte
automaticamente (buffer = raggio di influenza) sia dal dialogo a TAB sia
dall'algoritmo Processing.


### Specie e provincia

- **Specie**: il campo può contenere l'**id** numerico Orebla oppure il **nome**
  (anche parziale, es. `Tilia cordata`). Se non riconosciuta si usano i valori di
  default (gruppo `decidua_latifoglia`).
- **Provincia**: **sigla** (`VI`) o **nome** (`Vicenza`). Necessaria per il valore
  ornamentale; senza provincia gli altri benefici si calcolano comunque.
- **Coerenza fitoclimatica**: classe `A`..`E`.

## Nomi-campo convenzionali (default)

Identificazione: `specie`, `provincia`, `fito`
Biometria: `h`, `dbh`, `circonf`, `d_ch`, `inser_c`, `stadio`, `vital`,
`p_soc`, `cond_staz`, `chioma_tr`
Fitosanitario/contesto: `cast_p`, `strumenti`, `dimora`, `organizzazione`,
`fus_p`, `localizzazione`
Clima: `prec_annua`, `n_eventi_pioggia`, `prec_evento`, `rr_evento`,
`tmax_media_estiva`, `vento_medio_estivo`, `umidita_rel_estiva`, `prec_giu_ago`,
`n_eventi_giu_ago`, `rad_globale_giu_ago`, `latitudine`
Opzionali: `km_eco`

## Vocabolari categoriali (case-insensitive)

- **stadio**: plantula · pianta giovane · albero giovane · albero adulto ·
  albero adulto avanzato · albero senescente · albero veterano
- **vital** (1..7): 1 = peggiore … 7 = migliore (7→0% riduzione; 1→albero
  non vitale, niente sequestro)
- **p_soc**: sottoposta · dominata · intermedia · codominante ·
  dominante margine · dominante interna · predominante · libera (giovane) · isolata
- **chioma_tr**: bassa · media · alta · scarsa
- **organizzazione**: aree rurali · aree rurali urbaniz. · periferia recente ·
  periferia antica · luoghi villeggiatura · centro città · centro storico ·
  zone industriali
- **fus_p** (vincolo): nessuno · tutela comunale · rilevanza comunale ·
  paesaggistico · storico-architettonico · monumentale
- **localizzazione**: alberata stradale · parcheggio · piazza · piazzola ·
  plesso scolastico · impianto sportivo · giardino recente · parco recente ·
  giardino storico · parco storico · bosco · cimitero · terreno agricolo
- **dimora**: prato, scarpata, aiuola, tornello, alberata stradale, parcheggio,
  filare arboreo, piazza, parco storico, … (vedi tabella DIMORA_P)
- **cast_p** (1..13): condizioni vegetative · **strumenti** (1..5): integrità
  strutturale · **cond_staz** (1..7): idoneità stazionale

## Campi di output (prefisso `ob_`)

| Campo | Significato |
|---|---|
| ob_spec / ob_prov | specie / provincia riconosciute |
| ob_co2stoc | CO₂ stoccata / biomassa (kg) |
| ob_co2seq | CO₂ sequestrata (kg/anno) |
| ob_o2 | O₂ prodotto (kg/anno) |
| ob_inq | inquinanti abbattuti (kg/anno) |
| ob_valeco | valore ambientale (€) |
| ob_valorn | valore ornamentale netto (€) |
| ob_qorn | Q ornamentale base |
| ob_valgl | valore globale (eco+orn) (€) |
| ob_runmc / ob_runeur / ob_runcls | runoff annuo m³ / € / classe |
| ob_runevmc / ob_runevcl | runoff evento m³ / classe |
| ob_raffdt | raffrescamento ΔT medio (°C) |
| ob_kwh / ob_raffco2 / ob_raffeur | energia/CO₂/€ risparmiati (raffrescamento) |
| ob_area / ob_rinf | area / raggio di influenza |
| ob_dtN ob_dtE ob_dtO ob_dtS | ΔT per direzione (°C) |
| ob_co2avf / ob_valecav / ob_valglav | CO₂ avanzata / valore eco avanzato / globale avanzato |
| ob_mauto ob_mbus ob_mnauto ob_mnbus | mobilità: CO₂ auto/bus e alberi di compensazione |

I campi non calcolabili (input mancanti) restano NULL, come la webapp che non
mostra il risultato quando i dati richiesti non sono presenti.

## Dataset di esempio

`esempio/alberi_esempio.csv` (WKT, EPSG:4326). In QGIS: *Layer → Aggiungi layer
testo delimitato*, geometria WKT, campo `wkt`.

## Note

- Il plugin funziona da Cassetta strumenti, da **Modellatore grafico** e in
  **batch**, come ogni algoritmo Processing.
- L'output può essere GeoPackage, Shapefile, memoria, ecc. Per Shapefile i nomi
  `ob_*` sono già ≤ 10 caratteri.

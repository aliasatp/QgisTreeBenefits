# QgisTreeBenefits — plugin QGIS

*Autore: **ALIAS ATP** · alias@aliasinfo.it · aliasinfo.it · QGIS ≥ 3.22 · versione 0.4*

🇬🇧 *English version: [README_en.md](README_en.md)*

Plugin **Processing** per QGIS che replica i calcoli della webapp Orebla e li
applica in batch a un layer di **punti-albero**, restituendo un nuovo layer con
le stime dei benefici ambientali per ogni albero.

**Novità della versione 0.4**: l'interfaccia è disponibile in **italiano e in
inglese**, ed è stata aggiunta una voce di riferimento generica per l'uso
**fuori dall'Italia**. Il funzionamento in italiano è identico alla v0.3.

## Cosa calcola (per ogni albero)

- **Valore ecologico**: biomassa / CO₂ stoccata (kg), CO₂ sequestrata (kg/anno),
  O₂ prodotto (kg/anno), inquinanti abbattuti (kg/anno), valore ambientale (€).
- **Valore ornamentale**: curva logistica RAM sul *valmax* provinciale, con
  riduzioni fitosanitarie. Richiede la provincia (o la voce generica `ZZ`).
- **Runoff annuo** evitato (m³/anno) + risparmio idrico (€) + classe.
- **Runoff da evento** (es. TR50) evitato (m³) + classe evento.
- **Raffrescamento estivo**: ΔT medio e per le 4 direzioni (N/E/O/S), energia
  risparmiata (kWh), CO₂ evitata (kg), risparmio (€), area e raggio di influenza.
- **(opzionale) CO₂ avanzata**: biomassa branche/rami con riduzione patologica.
- **(opzionale) Simulazioni mobilità**: CO₂ del tragitto casa↔scuola/lavoro e
  numero di alberi equivalenti per compensarla.

La logica, i coefficienti, le tabelle di lookup e i dataset di **261 specie** e
**107 province** sono il porting fedele di `orebla_calc.js` e `orebla_dati.js`.

## Lingua dell'interfaccia

Il plugin parte nella lingua dell'interfaccia di QGIS (italiano se QGIS è in
italiano, altrimenti inglese) e si può cambiare in qualsiasi momento:

- dal **selettore in alto a destra** nella finestra di stima benefici;
- dal menu **Plugin → QgisTreeBenefits → Lingua / Language**;
- per singola esecuzione, dal parametro **Lingua delle etichette** dei due
  algoritmi Processing.

### Cosa cambia e cosa no

| Cambia con la lingua | Resta invariato |
|---|---|
| etichette (alias) dei campi | **nomi** dei campi (`specie`, `dbh`, `ob_valgl`…) |
| voci dei menu a tendina | **valori memorizzati** (`albero adulto`, `codominante`…) |
| titoli delle schede, messaggi, guida | nomi di specie e province (nomi propri) |
| classi testuali di runoff in output | tutti i valori numerici |

Questa è la scelta progettuale centrale: **un inventario creato in inglese si
calcola correttamente anche in italiano e viceversa**, i progetti sono
interscambiabili e i risultati numerici sono identici nelle due lingue.

## Uso fuori dall'Italia

In cima all'elenco delle province c'è la voce generica
**«Media Italia (uso extra-Italia)»** — sigla **`ZZ`**. Il suo `valmax` è la
**media aritmetica** dei valori massimi Orebla delle 107 province italiane
(**112.399,79 €**) e serve a chi lavora fuori dall'Italia e non dispone di un
valore massimo di riferimento locale.

Il campo `provincia` accetta per questa voce anche gli alias `ZZ`, `INT`,
`EXTRA-ITALIA`, `OUTSIDE ITALY`, `Italy average (non-Italian use)`.

Tutti gli altri moduli non contengono parametri specifici dell'Italia:

- la **latitudine** è letta dalla geometria del punto (funziona a ogni latitudine);
- il **CRS di output UTM** viene proposto secondo il fuso reale del layer, nei
  due emisferi (es. EPSG:32721 Buenos Aires, EPSG:32756 Sydney);
- i **dati climatici** vanno inseriti con i valori locali. Nell'**emisfero sud**
  i campi "estivi" (`prec_giu_ago`, `n_eventi_giu_ago`, `rad_globale_giu_ago`,
  `tmax_media_estiva`…) vanno compilati con i dati di **dicembre–febbraio**.

I valori monetari restano espressi in **euro**, perché euro sono i riferimenti e
i costi unitari (energia, acqua) usati nei modelli: si convertono a posteriori.

## Installazione

1. In QGIS: *Plugin → Gestisci e installa plugin → Installa da ZIP*, selezionare
   `QgisTreeBenefits_v04.zip`.
2. Gli strumenti di inventario compaiono nella **Cassetta degli strumenti di
   Processing**, sotto **QgisTreeBenefits → Stima benefici alberi**:
   - **1 · Crea inventario alberi (layer vuoto a schede)**
   - **2 · Importa/adatta layer alberi esistente**
3. La **stima benefici** è nel menu **Plugin → QgisTreeBenefits**.

L'aggiornamento dalla v0.3 non richiede alcuna conversione dei dati.

## 1) Crea inventario alberi (layer vuoto)

Crea un layer di punti vuoto con **tutti i campi-parametro**: etichette nella
lingua scelta, **menu a tendina** per i campi categoriali e **modulo attributi a
TAB** (Dati base / avanzati / climatici). Si sceglie il CRS (default: CRS di
progetto). Dopo l'esecuzione, avviare l'editing e digitalizzare gli alberi.

## 2) Importa/adatta un layer alberi esistente

Trasforma un layer-alberi dell'utente in uno compatibile col calcolatore:

- si indicano il **campo specie** e i campi **biometrici**;
- la **specie** viene abbinata automaticamente alla libreria scegliendo il nome
  più simile; il **log** riporta ogni abbinamento con la percentuale di
  somiglianza (voci sotto il 60% segnalate con "VERIFICARE"/"CHECK");
- il layer risultante è già **a TAB con le tendine**, con specie e biometria
  precompilate.

## 3) Stima benefici ambientali (finestra a schede)

Menu Plugin → QgisTreeBenefits → "Stima benefici". Schede: Dati base / avanzati /
climatici / Opzioni & Output / Info / Guida. Si mappano i campi (auto se i nomi
coincidono); i **dati climatici** possono arrivare dal layer **oppure** essere
indicati come **costante** unica per tutti gli alberi. Opzioni: CO₂ avanzata,
mobilità, generazione delle **aree di influenza** e **CRS di output (UTM)**.

## Output in UTM e aree di influenza

L'output viene riproiettato nel **CRS UTM** scelto (in metri): così il campo
`ob_rinf` (raggio di influenza, m) e `ob_area` (m²) sono direttamente utilizzabili
per generare buffer. Le **aree di influenza** possono essere prodotte
automaticamente (buffer = raggio di influenza).

## Nomi-campo convenzionali (identici in ogni lingua)

Identificazione: `cod_alb`, `specie`, `provincia`, `fito`
Biometria: `h`, `dbh`, `circonf`, `d_ch`, `inser_c`, `stadio`, `vital`,
`p_soc`, `cond_staz`, `chioma_tr`
Fitosanitario/contesto: `cast_p`, `strumenti`, `dimora`, `organizzazione`,
`fus_p`, `localizzazione`
Clima: `prec_annua`, `n_eventi_pioggia`, `prec_evento`, `rr_evento`,
`tmax_media_estiva`, `vento_medio_estivo`, `umidita_rel_estiva`, `prec_giu_ago`,
`n_eventi_giu_ago`, `rad_globale_giu_ago`, `latitudine`
Opzionali: `km_eco`, `riduzione`

## Vocabolari categoriali (valori memorizzati, case-insensitive)

I valori memorizzati **non si traducono**: in inglese l'utente legge
"Mature tree" e nel campo resta scritto `albero adulto`.

- **stadio**: plantula · pianta giovane · albero giovane · albero adulto ·
  albero adulto avanzato · albero senescente · albero veterano
- **vital** (1..7): 1 = peggiore … 7 = migliore
- **p_soc**: sottoposta · dominata · intermedia · codominante ·
  dominante margine · dominante interna · predominante · libera (giovane) · isolata
- **chioma_tr**: bassa · media · alta · scarsa
- **organizzazione**: aree rurali · aree rurali urbaniz. · periferia recente ·
  periferia antica · luoghi villeggiatura · centro città · centro storico ·
  zone industriali
- **fus_p**: nessuno · tutela comunale · rilevanza comunale · paesaggistico ·
  storico-architettonico · monumentale
- **localizzazione**: alberata stradale · parcheggio · piazza · plesso scolastico ·
  impianto sportivo · giardino recente · parco recente · giardino storico ·
  parco storico · bosco · cimitero · terreno agricolo
- **dimora**: prato, scarpata, aiuola, tornello, alberata stradale, parcheggio,
  filare arboreo, piazza, parco storico, … (vedi tabella DIMORA_P)
- **cast_p** (1..13) · **strumenti** (1..5) · **cond_staz** (1..7)

## Campi di output (prefisso `ob_`)

I **nomi** sono gli stessi in ogni lingua; cambia solo l'etichetta mostrata.

| Campo | Significato (IT) | Meaning (EN) |
|---|---|---|
| ob_spec / ob_prov | specie / provincia riconosciute | matched species / reference area |
| ob_co2stoc | CO₂ stoccata / biomassa (kg) | stored CO₂ / biomass (kg) |
| ob_co2seq | CO₂ sequestrata (kg/anno) | CO₂ sequestered (kg/year) |
| ob_o2 | O₂ prodotto (kg/anno) | O₂ produced (kg/year) |
| ob_inq | inquinanti abbattuti (kg/anno) | pollutants removed (kg/year) |
| ob_valeco | valore ambientale (€) | environmental value (EUR) |
| ob_valorn | valore ornamentale netto (€) | net amenity value (EUR) |
| ob_qorn | Q ornamentale base | base amenity index Q |
| ob_valgl | valore globale (eco+orn) (€) | total value (EUR) |
| ob_runmc / ob_runeur / ob_runcls | runoff annuo m³ / € / classe | annual runoff |
| ob_runevmc / ob_runevcl | runoff evento m³ / classe | storm-event runoff |
| ob_raffdt | raffrescamento ΔT medio (°C) | mean cooling ΔT (°C) |
| ob_kwh / ob_raffco2 / ob_raffeur | energia/CO₂/€ risparmiati | energy/CO₂/EUR saved |
| ob_area / ob_rinf | area / raggio di influenza | area / radius of influence |
| ob_dtN ob_dtE ob_dtO ob_dtS | ΔT per direzione (°C) | ΔT per direction (°C) |
| ob_co2avf / ob_valecav / ob_valglav | CO₂ e valori avanzati | advanced CO₂ and values |
| ob_mauto ob_mbus ob_mnauto ob_mnbus | mobilità: CO₂ e alberi di compensazione | mobility |

I campi non calcolabili (input mancanti) restano NULL, come la webapp.

## Dataset di esempio

- `esempio/alberi_esempio.csv` — 3 alberi in provincia di Vicenza (WKT, EPSG:4326).
- `esempio/trees_example_international.csv` — 6 alberi a Lisbona, Lione e Sydney,
  con `provincia = ZZ`, per provare l'uso extra-Italia e l'emisfero sud.

In QGIS: *Layer → Aggiungi layer testo delimitato*, geometria WKT, campo `wkt`.

## Diagnostica

Le operazioni opzionali (API diverse fra Qt5 e Qt6, geometrie non valide,
configurazione del modulo attributi) non interrompono l'elaborazione ma vengono
registrate in *Vista → Pannelli → Log dei messaggi*, scheda **QgisTreeBenefits**.
Se qualcosa non si comporta come previsto, quella scheda dice cosa e` stato saltato.

## Note

- Il plugin funziona da Cassetta strumenti, da **Modellatore grafico** e in
  **batch**, come ogni algoritmo Processing.
- L'output può essere GeoPackage, Shapefile, memoria, ecc. Per Shapefile i nomi
  `ob_*` sono già ≤ 10 caratteri.
- **Disclaimer**: strumento a scopo dimostrativo e didattico. I risultati non
  costituiscono perizia, valutazione tecnica ufficiale o documento con valore
  legale o commerciale. Metodo Orebla: Luigi Sani. Raffrescamento e runoff:
  ALIAS ATP.

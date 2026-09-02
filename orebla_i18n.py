# -*- coding: utf-8 -*-
"""
orebla_i18n.py - Gestione bilingue (IT/EN) del plugin QgisTreeBenefits.
orebla_i18n.py - Bilingual (IT/EN) support for the QgisTreeBenefits plugin.

PRINCIPIO / DESIGN PRINCIPLE
---------------------------
IT: si traducono SOLO le etichette mostrate all'utente (alias dei campi, voci
    dei menu a tendina, testi dell'interfaccia, guida). I NOMI FISICI DEI CAMPI
    e i VALORI MEMORIZZATI restano invariati: cosi' un inventario creato in
    inglese si calcola correttamente anche in italiano e viceversa, e i progetti
    restano interscambiabili.

EN: only the labels shown to the user are translated (field aliases, drop-down
    entries, UI texts, help). PHYSICAL FIELD NAMES and STORED VALUES are left
    unchanged, so an inventory created in English computes correctly in Italian
    and vice versa; projects stay fully interchangeable.

La lingua e' salvata nelle impostazioni QGIS (chiave QgisTreeBenefits/language)
e puo' valere 'auto', 'it' o 'en'.
"""

DEFAULT_LANG = 'it'
LANGS = [('it', 'Italiano'), ('en', 'English')]
LANG_CODES = [c for c, _ in LANGS]

SETTINGS_KEY = 'QgisTreeBenefits/language'

_OVERRIDE = None          # forzatura di sessione (es. parametro Processing)


# ====================================================================
#  STATO DELLA LINGUA / LANGUAGE STATE
# ====================================================================

def _qgis_locale():
    """Codice lingua dell'interfaccia QGIS ('it', 'en', ...)."""
    try:
        from qgis.PyQt.QtCore import QSettings
        s = QSettings()
        loc = s.value('locale/userLocale', '') or ''
        if not loc:
            from qgis.PyQt.QtCore import QLocale
            loc = QLocale.system().name()
        return str(loc)[:2].lower()
    except Exception:
        return ''


def stored_language():
    """Valore grezzo dell'impostazione: 'auto' | 'it' | 'en'."""
    try:
        from qgis.PyQt.QtCore import QSettings
        v = QSettings().value(SETTINGS_KEY, 'auto')
        v = str(v).lower() if v is not None else 'auto'
        return v if v in ('auto',) + tuple(LANG_CODES) else 'auto'
    except Exception:
        return 'auto'


def current_language():
    """Lingua effettiva in uso ('it' o 'en')."""
    if _OVERRIDE in LANG_CODES:
        return _OVERRIDE
    v = stored_language()
    if v in LANG_CODES:
        return v
    return 'it' if _qgis_locale().startswith('it') else 'en'


def set_language(code):
    """Salva la lingua ('auto', 'it', 'en') nelle impostazioni QGIS."""
    code = (code or 'auto').lower()
    if code not in ('auto',) + tuple(LANG_CODES):
        code = 'auto'
    try:
        from qgis.PyQt.QtCore import QSettings
        QSettings().setValue(SETTINGS_KEY, code)
    except Exception:
        pass
    return code


def set_override(code):
    """Forza la lingua per la sessione corrente (None = nessuna forzatura)."""
    global _OVERRIDE
    _OVERRIDE = code if code in LANG_CODES else None


def lang_or_current(lang=None):
    return lang if lang in LANG_CODES else current_language()


# ====================================================================
#  DIZIONARIO STRINGHE INTERFACCIA / UI STRINGS
# ====================================================================

UI = {
    # ---- generale ----
    'plugin.title': {
        'it': 'QgisTreeBenefits \u2013 Stima benefici ambientali',
        'en': 'QgisTreeBenefits \u2013 Tree benefit assessment'},
    'plugin.menu': {'it': '&QgisTreeBenefits', 'en': '&QgisTreeBenefits'},
    'plugin.action.calc': {
        'it': 'Stima benefici (finestra a schede)\u2026',
        'en': 'Benefit assessment (tabbed window)\u2026'},
    'plugin.action.lang': {
        'it': 'Lingua / Language\u2026', 'en': 'Language / Lingua\u2026'},
    'provider.longname': {
        'it': 'QgisTreeBenefits \u2013 Stima benefici ambientali degli alberi',
        'en': 'QgisTreeBenefits \u2013 Environmental benefits of urban trees'},
    'group.name': {'it': 'Stima benefici alberi', 'en': 'Tree benefit assessment'},

    # ---- selettore lingua ----
    'lang.label': {'it': 'Lingua:', 'en': 'Language:'},
    'lang.auto': {
        'it': 'Automatica (come QGIS)', 'en': 'Automatic (follow QGIS)'},
    'lang.dialog.title': {'it': 'Lingua / Language', 'en': 'Language / Lingua'},
    'lang.dialog.text': {
        'it': 'Scegli la lingua dell\u2019interfaccia del plugin.\n'
              'Gli algoritmi nella Cassetta degli strumenti si aggiornano subito; '
              'i layer gi\u00e0 creati mantengono le etichette con cui sono nati.',
        'en': 'Choose the plugin interface language.\n'
              'Processing algorithms refresh immediately; layers already created '
              'keep the labels they were built with.'},

    # ---- schede ----
    'tab.base': {'it': 'Dati base', 'en': 'Basic data'},
    'tab.avanzati': {'it': 'Dati avanzati', 'en': 'Advanced data'},
    'tab.clima': {'it': 'Dati climatici', 'en': 'Climate data'},
    'tab.options': {'it': 'Opzioni & Output', 'en': 'Options & Output'},
    'tab.info': {'it': '\u2139 Info', 'en': '\u2139 Info'},
    'tab.help': {'it': '\u2753 Guida', 'en': '\u2753 Help'},

    # ---- finestra di calcolo ----
    'dlg.layer': {'it': 'Layer di punti-albero:', 'en': 'Tree point layer:'},
    'dlg.col.field': {'it': '<b>Campo</b>', 'en': '<b>Field</b>'},
    'dlg.col.fixed': {'it': '<b>Valore fisso</b>', 'en': '<b>Fixed value</b>'},
    'dlg.fixed': {'it': 'fisso', 'en': 'fixed'},
    'dlg.btn.run': {'it': 'Esegui calcolo', 'en': 'Run calculation'},
    'dlg.btn.close': {'it': 'Chiudi', 'en': 'Close'},
    'dlg.opt.co2av': {
        'it': 'Calcola stima avanzata CO\u2082 (branche/rami)',
        'en': 'Compute advanced CO\u2082 estimate (branches/limbs)'},
    'dlg.opt.rid': {
        'it': 'Fattore di riduzione (predefinito):',
        'en': 'Reduction factor (default):'},
    'dlg.opt.rid.note': {
        'it': 'Il fattore di riduzione pu\u00f2 anche essere prelevato da un campo '
              'del layer (scheda Dati avanzati \u2192 "Fattore di riduzione"); se '
              'mappato, ha la priorit\u00e0 su questo predefinito.',
        'en': 'The reduction factor can also be read from a layer field '
              '(Advanced data tab \u2192 "Decay reduction factor"); when mapped, it '
              'takes priority over this default.'},
    'dlg.opt.mob': {
        'it': 'Calcola simulazioni di mobilit\u00e0 (campo "Km percorsi")',
        'en': 'Compute mobility simulations (field "Daily distance")'},
    'dlg.opt.buffer': {
        'it': 'Genera i poligoni delle aree di influenza (buffer = raggio di influenza)',
        'en': 'Generate areas of influence as polygons (buffer = radius of influence)'},
    'dlg.opt.crs': {'it': 'CRS di output (UTM):', 'en': 'Output CRS (UTM):'},
    'dlg.opt.hint': {
        'it': 'Suggerimento: per tutta una citt\u00e0 i dati climatici sono spesso '
              'uguali; usa i "valori fissi" nella scheda Dati climatici invece di '
              'un campo del layer.',
        'en': 'Tip: across a whole town the climate data are often identical; use '
              'the "fixed values" in the Climate data tab instead of a layer field.'},

    # ---- messaggi ----
    'msg.need.layer': {
        'it': 'Seleziona un layer di punti valido.',
        'en': 'Please select a valid point layer.'},
    'msg.need.point': {
        'it': 'Il layer deve essere di tipo punto.',
        'en': 'The layer must be a point layer.'},
    'msg.done': {
        'it': 'Calcolo completato su %d alberi. Output in %s.',
        'en': 'Calculation completed on %d trees. Output in %s.'},
    'msg.no.species': {
        'it': '%d senza specie riconosciuta (default)',
        'en': '%d with no matched species (defaults used)'},
    'msg.no.prov': {
        'it': '%d senza provincia (no valore ornamentale)',
        'en': '%d with no reference area (no amenity value)'},

    # ---- nomi dei layer prodotti ----
    'layer.out.points': {
        'it': 'Alberi - benefici (Orebla)', 'en': 'Trees - benefits (Orebla)'},
    'layer.out.polygons': {
        'it': 'Aree di influenza (Orebla)', 'en': 'Areas of influence (Orebla)'},
    'layer.inventory': {'it': 'Alberi Orebla', 'en': 'Orebla trees'},

    # ---- gruppi del modulo attributi di output ----
    'grp.params': {'it': 'Parametri albero', 'en': 'Tree parameters'},
    'grp.match': {'it': 'Riconoscimento', 'en': 'Matching'},
    'grp.value': {'it': 'Valore & ecologia', 'en': 'Value & ecology'},
    'grp.runoff': {'it': 'Runoff', 'en': 'Runoff'},
    'grp.cooling': {'it': 'Raffrescamento', 'en': 'Cooling'},
    'grp.advanced': {
        'it': 'CO2 avanzata & mobilita', 'en': 'Advanced CO2 & mobility'},

    # ---- algoritmo 1: crea inventario ----
    'alg1.name': {
        'it': '1 \u00b7 Crea inventario alberi (layer vuoto a schede)',
        'en': '1 \u00b7 Create tree inventory (empty tabbed layer)'},
    'alg1.p.crs': {'it': 'CRS del layer alberi', 'en': 'CRS of the tree layer'},
    'alg1.p.out': {'it': 'Inventario alberi', 'en': 'Tree inventory'},
    'alg1.p.lang': {'it': 'Lingua delle etichette', 'en': 'Label language'},
    'alg1.help': {
        'it': "Crea un layer di punti vuoto con tutti i campi-parametro come "
              "richiesti dal plugin. Il layer risultante ha:\n"
              "\u2022 etichette dei campi gi\u00e0 adeguate per fornirli alla funzione "
              "di stima;\n"
              "\u2022 menu a tendina (ValueMap) per i campi categoriali;\n"
              "\u2022 modulo attributi organizzato in TAB (Dati base / avanzati / "
              "climatici).\n\n"
              "Imposta il CRS desiderato, poi digitalizza gli alberi compilando i "
              "campi dai menu a tendina. Per usare le aree di influenza in seguito "
              "conviene un CRS UTM (in metri).\n\n"
              "Nota: i NOMI dei campi restano invariati in ogni lingua; cambiano solo "
              "le etichette (alias) e le voci delle tendine.\n\n",
        'en': "Creates an empty point layer with all the parameter fields required "
              "by the plugin. The resulting layer has:\n"
              "\u2022 field labels already matching the assessment function;\n"
              "\u2022 drop-down menus (ValueMap) for categorical fields;\n"
              "\u2022 an attribute form organised in TABS (Basic / Advanced / "
              "Climate data).\n\n"
              "Set the desired CRS, then digitise the trees filling in the fields "
              "from the drop-downs. A UTM CRS (in metres) is recommended if you plan "
              "to use the areas of influence.\n\n"
              "Note: field NAMES are identical in every language; only labels "
              "(aliases) and drop-down entries change.\n\n"},
    'alg1.done': {
        'it': 'Inventario vuoto creato. Compila gli alberi dai menu a tendina, '
              'nelle schede del modulo attributi.',
        'en': 'Empty inventory created. Fill in the trees using the drop-down menus '
              'in the tabs of the attribute form.'},
    'alg1.err': {
        'it': 'Impossibile creare il layer di output.',
        'en': 'Unable to create the output layer.'},

    # ---- algoritmo 2: importa ----
    'alg2.name': {
        'it': '2 \u00b7 Importa/adatta layer alberi esistente',
        'en': '2 \u00b7 Import/adapt an existing tree layer'},
    'alg2.p.in': {'it': 'Layer alberi sorgente', 'en': 'Source tree layer'},
    'alg2.p.specie': {'it': 'Campo con la specie', 'en': 'Species field'},
    'alg2.p.cod': {
        'it': 'Campo codice albero (identificativo)',
        'en': 'Tree code field (identifier)'},
    'alg2.p.h': {'it': 'Campo altezza h (m)', 'en': 'Total height field (m)'},
    'alg2.p.dbh': {'it': 'Campo DBH (cm)', 'en': 'DBH field (cm)'},
    'alg2.p.circ': {
        'it': 'Campo circonferenza (cm)', 'en': 'Trunk girth field (cm)'},
    'alg2.p.dch': {
        'it': 'Campo diametro chioma (m)', 'en': 'Crown diameter field (m)'},
    'alg2.p.insc': {
        'it': 'Campo inserzione chioma (m)', 'en': 'Crown base height field (m)'},
    'alg2.p.crs': {'it': 'CRS di output', 'en': 'Output CRS'},
    'alg2.p.out': {
        'it': 'Alberi Orebla (importato)', 'en': 'Orebla trees (imported)'},
    'alg2.help': {
        'it': "Trasforma un layer-alberi dell'utente in un layer compatibile con il "
              "calcolatore (stessi nomi-parametro \u2192 pesi corretti).\n\n"
              "\u2022 La specie viene abbinata automaticamente alla libreria del "
              "plugin scegliendo il nome pi\u00f9 simile (nome scientifico/comune); il "
              "log riporta ogni abbinamento con la percentuale di somiglianza.\n"
              "\u2022 I dati biometrici indicati vengono copiati.\n"
              "\u2022 Gli altri parametri (stadio, vitalit\u00e0, posizione, condizioni, "
              "clima\u2026) si completano nel layer risultante, gi\u00e0 a schede e con i "
              "menu a tendina; le specie dubbie si correggono dal campo a tendina.\n\n",
        'en': "Converts your own tree layer into one compatible with the calculator "
              "(same parameter names \u2192 correct weightings).\n\n"
              "\u2022 Species are matched automatically against the plugin library by "
              "closest name (scientific/common name); the log reports every match "
              "with its similarity score.\n"
              "\u2022 The biometric fields you map are copied across.\n"
              "\u2022 The remaining parameters (growth stage, vitality, position, "
              "condition, climate\u2026) are completed in the resulting layer, already "
              "tabbed and with drop-downs; uncertain species are corrected from the "
              "species drop-down.\n\n"},
    'alg2.err': {
        'it': 'Layer sorgente non valido.', 'en': 'Invalid source layer.'},
    'alg2.log.head': {
        'it': '--- Abbinamento specie (sorgente -> libreria | somiglianza) ---',
        'en': '--- Species matching (source -> library | similarity) ---'},
    'alg2.log.check': {'it': '  <-- VERIFICARE', 'en': '  <-- CHECK'},
    'alg2.log.count': {
        'it': 'Alberi con specie abbinata: %d',
        'en': 'Trees with a matched species: %d'},
    'alg2.done': {
        'it': 'Completa gli altri parametri nelle schede del modulo attributi '
              '(menu a tendina).',
        'en': 'Complete the remaining parameters in the tabs of the attribute form '
              '(drop-down menus).'},

    # ---- classi di runoff (valori di output) ----
    'cls.molto alto': {'it': 'molto alto', 'en': 'very high'},
    'cls.alto': {'it': 'alto', 'en': 'high'},
    'cls.medio': {'it': 'medio', 'en': 'medium'},
    'cls.basso': {'it': 'basso', 'en': 'low'},
    'cls.molto basso': {'it': 'molto basso', 'en': 'very low'},
    'cls.evento severo': {'it': 'evento severo', 'en': 'severe event'},
    'cls.evento medio': {'it': 'evento medio', 'en': 'moderate event'},
    'cls.evento lieve': {'it': 'evento lieve', 'en': 'light event'},
}


def tr(key, lang=None):
    """Traduce una chiave di interfaccia."""
    lang = lang_or_current(lang)
    entry = UI.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key


def tr_class(value, lang=None):
    """Traduce una classe di runoff restituita da orebla_core."""
    if value is None:
        return None
    return tr('cls.' + str(value), lang) if ('cls.' + str(value)) in UI else value


def language_choices(lang=None):
    """Voci per il selettore di lingua: [(etichetta, codice), ...]."""
    return [(tr('lang.auto', lang), 'auto')] + [(nm, c) for c, nm in LANGS]


# ====================================================================
#  ETICHETTE DEI CAMPI DI INPUT / INPUT FIELD LABELS
# ====================================================================

FIELD_LABELS = {
    # ---- base ----
    'cod_alb': {'it': 'Codice albero', 'en': 'Tree code'},
    'specie': {'it': 'Specie', 'en': 'Species'},
    'provincia': {'it': 'Provincia', 'en': 'Province / reference area'},
    'fito': {'it': 'Coerenza fitoclimatica specie/stazione',
             'en': 'Species/site phytoclimatic match'},
    'h': {'it': 'Altezza totale (m)', 'en': 'Total height (m)'},
    'dbh': {'it': 'DBH \u2013 Diametro (cm)', 'en': 'DBH \u2013 stem diameter (cm)'},
    'circonf': {'it': 'Circonferenza (cm)', 'en': 'Stem girth (cm)'},
    'd_ch': {'it': 'Diametro chioma (m)', 'en': 'Crown diameter (m)'},
    'inser_c': {'it': 'Inserzione chioma (m)', 'en': 'Crown base height (m)'},
    'stadio': {'it': 'Stadio', 'en': 'Growth stage'},
    'vital': {'it': 'Vitalit\u00e0 (1\u20137)', 'en': 'Vitality (1\u20137)'},
    'p_soc': {'it': 'Posizione sociale', 'en': 'Social position (crown class)'},
    # ---- avanzati ----
    'cond_staz': {'it': 'Condizioni stazionali (1\u20137)*',
                  'en': 'Site conditions (1\u20137)*'},
    'chioma_tr': {'it': 'Trasparenza chioma**', 'en': 'Crown transparency**'},
    'cast_p': {'it': 'Condizioni vegetative (1\u201313)',
               'en': 'Vegetative condition (1\u201313)'},
    'strumenti': {'it': 'Integrit\u00e0 strutturale (1\u20135)',
                  'en': 'Structural integrity (1\u20135)'},
    'dimora': {'it': 'Tipo di dimora', 'en': 'Planting site type'},
    'organizzazione': {'it': 'Organizzazione urbanistica', 'en': 'Urban context'},
    'fus_p': {'it': 'Vincoli/tutele', 'en': 'Legal protection status'},
    'localizzazione': {'it': 'Localizzazione funzionale*',
                       'en': 'Functional location*'},
    'riduzione': {'it': 'Fattore di riduzione (CO\u2082 avanzata)',
                  'en': 'Decay reduction factor (advanced CO\u2082)'},
    'km_eco': {'it': 'Km percorsi al giorno A/R (casa\u2194scuola/lavoro)',
               'en': 'Daily round-trip distance, km (home\u2194school/work)'},
    # ---- clima ----
    'prec_annua': {'it': 'Precipitazioni annue (mm)*',
                   'en': 'Annual rainfall (mm)*'},
    'n_eventi_pioggia': {'it': 'N\u00b0 eventi pioggia/anno*',
                         'en': 'Rain events per year*'},
    'prec_evento': {'it': 'Precipitazione evento (mm)*',
                    'en': 'Storm event rainfall (mm)*'},
    'rr_evento': {'it': 'Rain rate evento (mm/h)*',
                  'en': 'Event rain rate (mm/h)*'},
    'tmax_media_estiva': {'it': 'Tmax media estiva (\u00b0C)*',
                          'en': 'Mean summer Tmax (\u00b0C)*'},
    'vento_medio_estivo': {'it': 'Vento medio estivo (m/s)*',
                           'en': 'Mean summer wind speed (m/s)*'},
    'umidita_rel_estiva': {'it': 'Umidit\u00e0 relativa media (%)*',
                           'en': 'Mean relative humidity (%)*'},
    'prec_giu_ago': {'it': 'Precipitazioni giu\u2013ago (mm)*',
                     'en': 'Warm-season rainfall, 3 months (mm)*'},
    'n_eventi_giu_ago': {'it': 'N\u00b0 eventi giu\u2013ago*',
                         'en': 'Warm-season rain events, 3 months*'},
    'rad_globale_giu_ago': {'it': 'Radiazione globale giu\u2013ago (MJ/m\u00b2)*',
                            'en': 'Warm-season global radiation, 3 months (MJ/m\u00b2)*'},
}


def field_label(key, lang=None):
    lang = lang_or_current(lang)
    e = FIELD_LABELS.get(key)
    if not e:
        return key
    return e.get(lang) or e.get(DEFAULT_LANG) or key


# ====================================================================
#  ETICHETTE DEI CAMPI DI OUTPUT / OUTPUT FIELD LABELS
# ====================================================================

OUT_LABELS = {
    'ob_spec': {'it': 'specie riconosciuta', 'en': 'matched species'},
    'ob_prov': {'it': 'provincia riconosciuta', 'en': 'matched reference area'},
    'ob_co2stoc': {'it': 'CO2 stoccata / biomassa (kg)',
                   'en': 'Stored CO2 / biomass (kg)'},
    'ob_co2seq': {'it': 'CO2 sequestrata (kg/anno)',
                  'en': 'CO2 sequestered (kg/year)'},
    'ob_o2': {'it': 'O2 prodotto (kg/anno)', 'en': 'O2 produced (kg/year)'},
    'ob_inq': {'it': 'Inquinanti abbattuti (kg/anno)',
               'en': 'Pollutants removed (kg/year)'},
    'ob_valeco': {'it': 'Valore ambientale (EUR)',
                  'en': 'Environmental value (EUR)'},
    'ob_valorn': {'it': 'Valore ornamentale netto (EUR)',
                  'en': 'Net amenity value (EUR)'},
    'ob_qorn': {'it': 'Q ornamentale base', 'en': 'Base amenity index Q'},
    'ob_valgl': {'it': 'Valore globale (eco+orn) (EUR)',
                 'en': 'Total value (eco+amenity) (EUR)'},
    'ob_runmc': {'it': 'Runoff annuo evitato (m3/anno)',
                 'en': 'Annual runoff avoided (m3/year)'},
    'ob_runeur': {'it': 'Risparmio runoff (EUR/anno)',
                  'en': 'Runoff saving (EUR/year)'},
    'ob_runcls': {'it': 'Classe runoff annuo', 'en': 'Annual runoff class'},
    'ob_runevmc': {'it': 'Runoff evento evitato (m3)',
                   'en': 'Storm-event runoff avoided (m3)'},
    'ob_runevcl': {'it': 'Classe evento', 'en': 'Event class'},
    'ob_raffdt': {'it': 'Raffrescamento dT medio (\u00b0C)',
                  'en': 'Mean cooling dT (\u00b0C)'},
    'ob_kwh': {'it': 'Energia risparmiata (kWh)', 'en': 'Energy saved (kWh)'},
    'ob_raffco2': {'it': 'CO2 evitata raffrescamento (kg)',
                   'en': 'CO2 avoided through cooling (kg)'},
    'ob_raffeur': {'it': 'Risparmio energetico (EUR)', 'en': 'Energy saving (EUR)'},
    'ob_area': {'it': 'Area di influenza (m2)', 'en': 'Area of influence (m2)'},
    'ob_rinf': {'it': 'Raggio di influenza (m)', 'en': 'Radius of influence (m)'},
    'ob_dtN': {'it': 'dT Nord (\u00b0C)', 'en': 'dT North (\u00b0C)'},
    'ob_dtE': {'it': 'dT Est (\u00b0C)', 'en': 'dT East (\u00b0C)'},
    'ob_dtO': {'it': 'dT Ovest (\u00b0C)', 'en': 'dT West (\u00b0C)'},
    'ob_dtS': {'it': 'dT Sud (\u00b0C)', 'en': 'dT South (\u00b0C)'},
    'ob_co2avf': {'it': 'CO2 stoccata avanzata (kg)',
                  'en': 'Advanced stored CO2 (kg)'},
    'ob_valecav': {'it': 'Valore eco avanzato (EUR)',
                   'en': 'Advanced ecological value (EUR)'},
    'ob_valglav': {'it': 'Valore globale avanzato (EUR)',
                   'en': 'Advanced total value (EUR)'},
    'ob_mauto': {'it': 'CO2 mobilita auto (kg/anno)',
                 'en': 'Car commute CO2 (kg/year)'},
    'ob_mbus': {'it': 'CO2 mobilita bus (kg/anno)',
                'en': 'School bus CO2 (kg/year)'},
    'ob_mnauto': {'it': 'Alberi compensaz. auto', 'en': 'Trees to offset car'},
    'ob_mnbus': {'it': 'Alberi compensaz. bus', 'en': 'Trees to offset bus'},
}


def out_label(name, lang=None):
    lang = lang_or_current(lang)
    e = OUT_LABELS.get(name)
    if not e:
        return name
    return e.get(lang) or e.get(DEFAULT_LANG) or name


# ====================================================================
#  VOCI DEI MENU A TENDINA / DROP-DOWN ENTRIES
#  formato: (valore_memorizzato, {'it': etichetta, 'en': label})
#  ATTENZIONE: il valore memorizzato NON va mai tradotto.
# ====================================================================

OPTIONS = {

    'vital': [
        ('7', {'it': '7 \u2013 Ottimali', 'en': '7 \u2013 Optimal'}),
        ('6', {'it': '6 \u2013 Buone', 'en': '6 \u2013 Good'}),
        ('5', {'it': '5 \u2013 Medie', 'en': '5 \u2013 Average'}),
        ('4', {'it': '4 \u2013 Mediocri', 'en': '4 \u2013 Fair'}),
        ('3', {'it': '3 \u2013 Scadenti', 'en': '3 \u2013 Poor'}),
        ('2', {'it': '2 \u2013 Pessime', 'en': '2 \u2013 Very poor'}),
        ('1', {'it': '1 \u2013 Morto/irrecuperabile',
               'en': '1 \u2013 Dead/unrecoverable'}),
    ],

    'cond_staz': [
        ('7', {'it': '7 \u2013 Ottimali', 'en': '7 \u2013 Optimal'}),
        ('6', {'it': '6 \u2013 Buone', 'en': '6 \u2013 Good'}),
        ('5', {'it': '5 \u2013 Nella media', 'en': '5 \u2013 Average'}),
        ('4', {'it': '4 \u2013 Mediocri', 'en': '4 \u2013 Fair'}),
        ('3', {'it': '3 \u2013 Scadenti', 'en': '3 \u2013 Poor'}),
        ('2', {'it': '2 \u2013 Pessime', 'en': '2 \u2013 Very poor'}),
        ('1', {'it': '1 \u2013 Inadatte', 'en': '1 \u2013 Unsuitable'}),
    ],

    'cast_p': [
        ('13', {'it': '13 \u2013 Ottimali', 'en': '13 \u2013 Optimal'}),
        ('12', {'it': '12 \u2013 Buone', 'en': '12 \u2013 Good'}),
        ('11', {'it': '11 \u2013 Mediocri (conflitti manufatti)',
                'en': '11 \u2013 Fair (conflicts with structures)'}),
        ('10', {'it': '10 \u2013 Mediocri (conflitti radicali)',
                'en': '10 \u2013 Fair (root conflicts)'}),
        ('9', {'it': '9 \u2013 Mediocri (conflitti chioma)',
               'en': '9 \u2013 Fair (crown conflicts)'}),
        ('8', {'it': '8 \u2013 Scadenti (conflitti manufatti)',
               'en': '8 \u2013 Poor (conflicts with structures)'}),
        ('7', {'it': '7 \u2013 Scadenti (conflitti radicali)',
               'en': '7 \u2013 Poor (root conflicts)'}),
        ('6', {'it': '6 \u2013 Scadenti (conflitti chioma)',
               'en': '6 \u2013 Poor (crown conflicts)'}),
        ('5', {'it': '5 \u2013 Scadenti (limitazioni)',
               'en': '5 \u2013 Poor (site limitations)'}),
        ('4', {'it': '4 \u2013 Pessime (conflitti manufatti)',
               'en': '4 \u2013 Very poor (conflicts with structures)'}),
        ('3', {'it': '3 \u2013 Pessime (conflitti radicali)',
               'en': '3 \u2013 Very poor (root conflicts)'}),
        ('2', {'it': '2 \u2013 Pessime (conflitti chioma)',
               'en': '2 \u2013 Very poor (crown conflicts)'}),
        ('1', {'it': '1 \u2013 Pessime (limitazioni intollerabili)',
               'en': '1 \u2013 Very poor (intolerable limitations)'}),
    ],

    'strumenti': [
        ('5', {'it': '5 \u2013 Albero integro', 'en': '5 \u2013 Intact tree'}),
        ('4', {'it': '4 \u2013 Lievemente alterato',
               'en': '4 \u2013 Slightly altered'}),
        ('3', {'it': '3 \u2013 Strutturalmente alterato',
               'en': '3 \u2013 Structurally altered'}),
        ('2', {'it': '2 \u2013 Fortemente alterato',
               'en': '2 \u2013 Strongly altered'}),
        ('1', {'it': '1 \u2013 Molto alterato', 'en': '1 \u2013 Severely altered'}),
    ],

    'fito': [
        ('A', {'it': 'A \u2013 Fascia idonea', 'en': 'A \u2013 Suitable belt'}),
        ('B', {'it': 'B \u2013 Fascia sub-idonea',
               'en': 'B \u2013 Sub-suitable belt'}),
        ('C', {'it': 'C \u2013 Fascia con modesta idoneit\u00e0',
               'en': 'C \u2013 Moderately suitable belt'}),
        ('D', {'it': 'D \u2013 Fascia non idonea',
               'en': 'D \u2013 Unsuitable belt'}),
        ('E', {'it': 'E \u2013 Fascia ampiamente non idonea',
               'en': 'E \u2013 Highly unsuitable belt'}),
    ],

    'stadio': [
        ('plantula', {'it': 'Plantula', 'en': 'Seedling'}),
        ('pianta giovane', {'it': 'Pianta giovane', 'en': 'Young plant'}),
        ('albero giovane', {'it': 'Albero giovane', 'en': 'Young tree'}),
        ('albero adulto', {'it': 'Albero adulto', 'en': 'Mature tree'}),
        ('albero adulto avanzato', {'it': 'Albero adulto avanzato',
                                    'en': 'Late-mature tree'}),
        ('albero senescente', {'it': 'Albero senescente', 'en': 'Senescent tree'}),
        ('albero veterano', {'it': 'Albero veterano', 'en': 'Veteran tree'}),
    ],

    'p_soc': [
        ('predominante', {'it': 'Predominante', 'en': 'Predominant'}),
        ('dominante interna', {'it': 'Dominante interna',
                               'en': 'Dominant (interior)'}),
        ('dominante margine', {'it': 'Dominante margine',
                               'en': 'Dominant (edge)'}),
        ('codominante', {'it': 'Codominante', 'en': 'Codominant'}),
        ('intermedia', {'it': 'Intermedia', 'en': 'Intermediate'}),
        ('dominata', {'it': 'Dominata', 'en': 'Overtopped'}),
        ('sottoposta', {'it': 'Sottoposta', 'en': 'Suppressed'}),
        ('libera (giovane)', {'it': 'Libera (giovane)',
                              'en': 'Free-growing (young)'}),
        ('isolata', {'it': 'Isolata', 'en': 'Isolated'}),
    ],

    'chioma_tr': [
        ('scarsa', {'it': 'Scarsa', 'en': 'Very sparse'}),
        ('bassa', {'it': 'Bassa', 'en': 'Low'}),
        ('media', {'it': 'Media', 'en': 'Medium'}),
        ('alta', {'it': 'Alta', 'en': 'High'}),
    ],

    'dimora': [
        ('parco storico', {'it': 'Parco storico', 'en': 'Historic park'}),
        ('parco recente', {'it': 'Parco recente', 'en': 'Modern park'}),
        ('giardino storico', {'it': 'Giardino storico', 'en': 'Historic garden'}),
        ('giardino recente', {'it': 'Giardino recente', 'en': 'Modern garden'}),
        ('alberata stradale', {'it': 'Alberata stradale', 'en': 'Street tree avenue'}),
        ('parcheggio', {'it': 'Parcheggio', 'en': 'Car park'}),
        ('piazza', {'it': 'Piazza', 'en': 'Town square'}),
        ('bosco', {'it': 'Bosco', 'en': 'Woodland'}),
        ('buco asfalto', {'it': 'Buco asfalto', 'en': 'Cut-out in asphalt'}),
        ('aiuola', {'it': 'Aiuola', 'en': 'Planting bed'}),
        ('aiuola spartitraffico', {'it': 'Aiuola spartitraffico',
                                   'en': 'Central reservation bed'}),
        ('cimitero', {'it': 'Cimitero', 'en': 'Cemetery'}),
        ('prato', {'it': 'Prato', 'en': 'Lawn / grassland'}),
        ('filare arboreo', {'it': 'Filare arboreo', 'en': 'Tree row'}),
        ('rimboschimento', {'it': 'Rimboschimento', 'en': 'Reforestation'}),
        ('gruppo/boschetto', {'it': 'Gruppo/boschetto', 'en': 'Group / copse'}),
        ('tornello', {'it': 'Tornello', 'en': 'Tree pit'}),
        ('banchina stradale', {'it': 'Banchina stradale', 'en': 'Road verge'}),
        ('scarpata', {'it': 'Scarpata', 'en': 'Embankment slope'}),
        ('terrapieno', {'it': 'Terrapieno', 'en': 'Earth bank'}),
        ('terreno coltivato', {'it': 'Terreno coltivato', 'en': 'Cultivated land'}),
        ('terreno incolto', {'it': 'Terreno incolto', 'en': 'Uncultivated land'}),
        ('area di pertinenza', {'it': 'Area di pertinenza', 'en': 'Ancillary area'}),
        ('marker', {'it': 'Marker', 'en': 'Landmark tree'}),
    ],

    'organizzazione': [
        ('centro storico', {'it': 'Centro storico', 'en': 'Historic centre'}),
        ('centro citt\u00e0', {'it': 'Centro citt\u00e0', 'en': 'City centre'}),
        ('periferia antica', {'it': 'Periferia antica', 'en': 'Older suburbs'}),
        ('periferia recente', {'it': 'Periferia recente', 'en': 'Recent suburbs'}),
        ('luoghi villeggiatura', {'it': 'Luoghi di villeggiatura',
                                  'en': 'Resort / holiday areas'}),
        ('zone industriali', {'it': 'Zone industriali', 'en': 'Industrial areas'}),
        ('aree rurali urbaniz.', {'it': 'Aree rurali urbanizzate',
                                  'en': 'Urbanised rural areas'}),
        ('aree rurali', {'it': 'Aree rurali', 'en': 'Rural areas'}),
    ],

    'fus_p': [
        ('nessuno', {'it': 'Nessuno', 'en': 'None'}),
        ('tutela comunale', {'it': 'Tutela comunale',
                             'en': 'Municipal protection'}),
        ('rilevanza comunale', {'it': 'Rilevanza comunale',
                                'en': 'Municipal significance'}),
        ('paesaggistico', {'it': 'Paesaggistico', 'en': 'Landscape designation'}),
        ('storico-architettonico', {'it': 'Storico-architettonico',
                                    'en': 'Historic-architectural'}),
        ('monumentale', {'it': 'Monumentale', 'en': 'Monumental tree'}),
    ],

    'localizzazione': [
        ('parco storico', {'it': 'Parco storico', 'en': 'Historic park'}),
        ('parco recente', {'it': 'Parco recente', 'en': 'Modern park'}),
        ('giardino storico', {'it': 'Giardino storico', 'en': 'Historic garden'}),
        ('giardino recente', {'it': 'Giardino recente', 'en': 'Modern garden'}),
        ('alberata stradale', {'it': 'Alberata stradale',
                               'en': 'Street tree avenue'}),
        ('parcheggio', {'it': 'Parcheggio', 'en': 'Car park'}),
        ('piazza', {'it': 'Piazza', 'en': 'Town square'}),
        ('bosco', {'it': 'Bosco', 'en': 'Woodland'}),
        ('plesso scolastico', {'it': 'Plesso scolastico', 'en': 'School grounds'}),
        ('impianto sportivo', {'it': 'Impianto sportivo', 'en': 'Sports facility'}),
        ('cimitero', {'it': 'Cimitero', 'en': 'Cemetery'}),
        ('terreno agricolo', {'it': 'Terreno agricolo', 'en': 'Farmland'}),
    ],

    'riduzione': [
        ('0', {'it': 'Nessuna riduzione', 'en': 'No reduction'}),
        ('0.2', {'it': 'Cavita basale localizzata (-20%)',
                 'en': 'Localised basal cavity (-20%)'}),
        ('0.4', {'it': 'Carie estesa al tronco (-40%)',
                 'en': 'Extensive stem decay (-40%)'}),
        ('0.5', {'it': 'Carie tronco e branche grave (-50%)',
                 'en': 'Severe stem and branch decay (-50%)'}),
        ('0.6', {'it': 'Cilindro centrale cariato (-60%)',
                 'en': 'Decayed central cylinder (-60%)'}),
    ],

    'patologia': [
        ('0', {'it': 'Nessuna patologia', 'en': 'No decay'}),
        ('0.2', {'it': 'Cavita basale localizzata (-20%)',
                 'en': 'Localised basal cavity (-20%)'}),
        ('0.4', {'it': 'Carie estesa al tronco (-40%)',
                 'en': 'Extensive stem decay (-40%)'}),
        ('0.5', {'it': 'Carie tronco e branche grave (-50%)',
                 'en': 'Severe stem and branch decay (-50%)'}),
        ('0.6', {'it': 'Cilindro centrale cariato (-60%)',
                 'en': 'Decayed central cylinder (-60%)'}),
    ],
}


def options(name, lang=None):
    """Restituisce [(etichetta_tradotta, valore_memorizzato), ...]."""
    lang = lang_or_current(lang)
    out = []
    for value, labels in OPTIONS.get(name, []):
        out.append((labels.get(lang) or labels.get(DEFAULT_LANG) or value, value))
    return out


def option_labels(name, lang=None):
    """Solo le etichette, nell'ordine di definizione."""
    return [lbl for lbl, _v in options(name, lang)]


def option_values(name):
    """Solo i valori memorizzati, nell'ordine di definizione."""
    return [v for v, _l in OPTIONS.get(name, [])]

# -*- coding: utf-8 -*-
"""
orebla_fields.py - Definizioni condivise tra gli algoritmi Processing
di calcolo (a TAB) e la creazione del layer vuoto.

Contiene:
  - INPUT_FIELDS : specifica di tutti i campi-parametro (nome, tipo, etichetta,
                   tab di appartenenza, tipo di widget)
  - OPTIONS      : vocabolari per i menu a tendina (come nella webapp)
  - OUT_FIELDS   : campi di output (prefisso ob_)
  - helper per ValueMap e per il calcolo della zona UTM
"""

from qgis.PyQt.QtCore import QVariant

from .orebla_data import SPECIE_DATA, PROVINCE_DATA


# --------------------------------------------------------------------
#  VOCABOLARI (menu a tendina)
#  ogni voce: (descrizione_mostrata, valore_memorizzato)
# --------------------------------------------------------------------

def _kv(keys):
    return [(k, k) for k in keys]


# Etichette tendine ESATTE dalla webapp Orebla (orebla.html), stesso ordine.
# Ogni voce: (testo_mostrato, valore_memorizzato)

VITAL_OPTS = [('7 \u2013 Ottimali', '7'), ('6 \u2013 Buone', '6'),
              ('5 \u2013 Medie', '5'), ('4 \u2013 Mediocri', '4'),
              ('3 \u2013 Scadenti', '3'), ('2 \u2013 Pessime', '2'),
              ('1 \u2013 Morto/irrecuperabile', '1')]

CONDSTAZ_OPTS = [('7 \u2013 Ottimali', '7'), ('6 \u2013 Buone', '6'),
                 ('5 \u2013 Nella media', '5'), ('4 \u2013 Mediocri', '4'),
                 ('3 \u2013 Scadenti', '3'), ('2 \u2013 Pessime', '2'),
                 ('1 \u2013 Inadatte', '1')]

CASTP_OPTS = [('13 \u2013 Ottimali', '13'), ('12 \u2013 Buone', '12'),
              ('11 \u2013 Mediocri (conflitti manufatti)', '11'),
              ('10 \u2013 Mediocri (conflitti radicali)', '10'),
              ('9 \u2013 Mediocri (conflitti chioma)', '9'),
              ('8 \u2013 Scadenti (conflitti manufatti)', '8'),
              ('7 \u2013 Scadenti (conflitti radicali)', '7'),
              ('6 \u2013 Scadenti (conflitti chioma)', '6'),
              ('5 \u2013 Scadenti (limitazioni)', '5'),
              ('4 \u2013 Pessime (conflitti manufatti)', '4'),
              ('3 \u2013 Pessime (conflitti radicali)', '3'),
              ('2 \u2013 Pessime (conflitti chioma)', '2'),
              ('1 \u2013 Pessime (limitazioni intollerabili)', '1')]

STRUM_OPTS = [('5 \u2013 Albero integro', '5'),
              ('4 \u2013 Lievemente alterato', '4'),
              ('3 \u2013 Strutturalmente alterato', '3'),
              ('2 \u2013 Fortemente alterato', '2'),
              ('1 \u2013 Molto alterato', '1')]

FITO_OPTS = [('A \u2013 Fascia idonea', 'A'),
             ('B \u2013 Fascia sub-idonea', 'B'),
             ('C \u2013 Fascia con modesta idoneit\u00e0', 'C'),
             ('D \u2013 Fascia non idonea', 'D'),
             ('E \u2013 Fascia ampiamente non idonea', 'E')]

STADIO_OPTS = [('Plantula', 'plantula'), ('Pianta giovane', 'pianta giovane'),
               ('Albero giovane', 'albero giovane'), ('Albero adulto', 'albero adulto'),
               ('Albero adulto avanzato', 'albero adulto avanzato'),
               ('Albero senescente', 'albero senescente'),
               ('Albero veterano', 'albero veterano')]

PSOC_OPTS = [('Predominante', 'predominante'), ('Dominante interna', 'dominante interna'),
             ('Dominante margine', 'dominante margine'), ('Codominante', 'codominante'),
             ('Intermedia', 'intermedia'), ('Dominata', 'dominata'),
             ('Sottoposta', 'sottoposta'), ('Libera (giovane)', 'libera (giovane)'),
             ('Isolata', 'isolata')]

CHIOMATR_OPTS = [('Scarsa', 'scarsa'), ('Bassa', 'bassa'),
                 ('Media', 'media'), ('Alta', 'alta')]

DIMORA_OPTS = [('Parco storico', 'parco storico'), ('Parco recente', 'parco recente'),
               ('Giardino storico', 'giardino storico'), ('Giardino recente', 'giardino recente'),
               ('Alberata stradale', 'alberata stradale'), ('Parcheggio', 'parcheggio'),
               ('Piazza', 'piazza'), ('Bosco', 'bosco'), ('Buco asfalto', 'buco asfalto'),
               ('Aiuola', 'aiuola'), ('Aiuola spartitraffico', 'aiuola spartitraffico'),
               ('Cimitero', 'cimitero'), ('Prato', 'prato'), ('Filare arboreo', 'filare arboreo'),
               ('Rimboschimento', 'rimboschimento'), ('Gruppo/boschetto', 'gruppo/boschetto'),
               ('Tornello', 'tornello'), ('Banchina stradale', 'banchina stradale'),
               ('Scarpata', 'scarpata'), ('Terrapieno', 'terrapieno'),
               ('Terreno coltivato', 'terreno coltivato'), ('Terreno incolto', 'terreno incolto'),
               ('Area di pertinenza', 'area di pertinenza'), ('Marker', 'marker')]

ORG_OPTS = [('Centro storico', 'centro storico'), ('Centro citt\u00e0', 'centro città'),
            ('Periferia antica', 'periferia antica'), ('Periferia recente', 'periferia recente'),
            ('Luoghi di villeggiatura', 'luoghi villeggiatura'),
            ('Zone industriali', 'zone industriali'),
            ('Aree rurali urbanizzate', 'aree rurali urbaniz.'),
            ('Aree rurali', 'aree rurali')]

FUSP_OPTS = [('Nessuno', 'nessuno'), ('Tutela comunale', 'tutela comunale'),
             ('Rilevanza comunale', 'rilevanza comunale'), ('Paesaggistico', 'paesaggistico'),
             ('Storico-architettonico', 'storico-architettonico'),
             ('Monumentale', 'monumentale')]

LOCALIZ_OPTS = [('Parco storico', 'parco storico'), ('Parco recente', 'parco recente'),
                ('Giardino storico', 'giardino storico'), ('Giardino recente', 'giardino recente'),
                ('Alberata stradale', 'alberata stradale'), ('Parcheggio', 'parcheggio'),
                ('Piazza', 'piazza'), ('Bosco', 'bosco'), ('Plesso scolastico', 'plesso scolastico'),
                ('Impianto sportivo', 'impianto sportivo'), ('Cimitero', 'cimitero'),
                ('Terreno agricolo', 'terreno agricolo')]

# Specie: descrizione = nome, valore = nome (find_specie accetta anche il nome)
SPECIE_OPTS = sorted([(s['nome'], s['nome']) for s in SPECIE_DATA],
                     key=lambda t: t[0].lower())

# Provincia: descrizione = "Nome (SIG)", valore = sigla
PROV_OPTS = sorted([('%s (%s)' % (p['prov'], p['sigla']), p['sigla'])
                    for p in PROVINCE_DATA], key=lambda t: t[0].lower())

# Fattore di riduzione (per la stima avanzata della CO2 stoccata)
RIDUZIONE_OPTS = [('Nessuna riduzione', '0'),
                  ('Cavita basale localizzata (-20%)', '0.2'),
                  ('Carie estesa al tronco (-40%)', '0.4'),
                  ('Carie tronco e branche grave (-50%)', '0.5'),
                  ('Cilindro centrale cariato (-60%)', '0.6')]


# --------------------------------------------------------------------
#  SPECIFICA CAMPI DI INPUT
#  key, qtype, label, tab ('base'|'avanzati'|'clima'), widget, options
#  widget: 'map' (tendina), 'text', 'num'
# --------------------------------------------------------------------

INPUT_FIELDS = [
    # ---- BASE ----
    dict(key='cod_alb', qtype=QVariant.String, label='Codice albero',
         tab='base', widget='text', options=None),
    dict(key='specie', qtype=QVariant.String, label='Specie',
         tab='base', widget='map', options=SPECIE_OPTS),
    dict(key='provincia', qtype=QVariant.String, label='Provincia',
         tab='base', widget='map', options=PROV_OPTS),
    dict(key='fito', qtype=QVariant.String, label='Coerenza fitoclimatica specie/stazione',
         tab='base', widget='map', options=FITO_OPTS),
    dict(key='h', qtype=QVariant.Double, label='Altezza totale (m)',
         tab='base', widget='num', options=None),
    dict(key='dbh', qtype=QVariant.Double, label='DBH \u2013 Diametro (cm)',
         tab='base', widget='num', options=None),
    dict(key='circonf', qtype=QVariant.Double, label='Circonferenza (cm)',
         tab='base', widget='num', options=None),
    dict(key='d_ch', qtype=QVariant.Double, label='Diametro chioma (m)',
         tab='base', widget='num', options=None),
    dict(key='inser_c', qtype=QVariant.Double, label='Inserzione chioma (m)',
         tab='base', widget='num', options=None),
    dict(key='stadio', qtype=QVariant.String, label='Stadio fenologico',
         tab='base', widget='map', options=STADIO_OPTS),
    dict(key='vital', qtype=QVariant.Int, label='Vitalit\u00e0 (1\u20137)',
         tab='base', widget='map', options=VITAL_OPTS),
    dict(key='p_soc', qtype=QVariant.String, label='Posizione sociale',
         tab='base', widget='map', options=PSOC_OPTS),

    # ---- AVANZATI ----
    dict(key='cond_staz', qtype=QVariant.Int, label='Condizioni stazionali (1\u20137)*',
         tab='avanzati', widget='map', options=CONDSTAZ_OPTS),
    dict(key='chioma_tr', qtype=QVariant.String, label='Trasparenza chioma**',
         tab='avanzati', widget='map', options=CHIOMATR_OPTS),
    dict(key='cast_p', qtype=QVariant.Int, label='Condizioni vegetative (1\u201313)',
         tab='avanzati', widget='map', options=CASTP_OPTS),
    dict(key='strumenti', qtype=QVariant.Int, label='Integrit\u00e0 strutturale (1\u20135)',
         tab='avanzati', widget='map', options=STRUM_OPTS),
    dict(key='dimora', qtype=QVariant.String, label='Tipo di dimora',
         tab='avanzati', widget='map', options=DIMORA_OPTS),
    dict(key='organizzazione', qtype=QVariant.String, label='Organizzazione urbanistica',
         tab='avanzati', widget='map', options=ORG_OPTS),
    dict(key='fus_p', qtype=QVariant.String, label='Vincoli/tutele',
         tab='avanzati', widget='map', options=FUSP_OPTS),
    dict(key='localizzazione', qtype=QVariant.String, label='Localizzazione funzionale*',
         tab='avanzati', widget='map', options=LOCALIZ_OPTS),
    dict(key='riduzione', qtype=QVariant.Double, label='Fattore di riduzione (CO\u2082 avanzata)',
         tab='avanzati', widget='map', options=RIDUZIONE_OPTS),
    dict(key='km_eco', qtype=QVariant.Double, label='Km percorsi al giorno A/R (casa\u2194scuola/lavoro)',
         tab='avanzati', widget='num', options=None),

    # ---- CLIMA ----
    dict(key='prec_annua', qtype=QVariant.Double, label='Precipitazioni annue (mm)*',
         tab='clima', widget='num', options=None),
    dict(key='n_eventi_pioggia', qtype=QVariant.Double, label='N\u00b0 eventi pioggia/anno*',
         tab='clima', widget='num', options=None),
    dict(key='prec_evento', qtype=QVariant.Double, label='Precipitazione evento (mm)*',
         tab='clima', widget='num', options=None),
    dict(key='rr_evento', qtype=QVariant.Double, label='Rain rate evento (mm/h)*',
         tab='clima', widget='num', options=None),
    dict(key='tmax_media_estiva', qtype=QVariant.Double, label='Tmax media estiva (\u00b0C)*',
         tab='clima', widget='num', options=None),
    dict(key='vento_medio_estivo', qtype=QVariant.Double, label='Vento medio estivo (m/s)*',
         tab='clima', widget='num', options=None),
    dict(key='umidita_rel_estiva', qtype=QVariant.Double, label='Umidit\u00e0 relativa media (%)*',
         tab='clima', widget='num', options=None),
    dict(key='prec_giu_ago', qtype=QVariant.Double, label='Precipitazioni giu\u2013ago (mm)*',
         tab='clima', widget='num', options=None),
    dict(key='n_eventi_giu_ago', qtype=QVariant.Double, label='N\u00b0 eventi giu\u2013ago*',
         tab='clima', widget='num', options=None),
    dict(key='rad_globale_giu_ago', qtype=QVariant.Double, label='Radiazione globale giu\u2013ago (MJ/m\u00b2)*',
         tab='clima', widget='num', options=None),
]

INPUT_FIELDS_BY_KEY = {f['key']: f for f in INPUT_FIELDS}


# --------------------------------------------------------------------
#  CAMPI DI OUTPUT (prefisso ob_)
# --------------------------------------------------------------------

OUT_FIELDS = [
    ('ob_spec',    QVariant.String, 'specie riconosciuta'),
    ('ob_prov',    QVariant.String, 'provincia riconosciuta'),
    ('ob_co2stoc', QVariant.Double, 'CO2 stoccata / biomassa (kg)'),
    ('ob_co2seq',  QVariant.Double, 'CO2 sequestrata (kg/anno)'),
    ('ob_o2',      QVariant.Double, 'O2 prodotto (kg/anno)'),
    ('ob_inq',     QVariant.Double, 'Inquinanti abbattuti (kg/anno)'),
    ('ob_valeco',  QVariant.Double, 'Valore ambientale (EUR)'),
    ('ob_valorn',  QVariant.Double, 'Valore ornamentale netto (EUR)'),
    ('ob_qorn',    QVariant.Double, 'Q ornamentale base'),
    ('ob_valgl',   QVariant.Double, 'Valore globale (eco+orn) (EUR)'),
    ('ob_runmc',   QVariant.Double, 'Runoff annuo evitato (m3/anno)'),
    ('ob_runeur',  QVariant.Double, 'Risparmio runoff (EUR/anno)'),
    ('ob_runcls',  QVariant.String, 'Classe runoff annuo'),
    ('ob_runevmc', QVariant.Double, 'Runoff evento evitato (m3)'),
    ('ob_runevcl', QVariant.String, 'Classe evento'),
    ('ob_raffdt',  QVariant.Double, 'Raffrescamento dT medio (°C)'),
    ('ob_kwh',     QVariant.Double, 'Energia risparmiata (kWh)'),
    ('ob_raffco2', QVariant.Double, 'CO2 evitata raffrescamento (kg)'),
    ('ob_raffeur', QVariant.Double, 'Risparmio energetico (EUR)'),
    ('ob_area',    QVariant.Double, 'Area di influenza (m2)'),
    ('ob_rinf',    QVariant.Double, 'Raggio di influenza (m)'),
    ('ob_dtN',     QVariant.Double, 'dT Nord (°C)'),
    ('ob_dtE',     QVariant.Double, 'dT Est (°C)'),
    ('ob_dtO',     QVariant.Double, 'dT Ovest (°C)'),
    ('ob_dtS',     QVariant.Double, 'dT Sud (°C)'),
    ('ob_co2avf',  QVariant.Double, 'CO2 stoccata avanzata (kg)'),
    ('ob_valecav', QVariant.Double, 'Valore eco avanzato (EUR)'),
    ('ob_valglav', QVariant.Double, 'Valore globale avanzato (EUR)'),
    ('ob_mauto',   QVariant.Double, 'CO2 mobilita auto (kg/anno)'),
    ('ob_mbus',    QVariant.Double, 'CO2 mobilita bus (kg/anno)'),
    ('ob_mnauto',  QVariant.Double, 'Alberi compensaz. auto'),
    ('ob_mnbus',   QVariant.Double, 'Alberi compensaz. bus'),
]

PATOLOGIA_VALS = [0.0, 0.20, 0.40, 0.50, 0.60]
PATOLOGIA_LBL = ['Nessuna patologia', 'Cavita basale localizzata (-20%)',
                 'Carie estesa al tronco (-40%)',
                 'Carie tronco e branche grave (-50%)',
                 'Cilindro centrale cariato (-60%)']


# --------------------------------------------------------------------
#  HELPER ValueMap (menu a tendina nel modulo attributi)
# --------------------------------------------------------------------

def value_map_config(options):
    """Restituisce la config per QgsEditorWidgetSetup('ValueMap', cfg),
    preservando l'ordine con una lista di dict {descrizione: valore}."""
    return {'map': [{desc: val} for desc, val in options]}


# --------------------------------------------------------------------
#  HELPER UTM
# --------------------------------------------------------------------

def utm_epsg_from_lonlat(lon, lat):
    """EPSG del fuso UTM/WGS84 per la coppia lon/lat data."""
    try:
        zone = int((float(lon) + 180.0) / 6.0) + 1
        zone = max(1, min(60, zone))
    except (TypeError, ValueError):
        zone = 32  # fallback Italia centro-nord
    if lat is None:
        lat = 45.0
    base = 32600 if float(lat) >= 0 else 32700
    return 'EPSG:%d' % (base + zone)


def build_out_attr_dict(feat_attrs, res, sp, pr):
    """Compone il dizionario nome->valore dei campi ob_ a partire dai risultati
    di orebla_core.compute_all(). Condiviso tra gli algoritmi."""
    eco = res['eco']
    orn = res['orn']
    run = res['run']
    run_ev = res['run_ev']
    raff = res['raff']
    co2av = res['co2av']
    mob = res['mob']

    def g(d, k):
        return d[k] if (d is not None and k in d and d[k] is not None) else None

    dt = {}
    if raff:
        for dn in ('nord', 'est', 'ovest', 'sud'):
            dt[dn] = raff['dir'][dn]['dt']

    return {
        'ob_spec':    sp['nome'] if sp else None,
        'ob_prov':    pr['prov'] if pr else None,
        'ob_co2stoc': g(eco, 'biologia'),
        'ob_co2seq':  g(eco, 'co2'),
        'ob_o2':      g(eco, 'o2'),
        'ob_inq':     g(eco, 'i'),
        'ob_valeco':  g(eco, 'valore_eco'),
        'ob_valorn':  g(orn, 'val_def'),
        'ob_qorn':    round(g(orn, 'q_orn_bas'), 5) if orn else None,
        'ob_valgl':   res['val_globale'],
        'ob_runmc':   round(run['runoff_mc'], 5) if run else None,
        'ob_runeur':  round(run['runoff_mc'] * 1.9, 2) if run else None,
        'ob_runcls':  g(run, 'classe'),
        'ob_runevmc': round(run_ev['runoff_ev'], 6) if run_ev else None,
        'ob_runevcl': g(run_ev, 'classe_ev'),
        'ob_raffdt':  round(raff['avg_dt'], 3) if raff else None,
        'ob_kwh':     round(raff['tot_kwh'], 3) if raff else None,
        'ob_raffco2': round(raff['tot_co2'], 3) if raff else None,
        'ob_raffeur': round(raff['tot_euro'], 2) if raff else None,
        'ob_area':    round(raff['area_inf'], 3) if raff else None,
        'ob_rinf':    round(raff['r_inf'], 3) if raff else None,
        'ob_dtN':     round(dt['nord'], 4) if raff else None,
        'ob_dtE':     round(dt['est'], 4) if raff else None,
        'ob_dtO':     round(dt['ovest'], 4) if raff else None,
        'ob_dtS':     round(dt['sud'], 4) if raff else None,
        'ob_co2avf':  g(co2av, 'co2_finale'),
        'ob_valecav': g(co2av, 'valore_eco_avanzato'),
        'ob_valglav': res['val_globale_av'],
        'ob_mauto':   g(mob, 'co2_auto'),
        'ob_mbus':    g(mob, 'co2_scuolabus'),
        'ob_mnauto':  g(mob, 'neutro_auto'),
        'ob_mnbus':   g(mob, 'neutro_scuolabus'),
    }

# -*- coding: utf-8 -*-
"""
orebla_fields.py - Definizioni condivise tra gli algoritmi Processing
di calcolo (a TAB) e la creazione del layer vuoto.

Contiene:
  - INPUT_FIELDS : specifica di tutti i campi-parametro (nome, tipo, tab di
                   appartenenza, tipo di widget, gruppo di opzioni)
  - OUT_FIELDS   : campi di output (prefisso ob_)
  - helper per ValueMap e per il calcolo della zona UTM

BILINGUE / BILINGUAL
--------------------
Le etichette e le voci delle tendine NON sono piu' scritte qui: si ricavano da
orebla_i18n in base alla lingua corrente. I NOMI dei campi e i VALORI
memorizzati sono invece invariati in ogni lingua, cosi' un inventario resta
utilizzabile e ricalcolabile indipendentemente dalla lingua dell'interfaccia.

Labels and drop-down entries are no longer hard-coded here: they come from
orebla_i18n according to the current language. Field NAMES and STORED VALUES
are language-independent, so an inventory stays usable and re-computable
whatever the interface language is.
"""

from qgis.PyQt.QtCore import QVariant

from .orebla_data import SPECIE_DATA, PROVINCE_DATA, PROVINCE_EXTRA_SIGLA
from . import orebla_i18n as I18N


# --------------------------------------------------------------------
#  VOCABOLARI DINAMICI (menu a tendina)
#  ogni voce: (descrizione_mostrata, valore_memorizzato)
# --------------------------------------------------------------------

def opts(name, lang=None):
    """Voci tradotte di un gruppo di opzioni definito in orebla_i18n."""
    return I18N.options(name, lang)


def specie_opts():
    """Specie: descrizione = nome, valore = nome. I nomi botanici e i nomi
    comuni della libreria non vengono tradotti (restano come da dataset)."""
    return sorted([(s['nome'], s['nome']) for s in SPECIE_DATA],
                  key=lambda t: t[0].lower())


def prov_opts(lang=None):
    """Province: descrizione = "Nome (SIG)", valore = sigla.

    La voce generica extra-Italia e' sempre in cima all'elenco.
    The generic non-Italian entry is always listed first.
    """
    lang = I18N.lang_or_current(lang)
    extra = []
    normal = []
    for p in PROVINCE_DATA:
        if lang != 'it' and p.get('prov_' + lang):
            nome = p['prov_' + lang]
        else:
            nome = p['prov']
        item = ('%s (%s)' % (nome, p['sigla']), p['sigla'])
        if p['sigla'] == PROVINCE_EXTRA_SIGLA:
            extra.append(item)
        else:
            normal.append(item)
    return extra + sorted(normal, key=lambda t: t[0].lower())


# --------------------------------------------------------------------
#  SPECIFICA CAMPI DI INPUT
#  key, qtype, tab ('base'|'avanzati'|'clima'), widget, opts_name
#  widget: 'map' (tendina), 'text', 'num'
#  opts_name: nome del gruppo di opzioni in orebla_i18n, oppure
#             'specie' / 'provincia' (liste generate dal dataset), oppure None
# --------------------------------------------------------------------

INPUT_FIELDS = [
    # ---- BASE ----
    dict(key='cod_alb', qtype=QVariant.String, tab='base', widget='text', opts_name=None),
    dict(key='specie', qtype=QVariant.String, tab='base', widget='map', opts_name='specie'),
    dict(key='provincia', qtype=QVariant.String, tab='base', widget='map', opts_name='provincia'),
    dict(key='fito', qtype=QVariant.String, tab='base', widget='map', opts_name='fito'),
    dict(key='h', qtype=QVariant.Double, tab='base', widget='num', opts_name=None),
    dict(key='dbh', qtype=QVariant.Double, tab='base', widget='num', opts_name=None),
    dict(key='circonf', qtype=QVariant.Double, tab='base', widget='num', opts_name=None),
    dict(key='d_ch', qtype=QVariant.Double, tab='base', widget='num', opts_name=None),
    dict(key='inser_c', qtype=QVariant.Double, tab='base', widget='num', opts_name=None),
    dict(key='stadio', qtype=QVariant.String, tab='base', widget='map', opts_name='stadio'),
    dict(key='vital', qtype=QVariant.Int, tab='base', widget='map', opts_name='vital'),
    dict(key='p_soc', qtype=QVariant.String, tab='base', widget='map', opts_name='p_soc'),

    # ---- AVANZATI ----
    dict(key='cond_staz', qtype=QVariant.Int, tab='avanzati', widget='map', opts_name='cond_staz'),
    dict(key='chioma_tr', qtype=QVariant.String, tab='avanzati', widget='map', opts_name='chioma_tr'),
    dict(key='cast_p', qtype=QVariant.Int, tab='avanzati', widget='map', opts_name='cast_p'),
    dict(key='strumenti', qtype=QVariant.Int, tab='avanzati', widget='map', opts_name='strumenti'),
    dict(key='dimora', qtype=QVariant.String, tab='avanzati', widget='map', opts_name='dimora'),
    dict(key='organizzazione', qtype=QVariant.String, tab='avanzati', widget='map',
         opts_name='organizzazione'),
    dict(key='fus_p', qtype=QVariant.String, tab='avanzati', widget='map', opts_name='fus_p'),
    dict(key='localizzazione', qtype=QVariant.String, tab='avanzati', widget='map',
         opts_name='localizzazione'),
    dict(key='riduzione', qtype=QVariant.Double, tab='avanzati', widget='map',
         opts_name='riduzione'),
    dict(key='km_eco', qtype=QVariant.Double, tab='avanzati', widget='num', opts_name=None),

    # ---- CLIMA ----
    dict(key='prec_annua', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='n_eventi_pioggia', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='prec_evento', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='rr_evento', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='tmax_media_estiva', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='vento_medio_estivo', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='umidita_rel_estiva', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='prec_giu_ago', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='n_eventi_giu_ago', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
    dict(key='rad_globale_giu_ago', qtype=QVariant.Double, tab='clima', widget='num', opts_name=None),
]

INPUT_FIELDS_BY_KEY = {f['key']: f for f in INPUT_FIELDS}


def field_label(key, lang=None):
    """Etichetta tradotta di un campo di input."""
    return I18N.field_label(key, lang)


def field_options(f, lang=None):
    """Voci della tendina di un campo di input (o None)."""
    name = f.get('opts_name')
    if not name:
        return None
    if name == 'specie':
        return specie_opts()
    if name == 'provincia':
        return prov_opts(lang)
    return opts(name, lang)


# --------------------------------------------------------------------
#  CAMPI DI OUTPUT (prefisso ob_)
#  I NOMI restano invariati in ogni lingua (compatibilita' Shapefile: <=10 car.)
# --------------------------------------------------------------------

OUT_FIELDS = [
    ('ob_spec', QVariant.String),
    ('ob_prov', QVariant.String),
    ('ob_co2stoc', QVariant.Double),
    ('ob_co2seq', QVariant.Double),
    ('ob_o2', QVariant.Double),
    ('ob_inq', QVariant.Double),
    ('ob_valeco', QVariant.Double),
    ('ob_valorn', QVariant.Double),
    ('ob_qorn', QVariant.Double),
    ('ob_valgl', QVariant.Double),
    ('ob_runmc', QVariant.Double),
    ('ob_runeur', QVariant.Double),
    ('ob_runcls', QVariant.String),
    ('ob_runevmc', QVariant.Double),
    ('ob_runevcl', QVariant.String),
    ('ob_raffdt', QVariant.Double),
    ('ob_kwh', QVariant.Double),
    ('ob_raffco2', QVariant.Double),
    ('ob_raffeur', QVariant.Double),
    ('ob_area', QVariant.Double),
    ('ob_rinf', QVariant.Double),
    ('ob_dtN', QVariant.Double),
    ('ob_dtE', QVariant.Double),
    ('ob_dtO', QVariant.Double),
    ('ob_dtS', QVariant.Double),
    ('ob_co2avf', QVariant.Double),
    ('ob_valecav', QVariant.Double),
    ('ob_valglav', QVariant.Double),
    ('ob_mauto', QVariant.Double),
    ('ob_mbus', QVariant.Double),
    ('ob_mnauto', QVariant.Double),
    ('ob_mnbus', QVariant.Double),
]

OUT_FIELD_NAMES = [nm for nm, _t in OUT_FIELDS]


def out_label(name, lang=None):
    """Etichetta tradotta di un campo di output."""
    return I18N.out_label(name, lang)


# Valori del fattore di riduzione per il menu "predefinito" della finestra.
PATOLOGIA_VALS = [0.0, 0.20, 0.40, 0.50, 0.60]


def patologia_labels(lang=None):
    return I18N.option_labels('patologia', lang)


# --------------------------------------------------------------------
#  HELPER ValueMap (menu a tendina nel modulo attributi)
# --------------------------------------------------------------------

def value_map_config(options_list):
    """Restituisce la config per QgsEditorWidgetSetup('ValueMap', cfg),
    preservando l'ordine con una lista di dict {descrizione: valore}."""
    return {'map': [{desc: val} for desc, val in options_list]}


# --------------------------------------------------------------------
#  HELPER UTM
# --------------------------------------------------------------------

def utm_epsg_from_lonlat(lon, lat):
    """EPSG del fuso UTM/WGS84 per la coppia lon/lat data.
    Funziona per qualsiasi fuso 1-60, emisfero nord e sud."""
    try:
        zone = int((float(lon) + 180.0) / 6.0) + 1
        zone = max(1, min(60, zone))
    except (TypeError, ValueError):
        zone = 32  # fallback Italia centro-nord
    if lat is None:
        lat = 45.0
    base = 32600 if float(lat) >= 0 else 32700
    return 'EPSG:%d' % (base + zone)


def build_out_attr_dict(feat_attrs, res, sp, pr, lang=None):
    """Compone il dizionario nome->valore dei campi ob_ a partire dai risultati
    di orebla_core.compute_all(). Condiviso tra gli algoritmi.

    Le classi testuali di runoff vengono restituite nella lingua corrente;
    tutti i valori numerici sono identici in ogni lingua.
    """
    lang = I18N.lang_or_current(lang)

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

    if pr:
        prov_name = pr.get('prov_' + lang) or pr.get('prov') if lang != 'it' else pr.get('prov')
    else:
        prov_name = None

    return {
        'ob_spec': sp['nome'] if sp else None,
        'ob_prov': prov_name,
        'ob_co2stoc': g(eco, 'biologia'),
        'ob_co2seq': g(eco, 'co2'),
        'ob_o2': g(eco, 'o2'),
        'ob_inq': g(eco, 'i'),
        'ob_valeco': g(eco, 'valore_eco'),
        'ob_valorn': g(orn, 'val_def'),
        'ob_qorn': round(g(orn, 'q_orn_bas'), 5) if orn else None,
        'ob_valgl': res['val_globale'],
        'ob_runmc': round(run['runoff_mc'], 5) if run else None,
        'ob_runeur': round(run['runoff_mc'] * 1.9, 2) if run else None,
        'ob_runcls': I18N.tr_class(g(run, 'classe'), lang),
        'ob_runevmc': round(run_ev['runoff_ev'], 6) if run_ev else None,
        'ob_runevcl': I18N.tr_class(g(run_ev, 'classe_ev'), lang),
        'ob_raffdt': round(raff['avg_dt'], 3) if raff else None,
        'ob_kwh': round(raff['tot_kwh'], 3) if raff else None,
        'ob_raffco2': round(raff['tot_co2'], 3) if raff else None,
        'ob_raffeur': round(raff['tot_euro'], 2) if raff else None,
        'ob_area': round(raff['area_inf'], 3) if raff else None,
        'ob_rinf': round(raff['r_inf'], 3) if raff else None,
        'ob_dtN': round(dt['nord'], 4) if raff else None,
        'ob_dtE': round(dt['est'], 4) if raff else None,
        'ob_dtO': round(dt['ovest'], 4) if raff else None,
        'ob_dtS': round(dt['sud'], 4) if raff else None,
        'ob_co2avf': g(co2av, 'co2_finale'),
        'ob_valecav': g(co2av, 'valore_eco_avanzato'),
        'ob_valglav': res['val_globale_av'],
        'ob_mauto': g(mob, 'co2_auto'),
        'ob_mbus': g(mob, 'co2_scuolabus'),
        'ob_mnauto': g(mob, 'neutro_auto'),
        'ob_mnbus': g(mob, 'neutro_scuolabus'),
    }

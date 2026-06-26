# -*- coding: utf-8 -*-
"""
orebla_core.py - Porting fedele in Python della logica di calcolo di
orebla_calc.js (Orebla Tree Valuation).

Replica esatta dei moduli:
  - calc_ecologico        (biomassa, CO2 stoccata/sequestrata, O2, inquinanti, valore eco)
  - calc_ornamentale      (curva logistica RAM su valmax provinciale)
  - calc_runoff_annuo
  - calc_runoff_evento
  - calc_raffrescamento    (4 direzioni)
  - calc_co2_avanzata      (opzionale)
  - calc_sim_mobilita      (opzionale)

Le formule, i coefficienti e l'ordine delle operazioni sono identici al
sorgente JavaScript. Le piccole differenze semantiche tra JS e Python
(Math.round, operatore || di "truthy fallback") sono replicate in modo
puntuale dove rilevante.
"""

import math
import difflib

# ====================================================================
#  HELPERS NUMERICI  (mimano gv()/gs()/Math.round del JS)
# ====================================================================


def js_round(x):
    """Math.round JS: arrotondamento dell'intero piu' vicino, .5 verso +inf."""
    if x is None:
        return None
    try:
        return int(math.floor(float(x) + 0.5))
    except (TypeError, ValueError):
        return None


def pfloat(x):
    """gv() del JS: accetta virgola o punto, ritorna 0.0 se non numerico."""
    if x is None:
        return 0.0
    try:
        return float(str(x).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return 0.0


def pint(x):
    """parseInt() del JS: ritorna int o None se non interpretabile."""
    try:
        return int(float(str(x).strip().replace(',', '.')))
    except (TypeError, ValueError):
        return None


def pstr(x):
    """gs() del JS: stringa trimmata ('' se assente)."""
    if x is None:
        return ''
    return str(x).strip()


def _cat(table, key, fallback):
    """Lookup categoriale: esatto, poi case-insensitive, poi fallback.
    Non sostituisce valori 0 legittimi (mimando i CASE WHEN del JS)."""
    if key in table:
        return table[key]
    kl = key.strip().lower()
    for k, v in table.items():
        if k.lower() == kl:
            return v
    return fallback


# ====================================================================
#  LOOKUP TABLES  (identiche a orebla_calc.js)
# ====================================================================

STADIO_FIT = {'plantula': 10, 'pianta giovane': 20, 'albero giovane': 30,
              'albero adulto': 40, 'albero adulto avanzato': 60,
              'albero senescente': 80, 'albero veterano': 100}

VITAL_FIT = {7: 0, 6: 5, 5: 10, 4: 15, 3: 20, 2: 30, 1: 35}

SOC_ADJ = {'sottoposta': 0.20, 'dominata': 0.15, 'intermedia': 0.10,
           'codominante': 0.08, 'dominante margine': 0.04,
           'dominante interna': 0.06, 'predominante': 0.02,
           'libera (giovane)': 0.00, 'isolata': 0.00}

RAM_PAR = {
    'A': {'par3': 0.59, 'par2': 12, 'par4': 12,  'par5': 0.58},
    'B': {'par3': 0.66, 'par2': 15, 'par4': 9.5, 'par5': 0.65},
    'C': {'par3': 0.72, 'par2': 17, 'par4': 8.6, 'par5': 0.72},
    'D': {'par3': 0.77, 'par2': 19, 'par4': 8.3, 'par5': 0.79},
    'E': {'par3': 0.82, 'par2': 21, 'par4': 8.2, 'par5': 0.86},
}

DIMORA_P = {'prato': 2, 'scarpata': 2, 'terrapieno': 2, 'terreno coltivato': 2,
            'terreno incolto': 2, 'buco asfalto': 1, 'area di pertinenza': 5,
            'banchina stradale': 6, 'rimboschimento': 3, 'tornello': 5,
            'aiuola': 5, 'bosco': 3, 'aiuola spartitraffico': 5,
            'alberata stradale': 6, 'parcheggio': 8, 'gruppo/boschetto': 4,
            'giardino recente': 6, 'filare arboreo': 5, 'piazza': 8,
            'cimitero': 6, 'parco recente': 8, 'giardino storico': 10,
            'parco storico': 15, 'marker': 20}

ORGANIZ_P = {'aree rurali': 3, 'aree rurali urbaniz.': 5, 'periferia recente': 7,
             'periferia antica': 9, 'luoghi villeggiatura': 11,
             'centro città': 13, 'centro storico': 15, 'zone industriali': 6}

FUSE_P = {'nessuno': 0, 'tutela comunale': 6, 'rilevanza comunale': 10,
          'paesaggistico': 8, 'storico-architettonico': 12, 'monumentale': 14}

PSOC_P = {'sottoposta': 1, 'dominata': 2, 'intermedia': 4, 'codominante': 8,
          'dominante margine': 10, 'dominante interna': 8, 'predominante': 15,
          'libera (giovane)': 3, 'isolata': 15}

STADIO_P = {'plantula': 1, 'pianta giovane': 3, 'albero giovane': 5,
            'albero adulto': 8, 'albero adulto avanzato': 10,
            'albero senescente': 15, 'albero veterano': 20}

CAST_RID = {13: 0, 12: 5, 11: 10, 10: 10, 9: 10, 8: 20, 7: 20, 6: 20, 5: 20,
            4: 30, 3: 30, 2: 30, 1: 35}

STRUM_RID = {5: 0, 4: 5, 3: 10, 2: 20, 1: 30}

CHIOMA_K = {'bassa': 1.00, 'media': 0.85, 'alta': 0.65, 'scarsa': 0.40}

CHIOMA_STRESS = {'bassa': 0.70, 'media': 0.40, 'alta': 0.20, 'scarsa': 0.90}

STADIO_STRESS = {'plantula': 0.10, 'pianta giovane': 0.25, 'albero giovane': 0.40,
                 'albero adulto': 0.10, 'albero adulto avanzato': 0.30,
                 'albero senescente': 0.60, 'albero veterano': 0.40}

FOGLIA_ANNUO = {'sempreverde_latifoglia': 1.00, 'decidua_latifoglia': 0.65,
                'conifera': 0.85, 'palma': 0.60}

FOGLIA_EVENTO = {'sempreverde_latifoglia': 1.00, 'decidua_latifoglia': 0.85,
                 'conifera': 0.90, 'palma': 0.75}

LOCALIZ_FSITO = {'alberata stradale': 0.75, 'parcheggio': 0.70, 'piazza': 0.80,
                 'piazzola': 0.85, 'plesso scolastico': 0.95,
                 'impianto sportivo': 1.00, 'giardino recente': 1.00,
                 'parco recente': 1.05, 'giardino storico': 1.10,
                 'parco storico': 1.15, 'bosco': 1.20, 'cimitero': 1.00,
                 'terreno agricolo': 1.10}

FITO_COEFF = {'A': 1.00, 'B': 0.90, 'C': 0.80, 'D': 0.65, 'E': 0.50}

IRU_MIN = 76.3
IRU_MAX = 93.9


def get_iru_base(organizzazione, sp):
    """Replica di getIruBase(): sceglie iru compatto/aperto/specie."""
    if not sp:
        return 88.5
    compatti = ['centro storico', 'centro città', 'periferia antica', 'periferia recente']
    aperti = ['luoghi villeggiatura', 'zone industriali', 'aree rurali urbaniz.', 'aree rurali']
    o = (organizzazione or '').strip()
    if o in compatti:
        return sp['iru_comp']
    if o in aperti:
        return sp['iru_ap']
    return sp['iru_sp']


# ====================================================================
#  1) CALCOLO ECOLOGICO
# ====================================================================

def calc_ecologico(p):
    """p = dict di parametri-albero. Replica calcEcologico()."""
    h = pfloat(p.get('h'))
    dbh = pfloat(p.get('dbh'))
    stadio = pstr(p.get('stadio'))
    vital = p.get('vital')
    p_soc = pstr(p.get('p_soc'))
    if not h or not dbh:
        return None

    a1 = math.pi / 4.0
    b = (dbh / 100.0) * (dbh / 100.0)
    bio = a1 * b * h * 0.9 * 900.0

    fit_val = (VITAL_FIT.get(pint(vital)) or 0.1)        # eco: fallback 0.1
    stadio_v = (_cat(STADIO_FIT, stadio, None) or 0.1)

    b_su_fit = bio / stadio_v
    b_su_fit2 = bio * 0.2 / stadio_v

    adj = SOC_ADJ.get(p_soc)
    if adj is None:
        adj = SOC_ADJ.get(p_soc.lower()) if p_soc else None
    soc_rid = (1 - fit_val / 100.0 - adj) if adj is not None else 0.1

    co2 = js_round(b_su_fit * soc_rid) if fit_val != 35 else 0
    o2 = js_round((b_su_fit * soc_rid) / 44.01 * 31.999 * 0.9) if fit_val != 35 else 0
    i_val = js_round(b_su_fit2 * soc_rid) if fit_val != 35 else 0

    valore_eco = js_round(
        bio * 0.55
        + (b_su_fit * soc_rid)
        + ((b_su_fit * soc_rid) / 44.01 * 31.999 * 0.9) * 5
        + (b_su_fit2 * soc_rid) * 10
    )
    return {'biologia': js_round(bio), 'co2': co2, 'o2': o2,
            'i': i_val, 'valore_eco': valore_eco}


# ====================================================================
#  2) CALCOLO ORNAMENTALE
# ====================================================================

def calc_ornamentale(p, provincia):
    """Replica calcOrnamentale(). provincia = dict da PROVINCE_DATA (o None)."""
    if not provincia:
        return None

    vital = p.get('vital')
    cast_p = p.get('cast_p')
    strumenti_val = p.get('strumenti')
    ch_p = pfloat(provincia.get('valmax'))
    ram_p = pstr(p.get('fito')).upper() or 'C'
    circonf = pfloat(p.get('circonf'))
    d_ch_m = pfloat(p.get('d_ch'))
    h = pfloat(p.get('h'))
    stadio = pstr(p.get('stadio'))
    dimora = pstr(p.get('dimora'))
    organizzazione = pstr(p.get('organizzazione'))
    fus_p = pstr(p.get('fus_p'))
    p_soc = pstr(p.get('p_soc'))

    rid1 = (VITAL_FIT.get(pint(vital)) or 0)      # ornamentale: fallback 0
    rid2 = (CAST_RID.get(pint(cast_p)) or 0)
    rid3 = (STRUM_RID.get(pint(strumenti_val)) or 0)

    if circonf > 350:
        cr = 1.0 / (1.0 + math.exp(-40 * (circonf / 4500.0 - 0.06)))
    else:
        cr = 1.0 / (1.0 + math.exp(-45 * (circonf / 2200.0 - 0.15)))

    ch_val = 1.0 / (1.0 + math.exp(-12 * (d_ch_m / 100.0 - 0.4)))
    hh = 1.0 / (1.0 + math.exp(-35 * (h / 125.0 - 0.22)))

    st_p = _cat(STADIO_P, stadio, 0)
    ps_p = _cat(PSOC_P, p_soc, 0)
    dm_p = _cat(DIMORA_P, dimora, 0)
    or_p = _cat(ORGANIZ_P, organizzazione, 0)
    vin_p = _cat(FUSE_P, fus_p, 0)

    gc = max(cr, hh, ch_val)
    qb = gc + (1 - gc) * ((cr + hh + ch_val - gc) / 2.0)
    q_funz = (st_p + dm_p + ps_p + or_p + vin_p) / 100.0
    q_orn_bas = qb + (1 - qb) * q_funz

    par = RAM_PAR.get(ram_p)
    if not par:
        return None

    if q_orn_bas < par['par3']:
        val_base = ch_p / (1.0 + math.exp(-par['par4'] * (q_orn_bas - par['par5'])))
        val_def = js_round(val_base - val_base * (rid1 + rid2 + rid3) / 100.0)
    elif q_orn_bas > par['par3']:
        val_base = ch_p / (1.0 + math.exp(-par['par2'] * (q_orn_bas - par['par3'])))
        val_def = js_round(val_base - val_base * (rid1 + rid2 + rid3) / 100.0)
    else:
        val_base = 0
        val_def = 0

    return {'val_def': js_round(val_def), 'val_base': js_round(val_base),
            'q_orn_bas': q_orn_bas, 'q_funz': q_funz, 'qb': qb,
            'cr': cr, 'hh': hh, 'ch': ch_val,
            'st_p': st_p, 'ps_p': ps_p, 'dm_p': dm_p, 'or_p': or_p, 'vin_p': vin_p,
            'ch_p': ch_p, 'rid1': rid1, 'rid2': rid2, 'rid3': rid3, 'ram_p': ram_p}


# ====================================================================
#  3) RUNOFF ANNUO
# ====================================================================

def calc_runoff_annuo(p, sp):
    d_ch = pfloat(p.get('d_ch'))
    h = pfloat(p.get('h'))
    inser_c = pfloat(p.get('inser_c'))
    vital = p.get('vital')
    cond_staz = pfloat(p.get('cond_staz'))
    chioma_tr = pstr(p.get('chioma_tr'))
    organizzazione = pstr(p.get('organizzazione'))
    prec = pfloat(p.get('prec_annua'))
    n_ev = pfloat(p.get('n_eventi_pioggia'))
    dbh = pfloat(p.get('dbh'))
    if not d_ch or not prec:
        return None

    gruppo = sp['gruppo'] if sp else 'decidua_latifoglia'
    lai = sp['lai'] if sp else 4.8
    c_interc_sp = sp['coeff_interc'] if sp else 1.0
    iru_sp = sp['iru_sp'] if sp else 88.5

    area_chioma = math.pi * (d_ch / 2.0) ** 2
    c_foglia = _cat(FOGLIA_ANNUO, gruppo, 0.70)
    k_ch = _cat(CHIOMA_K, chioma_tr, 0.70)
    c_interc = min(1.0, lai * k_ch * c_interc_sp)

    v = pint(vital)
    v = v if v is not None else 0
    c_assorb = 0.85 if v >= 6 else 0.65 if v >= 4 else 0.40
    if dbh and h:
        c_rall = min(1.0, 0.35 + 0.1 * math.log(1 + max(dbh, 0)) + 0.1 * (h / 20.0))
    else:
        c_rall = 0.5
    c_ins = (1.00 if inser_c <= 2 else 0.90 if inser_c <= 4 else
             0.80 if inser_c <= 6 else 0.70 if inser_c <= 8 else 0.60)
    c_stato = (v / 7.0) * (cond_staz / 7.0)
    c_sat = (0.65 if n_ev >= 120 else 0.75 if n_ev >= 90 else
             0.85 if n_ev >= 60 else 0.95)

    iru_base = get_iru_base(organizzazione, sp)
    c_contesto = min(1.2, max(0.6, iru_base / iru_sp)) if iru_sp else 1.0

    prec_m = prec / 1000.0
    f = c_interc * c_assorb * c_foglia * c_rall * c_ins * c_stato * c_sat * c_contesto
    runoff = prec_m * area_chioma * min(1.0, f * 0.25)

    classe = ('molto alto' if runoff >= 15 else 'alto' if runoff >= 8 else
              'medio' if runoff >= 4 else 'basso' if runoff >= 1.5 else 'molto basso')
    return {'runoff_mc': runoff, 'classe': classe, 'area_chioma': area_chioma}


# ====================================================================
#  4) RUNOFF EVENTO
# ====================================================================

def calc_runoff_evento(p, sp):
    d_ch = pfloat(p.get('d_ch'))
    h = pfloat(p.get('h'))
    inser_c = pfloat(p.get('inser_c'))
    vital = p.get('vital')
    cond_staz = pfloat(p.get('cond_staz'))
    chioma_tr = pstr(p.get('chioma_tr'))
    organizzazione = pstr(p.get('organizzazione'))
    prec_ev = pfloat(p.get('prec_evento'))
    rr_ev = pfloat(p.get('rr_evento'))
    dbh = pfloat(p.get('dbh'))
    if not d_ch or not prec_ev:
        return None

    gruppo = sp['gruppo'] if sp else 'decidua_latifoglia'
    lai = sp['lai'] if sp else 4.8
    c_interc_sp = sp['coeff_interc'] if sp else 1.0
    iru_sp = sp['iru_sp'] if sp else 88.5

    area_chioma = math.pi * (d_ch / 2.0) ** 2
    c_foglia = _cat(FOGLIA_EVENTO, gruppo, 0.80)
    k_ch = _cat(CHIOMA_K, chioma_tr, 0.70)
    c_interc = min(1.0, lai * k_ch * c_interc_sp)

    v = pint(vital)
    v = v if v is not None else 0
    c_assorb = 0.85 if v >= 6 else 0.65 if v >= 4 else 0.40
    if dbh and h:
        c_rall = min(1.0, 0.35 + 0.1 * math.log(1 + max(dbh, 0)) + 0.1 * (h / 20.0))
    else:
        c_rall = 0.5
    c_ins = (1.00 if inser_c <= 2 else 0.90 if inser_c <= 4 else
             0.80 if inser_c <= 6 else 0.70 if inser_c <= 8 else 0.60)
    c_stato = (v / 7.0) * (cond_staz / 7.0)
    c_int = (0.60 if rr_ev >= 40 else 0.75 if rr_ev >= 25 else
             0.85 if rr_ev >= 15 else 0.95)

    iru_base = get_iru_base(organizzazione, sp)
    c_contesto = min(1.2, max(0.6, iru_base / iru_sp)) if iru_sp else 1.0

    prec_m = prec_ev / 1000.0
    f = c_interc * c_assorb * c_foglia * c_rall * c_ins * c_stato * c_contesto * c_int
    runoff_ev = prec_m * area_chioma * min(1.0, f * 0.25)

    pxa = prec_m * area_chioma
    classe_ev = ('evento severo' if pxa >= 1.5 else
                 'evento medio' if pxa >= 0.6 else 'evento lieve')
    return {'runoff_ev': runoff_ev, 'classe_ev': classe_ev}


# ====================================================================
#  5) RAFFRESCAMENTO ESTIVO (4 direzioni)
# ====================================================================

def calc_raffrescamento(p, sp, latitudine=None):
    d_ch = pfloat(p.get('d_ch'))
    h = pfloat(p.get('h'))
    inser_c = pfloat(p.get('inser_c'))
    vital = p.get('vital')
    cond_staz = pfloat(p.get('cond_staz'))
    stadio = pstr(p.get('stadio'))
    chioma_tr = pstr(p.get('chioma_tr'))
    organizzazione = pstr(p.get('organizzazione'))
    localizzazione = pstr(p.get('localizzazione'))
    tmax = pfloat(p.get('tmax_media_estiva'))
    vento = pfloat(p.get('vento_medio_estivo'))
    umid = pfloat(p.get('umidita_rel_estiva'))
    prec_ea = pfloat(p.get('prec_giu_ago'))
    n_ev_ea = pfloat(p.get('n_eventi_giu_ago'))
    rad_input = pfloat(p.get('rad_globale_giu_ago'))
    rad = rad_input / 3.5
    if not d_ch or not h:
        return None

    iru_raw = get_iru_base(organizzazione, sp)
    iru_sp_raw = sp['iru_sp'] if sp else 88.5

    iru_scale_sp = 1 + (iru_sp_raw - IRU_MIN) / (IRU_MAX - IRU_MIN) * 4
    k_scherm = (0.85 if iru_scale_sp >= 4.5 else 0.75 if iru_scale_sp >= 3.5 else
                0.65 if iru_scale_sp >= 2.5 else 0.55)

    f_stress = (0.85 if tmax >= 38 else 0.70 if tmax >= 35 else
                0.50 if tmax >= 32 else 0.40 if tmax >= 30 else 0.25)
    v = pint(vital)
    v = v if v is not None else 0
    stress_vital = v / 7.0
    stress_staz = cond_staz / 7.0
    stress_stadio = _cat(STADIO_STRESS, stadio, 0.40)
    stress_chioma = _cat(CHIOMA_STRESS, chioma_tr, 0.50)
    stress_ins = (0.10 if inser_c <= 2 else 0.25 if inser_c <= 5 else
                  0.45 if inser_c <= 8 else 0.65)

    ist = max(0.1, 1 - (f_stress + stress_vital + stress_staz +
                        stress_stadio + stress_chioma + stress_ins) / 6.0)

    f_vento = min(1.10, max(0.70, 1 - ((vento - 2.5) / 3.0) ** 2))
    if umid <= 45:
        f_umid = 1.15
    elif umid <= 60:
        f_umid = 1.15 - (umid - 45) * (0.15 / 15)
    elif umid <= 80:
        f_umid = 1.00 - (umid - 60) * (0.40 / 20)
    else:
        f_umid = 0.60
    if prec_ea < 80:
        f_prec = 0.70
    elif prec_ea <= 150:
        f_prec = 0.85 + (prec_ea - 80) * (0.15 / 70)
    else:
        f_prec = 1.05
    if n_ev_ea < 5:
        f_nev = 0.80
    elif n_ev_ea <= 15:
        f_nev = 0.90 + (n_ev_ea - 5) * (0.20 / 10)
    else:
        f_nev = 1.10
    f_idrico = f_prec * f_nev
    f_sito = _cat(LOCALIZ_FSITO, localizzazione, 1.00)

    r_chioma = d_ch / 2.0
    area_inf = (math.pi * r_chioma ** 2) + (d_ch * max(0, h - inser_c) * 0.5)
    r_inf = math.sqrt(area_inf / math.pi)

    dirs = [('nord', 0.45), ('est', 0.15), ('ovest', 0.05), ('sud', -0.20)]
    lat = (pfloat(latitudine) or pfloat(p.get('latitudine'))) or 43.8
    f_lat = 1 + 0.01 * abs(lat)

    dir_results = {}
    for d, k_dir in dirs:
        deltaT_base = 3.5 * (1 - math.exp(
            -((iru_raw * f_vento * f_umid * f_idrico * f_sito) * ist * (r_chioma / 3.0)) / 40.0))
        deltaT_dir = deltaT_base * 0.60 * (1 + f_lat * k_dir)
        kwh = (area_inf * 0.60) * (rad * (k_scherm * ist)) / (3.6 * 2.9) * (0.04 * (1 + k_dir))
        dir_results[d] = {'dt': deltaT_dir, 'kwh': kwh,
                          'euro': kwh * 0.28, 'co2': kwh * 0.25}

    avg_dt = (dir_results['nord']['dt'] + dir_results['est']['dt'] +
              dir_results['ovest']['dt'] + dir_results['sud']['dt']) / 4.0
    tot_kwh = (dir_results['nord']['kwh'] + dir_results['est']['kwh'] +
               dir_results['ovest']['kwh'] + dir_results['sud']['kwh'])
    tot_euro = tot_kwh * 0.28
    tot_co2 = tot_kwh * 0.25

    return {'dir': dir_results, 'avg_dt': avg_dt, 'tot_kwh': tot_kwh,
            'tot_euro': tot_euro, 'tot_co2': tot_co2,
            'area_inf': area_inf, 'r_inf': r_inf}


# ====================================================================
#  6) STIMA AVANZATA CO2 (opzionale)
# ====================================================================

def calc_co2_avanzata(p, eco, rid_patologia=0.0):
    if not eco:
        return None
    d_ch = pfloat(p.get('d_ch'))
    h = pfloat(p.get('h'))
    inser_c = pfloat(p.get('inser_c'))
    if not d_ch or not h:
        return None

    r_chioma = d_ch / 2.0
    h_chioma = max(0, h - inser_c)
    vol_cono = (1.0 / 3.0) * math.pi * r_chioma * r_chioma * h_chioma
    bio_branche = vol_cono * 0.01 * 900.0
    co2_branche = bio_branche * 0.55

    co2_totale_base = eco['biologia']
    bio_totale = co2_totale_base + bio_branche
    co2_totale = co2_totale_base + co2_branche

    rid = pfloat(rid_patologia) or 0.0
    co2_finale = js_round(co2_totale * (1 - rid))
    delta = js_round(co2_finale - co2_totale_base)

    fit_val = (VITAL_FIT.get(pint(p.get('vital'))) or 0.1)
    stadio_v = (_cat(STADIO_FIT, pstr(p.get('stadio')), None) or 0.1)
    adj = SOC_ADJ.get(pstr(p.get('p_soc')))
    if adj is None:
        adj = SOC_ADJ.get(pstr(p.get('p_soc')).lower()) if pstr(p.get('p_soc')) else None
    soc_rid = (1 - fit_val / 100.0 - adj) if adj is not None else 0.1

    bio_av = bio_totale
    b_fit_av = bio_av / stadio_v
    b_fit2_av = bio_av * 0.2 / stadio_v

    valore_eco_av_lordo = js_round(
        bio_av * 0.55
        + (b_fit_av * soc_rid)
        + ((b_fit_av * soc_rid) / 44.01 * 31.999 * 0.9) * 5
        + (b_fit2_av * soc_rid) * 10
    )
    valore_eco_avanzato = js_round(valore_eco_av_lordo * (1 - rid))

    return {'vol_cono': vol_cono, 'bio_branche': js_round(bio_branche),
            'co2_branche': js_round(co2_branche),
            'co2_totale_lorda': js_round(co2_totale), 'rid_patologia': rid,
            'co2_finale': co2_finale, 'delta': delta,
            'valore_eco_avanzato': valore_eco_avanzato,
            'valore_eco_base': eco['valore_eco']}


# ====================================================================
#  7) SIMULAZIONI MOBILITA' (opzionale)
# ====================================================================

def calc_sim_mobilita(p, eco, km_eco=None):
    km = pfloat(km_eco) if km_eco is not None else pfloat(p.get('km_eco'))
    if not km or km <= 0:
        return None
    co2_auto = (180 * km * 0.11) / 2.0
    co2_scuolabus = (180 * km * 0.20) / 20.0
    co2_albero = eco['co2'] if eco else 0
    altezza = pfloat(p.get('h'))
    neutro_auto = (co2_auto / co2_albero) if co2_albero > 0 else None
    neutro_scuolabus = (co2_scuolabus / co2_albero) if co2_albero > 0 else None
    return {'km_eco': km,
            'co2_auto': round(co2_auto * 100) / 100.0,
            'co2_scuolabus': round(co2_scuolabus * 100) / 100.0,
            'co2_bici': 0,
            'neutro_auto': (round(neutro_auto * 10) / 10.0) if neutro_auto is not None else None,
            'neutro_scuolabus': (round(neutro_scuolabus * 10) / 10.0) if neutro_scuolabus is not None else None,
            'altezza': altezza}


# ====================================================================
#  LOOKUP SPECIE / PROVINCIA
# ====================================================================

def build_indexes(specie_data, province_data):
    """Crea indici di ricerca per id/nome specie e sigla/nome provincia."""
    sp_by_id = {}
    sp_by_name = {}
    for s in specie_data:
        sp_by_id[str(s['id'])] = s
        sp_by_name[s['nome'].strip().lower()] = s
    pr_by_sigla = {}
    pr_by_name = {}
    for pr in province_data:
        pr_by_sigla[pr['sigla'].strip().upper()] = pr
        pr_by_name[pr['prov'].strip().lower()] = pr
    return sp_by_id, sp_by_name, pr_by_sigla, pr_by_name


def find_specie(value, sp_by_id, sp_by_name):
    """Trova la specie per id esatto o per nome (case-insensitive, anche parziale)."""
    if value is None:
        return None
    key = str(value).strip()
    if not key:
        return None
    if key in sp_by_id:
        return sp_by_id[key]
    kl = key.lower()
    if kl in sp_by_name:
        return sp_by_name[kl]
    # match parziale sul nome (es. "Tilia cordata")
    for name, s in sp_by_name.items():
        if kl in name or name in kl:
            return s
    return None


def find_provincia(value, pr_by_sigla, pr_by_name):
    """Trova la provincia per sigla (es. 'VI') o per nome (es. 'Vicenza')."""
    if value is None:
        return None
    key = str(value).strip()
    if not key:
        return None
    if key.upper() in pr_by_sigla:
        return pr_by_sigla[key.upper()]
    if key.lower() in pr_by_name:
        return pr_by_name[key.lower()]
    return None


def _norm_txt(s):
    return ' '.join(str(s).strip().lower().split())


def build_species_matcher(specie_data):
    """Crea una funzione match(query) -> (specie_dict, punteggio 0..1) che trova
    la specie della libreria col nome piu' simile al valore sorgente dell'utente.
    Confronta nome scientifico, nome comune e nome completo (case-insensitive)."""
    entries = []
    for sp in specie_data:
        nome = sp['nome']
        parts = nome.split(' - ')
        sci = _norm_txt(parts[0]) if parts else _norm_txt(nome)
        common = _norm_txt(parts[1]) if len(parts) > 1 else ''
        entries.append((sp, _norm_txt(nome), sci, common))

    def _score(q, qw, cand):
        if not cand:
            return 0.0
        if q == cand:
            return 1.0
        cw = set(cand.split())
        r = difflib.SequenceMatcher(None, q, cand).ratio()
        if q in cand or cand in q:
            r = max(r, 0.90)
        if len(qw) == 1 and qw[0] in cw:          # query di una parola = parola intera
            r = max(r, 0.96)
        if len(qw) > 1:                            # overlap di parole intere
            overlap = sum(1 for w in qw if w in cw) / float(len(qw))
            if overlap > 0:
                r = max(r, 0.97 * overlap)
        return r

    def match(query):
        q = _norm_txt(query)
        if not q:
            return (None, 0.0)
        qw = q.split()
        best = None
        best_score = -1.0
        for sp, full, sci, common in entries:
            s = max(_score(q, qw, full), _score(q, qw, sci), _score(q, qw, common))
            if s > best_score:
                best_score = s
                best = sp
        return (best, round(best_score, 3))

    return match


# ====================================================================
#  FUNZIONE DI SINTESI: calcola tutti i benefici per un albero
# ====================================================================

def compute_all(p, sp, provincia, latitudine=None,
                do_co2_avanzata=False, rid_patologia=0.0,
                do_mobilita=False, km_eco=None):
    """Esegue tutti i moduli e restituisce un dict piatto di risultati.
    Replica la sequenza di calcola() in orebla_calc.js."""
    eco = calc_ecologico(p)
    orn = calc_ornamentale(p, provincia)
    run = calc_runoff_annuo(p, sp)
    run_ev = calc_runoff_evento(p, sp)
    raff = calc_raffrescamento(p, sp, latitudine=latitudine)

    co2av = calc_co2_avanzata(p, eco, rid_patologia) if (do_co2_avanzata and eco) else None
    mob = calc_sim_mobilita(p, eco, km_eco) if (do_mobilita and eco) else None

    val_globale = ((eco['valore_eco'] if eco else 0) +
                   (orn['val_def'] if orn else 0))
    val_globale_av = None
    if co2av:
        val_globale_av = co2av['valore_eco_avanzato'] + (orn['val_def'] if orn else 0)

    return {
        'eco': eco, 'orn': orn, 'run': run, 'run_ev': run_ev, 'raff': raff,
        'co2av': co2av, 'mob': mob,
        'val_globale': val_globale, 'val_globale_av': val_globale_av,
    }

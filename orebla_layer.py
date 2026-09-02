# -*- coding: utf-8 -*-
"""
orebla_layer.py - Costruzione e configurazione del layer-alberi (inventario).
orebla_layer.py - Building and configuring the tree (inventory) layer.

Espone funzioni condivise da / shared by:
  - creazione inventario (create_layer_algorithm)
  - importazione guidata (import_algorithm)

Il layer risultante ha / the resulting layer has:
  - tutti i campi-parametro del modello (nomi identici in ogni lingua)
  - alias = etichette nella lingua scelta
  - menu a tendina (ValueMap) per i campi categoriali, tradotti
  - modulo attributi organizzato in TAB
"""

from qgis.core import (
    QgsVectorLayer, QgsField, QgsEditorWidgetSetup, QgsEditFormConfig,
    QgsAttributeEditorContainer, QgsAttributeEditorField,
    QgsProcessingLayerPostProcessorInterface,
)

from . import orebla_fields as F
from . import orebla_i18n as I18N

TAB_KEYS = ['base', 'avanzati', 'clima']


def tab_titles(lang=None):
    return [(k, I18N.tr('tab.' + k, lang)) for k in TAB_KEYS]


def tree_field_defs():
    """Lista di QgsField per i campi-parametro dell'inventario.
    I nomi non dipendono dalla lingua."""
    return [QgsField(f['key'], f['qtype']) for f in F.INPUT_FIELDS]


def apply_value_maps_and_aliases(layer, lang=None):
    lang = I18N.lang_or_current(lang)
    flds = layer.fields()
    for f in F.INPUT_FIELDS:
        idx = flds.indexOf(f['key'])
        if idx < 0:
            continue
        layer.setFieldAlias(idx, F.field_label(f['key'], lang))
        options = F.field_options(f, lang)
        if options:
            cfg = F.value_map_config(options)
            layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup('ValueMap', cfg))


def _apply_tabs(layer, groups):
    """Organizza il modulo attributi in TAB. groups = lista di (titolo, [nomi_campo])."""
    cfg = layer.editFormConfig()
    try:
        cfg.clearTabs()
    except Exception:
        pass
    cfg.setLayout(QgsEditFormConfig.TabLayout)
    try:
        root = cfg.invisibleRootContainer()
    except Exception:
        root = None

    for title, names in groups:
        present = [n for n in names if layer.fields().indexOf(n) >= 0]
        if not present:
            continue
        container = QgsAttributeEditorContainer(title, root)
        try:
            container.setIsGroupBox(False)   # rendi TAB, non group-box
        except Exception:
            pass
        try:
            container.setColumnCount(2)
        except Exception:
            pass
        for n in present:
            idx = layer.fields().indexOf(n)
            container.addChildElement(QgsAttributeEditorField(n, idx, container))
        cfg.addTab(container)

    layer.setEditFormConfig(cfg)


def apply_tab_form(layer, lang=None):
    """Organizza l'inventario in TAB (Dati base/avanzati/climatici)."""
    by_tab = {}
    for f in F.INPUT_FIELDS:
        by_tab.setdefault(f['tab'], []).append(f['key'])
    groups = [(title, by_tab.get(key, [])) for key, title in tab_titles(lang)]
    _apply_tabs(layer, groups)


def configure_tree_layer(layer, lang=None):
    """Applica alias, tendine e modulo a TAB al layer dato."""
    lang = I18N.lang_or_current(lang)
    apply_value_maps_and_aliases(layer, lang)
    try:
        apply_tab_form(layer, lang)
    except Exception:
        # Se la versione di QGIS differisce, il layer resta valido senza i TAB.
        pass


# --------------------------------------------------------------------
#  Configurazione del layer di OUTPUT (risultati ob_) con form a TAB
# --------------------------------------------------------------------

OUTPUT_GROUPS = [
    ('grp.match', ['ob_spec', 'ob_prov']),
    ('grp.value', ['ob_co2stoc', 'ob_co2seq', 'ob_o2', 'ob_inq',
                   'ob_valeco', 'ob_valorn', 'ob_qorn', 'ob_valgl']),
    ('grp.runoff', ['ob_runmc', 'ob_runeur', 'ob_runcls', 'ob_runevmc', 'ob_runevcl']),
    ('grp.cooling', ['ob_raffdt', 'ob_kwh', 'ob_raffco2', 'ob_raffeur',
                     'ob_area', 'ob_rinf', 'ob_dtN', 'ob_dtE', 'ob_dtO', 'ob_dtS']),
    ('grp.advanced', ['ob_co2avf', 'ob_valecav', 'ob_valglav',
                      'ob_mauto', 'ob_mbus', 'ob_mnauto', 'ob_mnbus']),
]


def configure_output_layer(layer, lang=None):
    """Applica etichette (alias) e modulo a TAB al layer dei risultati:
    una scheda 'Parametri albero' (campi di input) + schede tematiche per i
    risultati ob_ (valore/ecologia, runoff, raffrescamento, CO2 avanzata/mobilita)."""
    lang = I18N.lang_or_current(lang)
    flds = layer.fields()

    # alias dei parametri di input (se presenti con nome convenzionale)
    for f in F.INPUT_FIELDS:
        idx = flds.indexOf(f['key'])
        if idx >= 0:
            layer.setFieldAlias(idx, F.field_label(f['key'], lang))

    # alias dei campi risultato ob_
    for nm in F.OUT_FIELD_NAMES:
        idx = flds.indexOf(nm)
        if idx >= 0:
            layer.setFieldAlias(idx, F.out_label(nm, lang))

    # scheda 'Parametri albero' = tutti i campi non-ob_, in ordine di layer
    ob_names = set(F.OUT_FIELD_NAMES)
    param_names = [flds.at(i).name() for i in range(flds.count())
                   if flds.at(i).name() not in ob_names]
    groups = [(I18N.tr('grp.params', lang), param_names)]
    groups += [(I18N.tr(key, lang), names) for key, names in OUTPUT_GROUPS]

    try:
        _apply_tabs(layer, groups)
    except Exception:
        pass


def create_tree_layer(crs_authid, name=None, lang=None):
    """Crea un layer di punti in memoria gia' configurato (tendine + TAB)."""
    lang = I18N.lang_or_current(lang)
    name = name or I18N.tr('layer.inventory', lang)
    layer = QgsVectorLayer('Point?crs=%s' % crs_authid, name, 'memory')
    layer.dataProvider().addAttributes(tree_field_defs())
    layer.updateFields()
    configure_tree_layer(layer, lang)
    return layer


class TreeLayerPostProcessor(QgsProcessingLayerPostProcessorInterface):
    """Post-processor Processing: configura il layer di output (alias, tendine,
    modulo a TAB) una volta caricato nel progetto."""

    # mantiene vivi i post-processor (Processing non ne assume la proprieta')
    _keep = []

    @classmethod
    def create(cls, lang=None):
        pp = cls()
        pp.lang = I18N.lang_or_current(lang)
        cls._keep.append(pp)
        return pp

    def postProcessLayer(self, layer, context, feedback):
        try:
            configure_tree_layer(layer, getattr(self, 'lang', None))
        except Exception:
            pass


class OutputLayerPostProcessor(QgsProcessingLayerPostProcessorInterface):
    """Post-processor Processing: configura il layer dei risultati (alias + TAB)."""

    _keep = []

    @classmethod
    def create(cls, lang=None):
        pp = cls()
        pp.lang = I18N.lang_or_current(lang)
        cls._keep.append(pp)
        return pp

    def postProcessLayer(self, layer, context, feedback):
        try:
            configure_output_layer(layer, getattr(self, 'lang', None))
        except Exception:
            pass

# -*- coding: utf-8 -*-
"""
orebla_layer.py - Costruzione e configurazione del layer-alberi (inventario).

Espone funzioni condivise da:
  - creazione inventario (create_layer_algorithm)
  - importazione guidata (import_algorithm)

Il layer risultante ha:
  - tutti i campi-parametro del modello (nomi coincidenti con il calcolatore)
  - alias = etichette esatte della webapp
  - menu a tendina (ValueMap) per i campi categoriali
  - modulo attributi organizzato in TAB (Dati base / avanzati / climatici)
"""

from qgis.core import (
    QgsVectorLayer, QgsField, QgsEditorWidgetSetup, QgsEditFormConfig,
    QgsAttributeEditorContainer, QgsAttributeEditorField,
    QgsProcessingLayerPostProcessorInterface,
)

from . import orebla_fields as F

TAB_LABELS = [('base', 'Dati base'), ('avanzati', 'Dati avanzati'),
              ('clima', 'Dati climatici')]


def tree_field_defs():
    """Lista di QgsField per i campi-parametro dell'inventario."""
    return [QgsField(f['key'], f['qtype']) for f in F.INPUT_FIELDS]


def apply_value_maps_and_aliases(layer):
    flds = layer.fields()
    for f in F.INPUT_FIELDS:
        idx = flds.indexOf(f['key'])
        if idx < 0:
            continue
        layer.setFieldAlias(idx, f['label'])
        if f.get('options'):
            cfg = F.value_map_config(f['options'])
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


def apply_tab_form(layer):
    """Organizza l'inventario in TAB (Dati base/avanzati/climatici)."""
    by_tab = {}
    for f in F.INPUT_FIELDS:
        by_tab.setdefault(f['tab'], []).append(f['key'])
    groups = [(title, by_tab.get(key, [])) for key, title in TAB_LABELS]
    _apply_tabs(layer, groups)


def configure_tree_layer(layer):
    """Applica alias, tendine e modulo a TAB al layer dato."""
    apply_value_maps_and_aliases(layer)
    try:
        apply_tab_form(layer)
    except Exception:
        # Se la versione di QGIS differisce, il layer resta valido senza i TAB.
        pass


# --------------------------------------------------------------------
#  Configurazione del layer di OUTPUT (risultati ob_) con form a TAB
# --------------------------------------------------------------------

OUTPUT_GROUPS = [
    ('Riconoscimento', ['ob_spec', 'ob_prov']),
    ('Valore & ecologia', ['ob_co2stoc', 'ob_co2seq', 'ob_o2', 'ob_inq',
                           'ob_valeco', 'ob_valorn', 'ob_qorn', 'ob_valgl']),
    ('Runoff', ['ob_runmc', 'ob_runeur', 'ob_runcls', 'ob_runevmc', 'ob_runevcl']),
    ('Raffrescamento', ['ob_raffdt', 'ob_kwh', 'ob_raffco2', 'ob_raffeur',
                        'ob_area', 'ob_rinf', 'ob_dtN', 'ob_dtE', 'ob_dtO', 'ob_dtS']),
    ('CO2 avanzata & mobilita', ['ob_co2avf', 'ob_valecav', 'ob_valglav',
                                 'ob_mauto', 'ob_mbus', 'ob_mnauto', 'ob_mnbus']),
]

OB_LABELS = {nm: desc for nm, _typ, desc in F.OUT_FIELDS}


def configure_output_layer(layer):
    """Applica etichette (alias) e modulo a TAB al layer dei risultati:
    una scheda 'Parametri albero' (campi di input) + schede tematiche per i
    risultati ob_ (valore/ecologia, runoff, raffrescamento, CO2 avanzata/mobilita)."""
    flds = layer.fields()

    # alias dei parametri di input (se presenti con nome convenzionale)
    for f in F.INPUT_FIELDS:
        idx = flds.indexOf(f['key'])
        if idx >= 0:
            layer.setFieldAlias(idx, f['label'])

    # alias dei campi risultato ob_
    for nm, desc in OB_LABELS.items():
        idx = flds.indexOf(nm)
        if idx >= 0:
            layer.setFieldAlias(idx, desc)

    # scheda 'Parametri albero' = tutti i campi non-ob_, in ordine di layer
    ob_names = set(OB_LABELS.keys())
    param_names = [flds.at(i).name() for i in range(flds.count())
                   if flds.at(i).name() not in ob_names]
    groups = [('Parametri albero', param_names)] + OUTPUT_GROUPS

    try:
        _apply_tabs(layer, groups)
    except Exception:
        pass


def create_tree_layer(crs_authid, name='Alberi Orebla'):
    """Crea un layer di punti in memoria gia' configurato (tendine + TAB)."""
    layer = QgsVectorLayer('Point?crs=%s' % crs_authid, name, 'memory')
    layer.dataProvider().addAttributes(tree_field_defs())
    layer.updateFields()
    configure_tree_layer(layer)
    return layer


class TreeLayerPostProcessor(QgsProcessingLayerPostProcessorInterface):
    """Post-processor Processing: configura il layer di output (alias, tendine,
    modulo a TAB) una volta caricato nel progetto."""

    # mantiene vivi i post-processor (Processing non ne assume la proprieta')
    _keep = []

    @classmethod
    def create(cls):
        pp = cls()
        cls._keep.append(pp)
        return pp

    def postProcessLayer(self, layer, context, feedback):
        try:
            configure_tree_layer(layer)
        except Exception:
            pass


class OutputLayerPostProcessor(QgsProcessingLayerPostProcessorInterface):
    """Post-processor Processing: configura il layer dei risultati (alias + TAB)."""

    _keep = []

    @classmethod
    def create(cls):
        pp = cls()
        cls._keep.append(pp)
        return pp

    def postProcessLayer(self, layer, context, feedback):
        try:
            configure_output_layer(layer)
        except Exception:
            pass

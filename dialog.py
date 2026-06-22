# -*- coding: utf-8 -*-
"""
dialog.py - Finestra a schede (TAB) per la Stima dei benefici ambientali.

Compatibile con QGIS 4 / Qt6 (enum "scoped"): evita QDialogButtonBox e protegge
gli enum potenzialmente rinominati. Calcola tramite orebla_core e produce layer
di output (punti + opzionali poligoni aree di influenza), riproiettati in UTM.

Schede: Dati base | Dati avanzati | Dati climatici | Opzioni & Output | Info & Guida
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QTabWidget,
    QWidget, QCheckBox, QComboBox, QPushButton, QLabel, QDoubleSpinBox,
    QGroupBox, QMessageBox, QScrollArea, QTextBrowser,
)
from qgis.core import (
    QgsVectorLayer, QgsField, QgsFeature, QgsProject,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry,
    QgsWkbTypes, QgsPointXY, NULL,
)
from qgis.gui import (
    QgsFieldComboBox, QgsMapLayerComboBox, QgsProjectionSelectionWidget,
)

from . import orebla_core as C
from .orebla_data import SPECIE_DATA, PROVINCE_DATA
from . import orebla_fields as F
from . import orebla_about as ABOUT
from . import orebla_layer as OL


TAB_LABELS = [('base', 'Dati base'), ('avanzati', 'Dati avanzati'),
              ('clima', 'Dati climatici')]


def _set_point_filter(combo):
    """Imposta il filtro 'solo layer puntuali' in modo robusto su Qt5/Qt6."""
    try:
        from qgis.core import QgsMapLayerProxyModel
        try:
            combo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
            return
        except Exception:
            combo.setFilters(QgsMapLayerProxyModel.PointLayer)
            return
    except Exception:
        pass
    try:
        from qgis.core import Qgis
        combo.setFilters(Qgis.LayerFilter.PointLayer)
    except Exception:
        pass


def _auto_utm_crs(layer=None):
    lon, lat = 11.0, 45.0
    try:
        if layer is not None and layer.featureCount() > 0:
            ext = layer.extent()
            cx, cy = ext.center().x(), ext.center().y()
            src = layer.crs()
            if src.isValid() and src.authid() != 'EPSG:4326':
                tr = QgsCoordinateTransform(src, QgsCoordinateReferenceSystem('EPSG:4326'),
                                            QgsProject.instance())
                pt = tr.transform(QgsPointXY(cx, cy))
                lon, lat = pt.x(), pt.y()
            else:
                lon, lat = cx, cy
    except Exception:
        pass
    return QgsCoordinateReferenceSystem(F.utm_epsg_from_lonlat(lon, lat))


class OreblaCalcDialog(QDialog):

    def __init__(self, iface, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface = iface
        self.setWindowTitle('QgisTreeBenefits \u2013 Stima benefici ambientali')
        self.setMinimumSize(640, 660)

        self.field_combos = {}
        self.fixed_widgets = {}

        (self._sp_id, self._sp_name,
         self._pr_sig, self._pr_name) = C.build_indexes(SPECIE_DATA, PROVINCE_DATA)

        self._build_ui()
        self._on_layer_changed()

    # ----------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel('Layer di punti-albero:'))
        self.layer_combo = QgsMapLayerComboBox()
        _set_point_filter(self.layer_combo)
        self.layer_combo.layerChanged.connect(self._on_layer_changed)
        top.addWidget(self.layer_combo, 1)
        root.addLayout(top)

        self.tabs = QTabWidget()

        by_tab = {t: [] for t, _ in TAB_LABELS}
        for f in F.INPUT_FIELDS:
            by_tab[f['tab']].append(f)

        for tab_key, tab_title in TAB_LABELS:
            page = QWidget()
            grid = QGridLayout(page)
            grid.setColumnStretch(1, 1)
            row = 0
            if tab_key == 'clima':
                grid.addWidget(QLabel('<b>Campo</b>'), row, 1)
                grid.addWidget(QLabel('<b>Valore fisso</b>'), row, 2, 1, 2)
                row += 1
            for f in by_tab[tab_key]:
                grid.addWidget(QLabel(f['label']), row, 0)
                combo = QgsFieldComboBox()
                combo.setAllowEmptyFieldName(True)
                self.field_combos[f['key']] = combo
                grid.addWidget(combo, row, 1)
                if tab_key == 'clima' and f['widget'] == 'num':
                    chk = QCheckBox('fisso')
                    spin = QDoubleSpinBox()
                    spin.setRange(-1000000.0, 1000000.0)
                    spin.setDecimals(3)
                    spin.setEnabled(False)
                    chk.toggled.connect(spin.setEnabled)
                    self.fixed_widgets[f['key']] = (chk, spin)
                    grid.addWidget(chk, row, 2)
                    grid.addWidget(spin, row, 3)
                row += 1
            grid.setRowStretch(row, 1)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            self.tabs.addTab(scroll, tab_title)

        # --- scheda Opzioni & Output ---
        self.tabs.addTab(self._build_options_tab(), 'Opzioni & Output')

        # --- scheda Info ---
        info = QTextBrowser()
        info.setOpenExternalLinks(True)
        info.setHtml(ABOUT.about_info_html())
        self.tabs.addTab(info, '\u2139 Info')

        # --- scheda Guida (help) ---
        guide = QTextBrowser()
        guide.setOpenExternalLinks(True)
        guide.setHtml(ABOUT.about_help_html())
        self.tabs.addTab(guide, '\u2753 Guida')

        root.addWidget(self.tabs, 1)

        # --- pulsanti (senza QDialogButtonBox, per compatibilita' Qt6) ---
        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_run = QPushButton('Esegui calcolo')
        self.btn_run.clicked.connect(self._run)
        self.btn_close = QPushButton('Chiudi')
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_run)
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

    # ----------------------------------------------------------------
    def _build_options_tab(self):
        page = QWidget()
        form = QFormLayout(page)

        self.chk_co2av = QCheckBox('Calcola stima avanzata CO\u2082 (branche/rami)')
        self.cmb_pat = QComboBox()
        self.cmb_pat.addItems(F.PATOLOGIA_LBL)
        roww = QWidget()
        h = QHBoxLayout(roww)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self.chk_co2av)
        h.addWidget(QLabel('Fattore di riduzione (predefinito):'))
        h.addWidget(self.cmb_pat, 1)
        form.addRow(roww)
        note_rid = QLabel('Il fattore di riduzione pu\u00f2 anche essere prelevato da un '
                          'campo del layer (scheda Dati avanzati \u2192 "Fattore di '
                          'riduzione"); se mappato, ha la priorit\u00e0 su questo predefinito.')
        note_rid.setWordWrap(True)
        note_rid.setStyleSheet('color:#666;font-size:11px;')
        form.addRow(note_rid)

        self.chk_mob = QCheckBox('Calcola simulazioni di mobilit\u00e0 (campo "Km percorsi")')
        form.addRow(self.chk_mob)

        self.chk_buffer = QCheckBox('Genera i poligoni delle aree di influenza '
                                    '(buffer = raggio di influenza)')
        form.addRow(self.chk_buffer)

        self.crs_widget = QgsProjectionSelectionWidget()
        self.crs_widget.setCrs(_auto_utm_crs())
        form.addRow('CRS di output (UTM):', self.crs_widget)

        hint = QLabel('Suggerimento: per tutta una citt\u00e0 i dati climatici sono spesso '
                      'uguali; usa i "valori fissi" nella scheda Dati climatici invece di '
                      'un campo del layer.')
        hint.setWordWrap(True)
        hint.setStyleSheet('color:#666;font-size:11px;')
        form.addRow(hint)
        return page

    # ----------------------------------------------------------------
    def _on_layer_changed(self, *args):
        layer = self.layer_combo.currentLayer()
        for key, combo in self.field_combos.items():
            combo.setLayer(layer)
            if layer is not None and layer.fields().indexOf(key) >= 0:
                combo.setField(key)
            else:
                combo.setField('')
        if layer is not None:
            self.crs_widget.setCrs(_auto_utm_crs(layer=layer))

    # ----------------------------------------------------------------
    def _get_param(self, feat, key):
        if key in self.fixed_widgets and self.fixed_widgets[key][0].isChecked():
            return self.fixed_widgets[key][1].value()
        combo = self.field_combos.get(key)
        fn = combo.currentField() if combo else ''
        if fn:
            try:
                raw = feat[fn]
            except KeyError:
                raw = None
            if raw is not None and raw != NULL and not (isinstance(raw, str) and raw.strip() == ''):
                return raw
        return None

    # ----------------------------------------------------------------
    def _is_point_layer(self, layer):
        try:
            return QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.PointGeometry
        except Exception:
            return True

    # ----------------------------------------------------------------
    def _run(self):
        layer = self.layer_combo.currentLayer()
        if layer is None or not isinstance(layer, QgsVectorLayer):
            QMessageBox.warning(self, 'QgisTreeBenefits', 'Seleziona un layer di punti valido.')
            return
        if not self._is_point_layer(layer):
            QMessageBox.warning(self, 'QgisTreeBenefits', 'Il layer deve essere di tipo punto.')
            return

        out_crs = self.crs_widget.crs()
        if out_crs is None or not out_crs.isValid():
            out_crs = layer.crs()

        do_co2av = self.chk_co2av.isChecked()
        rid_pat_default = F.PATOLOGIA_VALS[self.cmb_pat.currentIndex()]
        do_mob = self.chk_mob.isChecked()
        do_buffer = self.chk_buffer.isChecked()

        src = layer.crs()
        wgs = QgsCoordinateReferenceSystem('EPSG:4326')
        tr_wgs = None
        if src.isValid() and src.authid() != 'EPSG:4326':
            tr_wgs = QgsCoordinateTransform(src, wgs, QgsProject.instance())
        tr_out = None
        if src.isValid() and out_crs.isValid() and src != out_crs:
            tr_out = QgsCoordinateTransform(src, out_crs, QgsProject.instance())

        out_pt = QgsVectorLayer('Point?crs=%s' % out_crs.authid(),
                                'Alberi - benefici (Orebla)', 'memory')
        op = out_pt.dataProvider()
        in_fields = [layer.fields().at(i) for i in range(layer.fields().count())]
        op.addAttributes(in_fields)
        op.addAttributes([QgsField(nm, typ) for nm, typ, _d in F.OUT_FIELDS])
        out_pt.updateFields()

        out_poly = None
        pp = None
        if do_buffer:
            out_poly = QgsVectorLayer('Polygon?crs=%s' % out_crs.authid(),
                                      'Aree di influenza (Orebla)', 'memory')
            pp = out_poly.dataProvider()
            pp.addAttributes(in_fields)
            pp.addAttributes([QgsField(nm, typ) for nm, typ, _d in F.OUT_FIELDS])
            out_poly.updateFields()

        n_tot = n_no_sp = n_no_pr = 0
        pt_feats = []
        poly_feats = []

        for feat in layer.getFeatures():
            n_tot += 1
            p = {f['key']: self._get_param(feat, f['key']) for f in F.INPUT_FIELDS}

            # Latitudine: sempre dalla geometria del punto
            lat = None
            if feat.hasGeometry():
                try:
                    g = feat.geometry()
                    pt = g.asPoint() if not g.isMultipart() else g.centroid().asPoint()
                    if tr_wgs is not None:
                        pt = tr_wgs.transform(pt)
                    lat = pt.y()
                except Exception:
                    pass
            p['latitudine'] = lat

            sp = C.find_specie(p.get('specie'), self._sp_id, self._sp_name)
            pr = C.find_provincia(p.get('provincia'), self._pr_sig, self._pr_name)
            if sp is None:
                n_no_sp += 1
            if pr is None:
                n_no_pr += 1

            rid = C.pfloat(p['riduzione']) if p.get('riduzione') is not None else rid_pat_default
            res = C.compute_all(p, sp, pr, latitudine=lat,
                                do_co2_avanzata=do_co2av, rid_patologia=rid,
                                do_mobilita=do_mob, km_eco=p.get('km_eco'))

            vals = F.build_out_attr_dict(feat.attributes(), res, sp, pr)
            attrs = list(feat.attributes())
            for nm, _typ, _d in F.OUT_FIELDS:
                v = vals.get(nm)
                attrs.append(v if v is not None else NULL)

            geom = QgsGeometry(feat.geometry()) if feat.hasGeometry() else QgsGeometry()
            if not geom.isEmpty() and tr_out is not None:
                try:
                    geom.transform(tr_out)
                except Exception:
                    pass

            nf = QgsFeature(out_pt.fields())
            nf.setGeometry(geom)
            nf.setAttributes(attrs)
            pt_feats.append(nf)

            if out_poly is not None and res['raff'] is not None and not geom.isEmpty():
                r_inf = res['raff'].get('r_inf')
                if r_inf and r_inf > 0:
                    bf = QgsFeature(out_poly.fields())
                    bf.setGeometry(geom.buffer(float(r_inf), 24))
                    bf.setAttributes(attrs)
                    poly_feats.append(bf)

        op.addFeatures(pt_feats)
        try:
            OL.configure_output_layer(out_pt)
        except Exception:
            pass
        QgsProject.instance().addMapLayer(out_pt)
        if out_poly is not None:
            pp.addFeatures(poly_feats)
            try:
                OL.configure_output_layer(out_poly)
            except Exception:
                pass
            QgsProject.instance().addMapLayer(out_poly)

        msg = 'Calcolo completato su %d alberi. Output in %s.' % (n_tot, out_crs.authid())
        extra = []
        if n_no_sp:
            extra.append('%d senza specie riconosciuta (default)' % n_no_sp)
        if n_no_pr:
            extra.append('%d senza provincia (no valore ornamentale)' % n_no_pr)
        if extra:
            msg += '\n' + '; '.join(extra) + '.'
        try:
            self.iface.messageBar().pushInfo('QgisTreeBenefits', msg)
        except Exception:
            pass
        QMessageBox.information(self, 'QgisTreeBenefits', msg)
        self.accept()

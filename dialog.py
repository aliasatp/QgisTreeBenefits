# -*- coding: utf-8 -*-
"""
dialog.py - Finestra a schede (TAB) per la Stima dei benefici ambientali.
dialog.py - Tabbed window for the environmental benefit assessment.

Compatibile con QGIS 4 / Qt6 (enum "scoped"): evita QDialogButtonBox e protegge
gli enum potenzialmente rinominati. Calcola tramite orebla_core e produce layer
di output (punti + opzionali poligoni aree di influenza), riproiettati in UTM.

Schede: Dati base | Dati avanzati | Dati climatici | Opzioni & Output | Info | Guida
Tabs:   Basic data | Advanced data | Climate data | Options & Output | Info | Help

La lingua dell'interfaccia si sceglie dal selettore in alto: la finestra si
ricostruisce mantenendo il layer e le scelte gia' fatte.
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QTabWidget,
    QWidget, QCheckBox, QComboBox, QPushButton, QLabel, QDoubleSpinBox,
    QMessageBox, QScrollArea, QTextBrowser,
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
from . import orebla_i18n as I18N
from . import orebla_log as LOG


TAB_KEYS = ['base', 'avanzati', 'clima']


def _set_point_filter(combo):
    """Imposta il filtro 'solo layer puntuali' in modo robusto su Qt5/Qt6.

    Si usano solo le forme "scoped" degli enum, valide sia con PyQt5 (sip >= 4.19.9,
    quindi tutte le versioni di QGIS 3 supportate) sia con PyQt6 / QGIS 4.
    Qgis.LayerFilter e' la collocazione moderna; QgsMapLayerProxyModel.Filter
    resta come ripiego per le versioni di QGIS 3 che non la espongono ancora.
    """
    try:
        from qgis.core import Qgis
        combo.setFilters(Qgis.LayerFilter.PointLayer)
        return
    except Exception as exc:
        LOG.ignored('filtro layer puntuali (Qgis.LayerFilter)', exc)
    try:
        from qgis.core import QgsMapLayerProxyModel
        combo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
    except Exception as exc:
        LOG.ignored('filtro layer puntuali (QgsMapLayerProxyModel.Filter)', exc)


def _auto_utm_crs(layer=None):
    """Fuso UTM/WGS84 suggerito. Con un layer si ricava dal suo baricentro
    (qualsiasi fuso, entrambi gli emisferi); senza layer si usa un fallback."""
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
    except Exception as exc:
        LOG.ignored('fuso UTM automatico dal layer: uso i valori predefiniti', exc)
    return QgsCoordinateReferenceSystem(F.utm_epsg_from_lonlat(lon, lat))


class OreblaCalcDialog(QDialog):

    def __init__(self, iface, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface = iface
        self.lang = I18N.current_language()

        self.field_combos = {}
        self.fixed_widgets = {}

        (self._sp_id, self._sp_name,
         self._pr_sig, self._pr_name) = C.build_indexes(SPECIE_DATA, PROVINCE_DATA)

        self._root = QVBoxLayout(self)
        self._build_ui()
        self._on_layer_changed()

    # ----------------------------------------------------------------
    def T(self, key):
        return I18N.tr(key, self.lang)

    # ----------------------------------------------------------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
            else:
                sub = item.layout()
                if sub is not None:
                    self._clear_layout(sub)

    # ----------------------------------------------------------------
    def _build_ui(self):
        self.setWindowTitle(self.T('plugin.title'))
        self.setMinimumSize(680, 680)

        root = self._root

        # --- riga superiore: layer + lingua ---
        top = QHBoxLayout()
        top.addWidget(QLabel(self.T('dlg.layer')))
        self.layer_combo = QgsMapLayerComboBox()
        _set_point_filter(self.layer_combo)
        self.layer_combo.layerChanged.connect(self._on_layer_changed)
        top.addWidget(self.layer_combo, 1)

        top.addSpacing(12)
        top.addWidget(QLabel(self.T('lang.label')))
        self.lang_combo = QComboBox()
        for code, name in I18N.LANGS:
            self.lang_combo.addItem(name, code)
        idx = self.lang_combo.findData(self.lang)
        self.lang_combo.setCurrentIndex(max(0, idx))
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top.addWidget(self.lang_combo)
        root.addLayout(top)

        # --- schede dei parametri ---
        self.tabs = QTabWidget()
        self.field_combos = {}
        self.fixed_widgets = {}

        by_tab = {t: [] for t in TAB_KEYS}
        for f in F.INPUT_FIELDS:
            by_tab[f['tab']].append(f)

        for tab_key in TAB_KEYS:
            page = QWidget()
            grid = QGridLayout(page)
            grid.setColumnStretch(1, 1)
            row = 0
            if tab_key == 'clima':
                grid.addWidget(QLabel(self.T('dlg.col.field')), row, 1)
                grid.addWidget(QLabel(self.T('dlg.col.fixed')), row, 2, 1, 2)
                row += 1
            for f in by_tab[tab_key]:
                grid.addWidget(QLabel(F.field_label(f['key'], self.lang)), row, 0)
                combo = QgsFieldComboBox()
                combo.setAllowEmptyFieldName(True)
                self.field_combos[f['key']] = combo
                grid.addWidget(combo, row, 1)
                if tab_key == 'clima' and f['widget'] == 'num':
                    chk = QCheckBox(self.T('dlg.fixed'))
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
            self.tabs.addTab(scroll, self.T('tab.' + tab_key))

        # --- scheda Opzioni & Output ---
        self.tabs.addTab(self._build_options_tab(), self.T('tab.options'))

        # --- scheda Info ---
        info = QTextBrowser()
        info.setOpenExternalLinks(True)
        info.setHtml(ABOUT.about_info_html(self.lang))
        self.tabs.addTab(info, self.T('tab.info'))

        # --- scheda Guida (help) ---
        guide = QTextBrowser()
        guide.setOpenExternalLinks(True)
        guide.setHtml(ABOUT.about_help_html(self.lang))
        self.tabs.addTab(guide, self.T('tab.help'))

        root.addWidget(self.tabs, 1)

        # --- pulsanti (senza QDialogButtonBox, per compatibilita' Qt6) ---
        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_run = QPushButton(self.T('dlg.btn.run'))
        self.btn_run.clicked.connect(self._run)
        self.btn_close = QPushButton(self.T('dlg.btn.close'))
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_run)
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

    # ----------------------------------------------------------------
    def _build_options_tab(self):
        page = QWidget()
        form = QFormLayout(page)

        self.chk_co2av = QCheckBox(self.T('dlg.opt.co2av'))
        self.cmb_pat = QComboBox()
        self.cmb_pat.addItems(F.patologia_labels(self.lang))
        roww = QWidget()
        h = QHBoxLayout(roww)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self.chk_co2av)
        h.addWidget(QLabel(self.T('dlg.opt.rid')))
        h.addWidget(self.cmb_pat, 1)
        form.addRow(roww)
        note_rid = QLabel(self.T('dlg.opt.rid.note'))
        note_rid.setWordWrap(True)
        note_rid.setStyleSheet('color:#666;font-size:11px;')
        form.addRow(note_rid)

        self.chk_mob = QCheckBox(self.T('dlg.opt.mob'))
        form.addRow(self.chk_mob)

        self.chk_buffer = QCheckBox(self.T('dlg.opt.buffer'))
        form.addRow(self.chk_buffer)

        self.crs_widget = QgsProjectionSelectionWidget()
        self.crs_widget.setCrs(_auto_utm_crs())
        form.addRow(self.T('dlg.opt.crs'), self.crs_widget)

        hint = QLabel(self.T('dlg.opt.hint'))
        hint.setWordWrap(True)
        hint.setStyleSheet('color:#666;font-size:11px;')
        form.addRow(hint)
        return page

    # ----------------------------------------------------------------
    def _snapshot(self):
        """Salva le scelte correnti, per ricostruire la finestra in altra lingua."""
        state = {
            'layer': self.layer_combo.currentLayer(),
            'fields': {k: c.currentField() for k, c in self.field_combos.items()},
            'fixed': {k: (chk.isChecked(), spin.value())
                      for k, (chk, spin) in self.fixed_widgets.items()},
            'co2av': self.chk_co2av.isChecked(),
            'pat': self.cmb_pat.currentIndex(),
            'mob': self.chk_mob.isChecked(),
            'buffer': self.chk_buffer.isChecked(),
            'crs': self.crs_widget.crs(),
            'tab': self.tabs.currentIndex(),
        }
        return state

    def _restore(self, state):
        if state.get('layer') is not None:
            self.layer_combo.setLayer(state['layer'])
        self._on_layer_changed()
        for k, fn in state.get('fields', {}).items():
            combo = self.field_combos.get(k)
            if combo is not None and fn:
                combo.setField(fn)
        for k, (checked, val) in state.get('fixed', {}).items():
            w = self.fixed_widgets.get(k)
            if w:
                w[0].setChecked(bool(checked))
                w[1].setValue(float(val))
        self.chk_co2av.setChecked(bool(state.get('co2av')))
        self.cmb_pat.setCurrentIndex(int(state.get('pat') or 0))
        self.chk_mob.setChecked(bool(state.get('mob')))
        self.chk_buffer.setChecked(bool(state.get('buffer')))
        crs = state.get('crs')
        if crs is not None and crs.isValid():
            self.crs_widget.setCrs(crs)
        try:
            self.tabs.setCurrentIndex(int(state.get('tab') or 0))
        except Exception as exc:
            LOG.ignored('ripristino della scheda attiva dopo il cambio lingua', exc)

    # ----------------------------------------------------------------
    def _on_lang_changed(self, *args):
        code = self.lang_combo.currentData()
        if not code or code == self.lang:
            return
        state = self._snapshot()
        self.lang = code
        I18N.set_language(code)
        _refresh_provider()
        self._clear_layout(self._root)
        self._build_ui()
        self._restore(state)

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
            return (QgsWkbTypes.geometryType(layer.wkbType())
                    == QgsWkbTypes.GeometryType.PointGeometry)
        except Exception:
            return True

    # ----------------------------------------------------------------
    def _run(self):
        title = self.T('plugin.title')
        layer = self.layer_combo.currentLayer()
        if layer is None or not isinstance(layer, QgsVectorLayer):
            QMessageBox.warning(self, title, self.T('msg.need.layer'))
            return
        if not self._is_point_layer(layer):
            QMessageBox.warning(self, title, self.T('msg.need.point'))
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
                                self.T('layer.out.points'), 'memory')
        op = out_pt.dataProvider()
        in_fields = [layer.fields().at(i) for i in range(layer.fields().count())]
        op.addAttributes(in_fields)
        op.addAttributes([QgsField(nm, typ) for nm, typ in F.OUT_FIELDS])
        out_pt.updateFields()

        out_poly = None
        pp = None
        if do_buffer:
            out_poly = QgsVectorLayer('Polygon?crs=%s' % out_crs.authid(),
                                      self.T('layer.out.polygons'), 'memory')
            pp = out_poly.dataProvider()
            pp.addAttributes(in_fields)
            pp.addAttributes([QgsField(nm, typ) for nm, typ in F.OUT_FIELDS])
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
                except Exception as exc:
                    LOG.ignored('latitudine dalla geometria del punto', exc)
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

            vals = F.build_out_attr_dict(feat.attributes(), res, sp, pr, lang=self.lang)
            attrs = list(feat.attributes())
            for nm, _typ in F.OUT_FIELDS:
                v = vals.get(nm)
                attrs.append(v if v is not None else NULL)

            geom = QgsGeometry(feat.geometry()) if feat.hasGeometry() else QgsGeometry()
            if not geom.isEmpty() and tr_out is not None:
                try:
                    geom.transform(tr_out)
                except Exception as exc:
                    LOG.ignored('riproiezione della geometria nel CRS di output', exc)

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
            OL.configure_output_layer(out_pt, self.lang)
        except Exception as exc:
            LOG.ignored('configurazione del layer di output (punti)', exc)
        QgsProject.instance().addMapLayer(out_pt)
        if out_poly is not None:
            pp.addFeatures(poly_feats)
            try:
                OL.configure_output_layer(out_poly, self.lang)
            except Exception as exc:
                LOG.ignored('configurazione del layer di output (poligoni)', exc)
            QgsProject.instance().addMapLayer(out_poly)

        msg = self.T('msg.done') % (n_tot, out_crs.authid())
        extra = []
        if n_no_sp:
            extra.append(self.T('msg.no.species') % n_no_sp)
        if n_no_pr:
            extra.append(self.T('msg.no.prov') % n_no_pr)
        if extra:
            msg += '\n' + '; '.join(extra) + '.'
        try:
            self.iface.messageBar().pushInfo('QgisTreeBenefits', msg)
        except Exception as exc:
            LOG.ignored('notifica nella barra dei messaggi', exc)
        QMessageBox.information(self, title, msg)
        self.accept()


def _refresh_provider():
    """Aggiorna i nomi degli algoritmi nella Cassetta degli strumenti dopo un
    cambio di lingua."""
    try:
        from qgis.core import QgsApplication
        prov = QgsApplication.processingRegistry().providerById('qgistreebenefits')
        if prov is not None:
            prov.refreshAlgorithms()
    except Exception as exc:
        LOG.ignored('aggiornamento della Cassetta degli strumenti', exc)

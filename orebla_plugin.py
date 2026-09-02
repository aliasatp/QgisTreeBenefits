# -*- coding: utf-8 -*-
"""Plugin QgisTreeBenefits: provider Processing + voci di menu (finestra a
schede e selettore di lingua).

QgisTreeBenefits plugin: Processing provider + menu entries (tabbed window and
language selector).
"""

from qgis.PyQt.QtWidgets import QAction, QInputDialog
from qgis.core import QgsApplication
from .provider import OreblaProvider
from . import orebla_i18n as I18N


class OreblaPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.menu = I18N.tr('plugin.menu')
        self.action = None
        self.action_lang = None
        self._calc_dlg = None

    def initProcessing(self):
        self.provider = OreblaProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        # Tutti gli algoritmi sono nella Cassetta degli strumenti di Processing.
        self.initProcessing()
        # In piu', la Stima benefici ha una finestra dedicata a schede (TAB),
        # richiamabile da menu Plugin (nessuna barra degli strumenti).
        self.action = QAction(I18N.tr('plugin.action.calc'),
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run_calc_dialog)
        self.iface.addPluginToMenu(self.menu, self.action)

        # Selettore di lingua, per chi non apre la finestra di stima.
        self.action_lang = QAction(I18N.tr('plugin.action.lang'),
                                   self.iface.mainWindow())
        self.action_lang.triggered.connect(self.choose_language)
        self.iface.addPluginToMenu(self.menu, self.action_lang)

    def unload(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None
        for act in (self.action, self.action_lang):
            if act is not None:
                self.iface.removePluginMenu(self.menu, act)
        self.action = None
        self.action_lang = None

    def run_calc_dialog(self):
        from .dialog import OreblaCalcDialog
        self._calc_dlg = OreblaCalcDialog(self.iface)
        self._calc_dlg.show()
        self._calc_dlg.raise_()
        self._calc_dlg.activateWindow()

    def choose_language(self):
        """Dialogo minimale per scegliere la lingua (auto / italiano / inglese)."""
        choices = I18N.language_choices()
        labels = [lbl for lbl, _c in choices]
        codes = [c for _l, c in choices]
        try:
            current = codes.index(I18N.stored_language())
        except ValueError:
            current = 0
        label, ok = QInputDialog.getItem(
            self.iface.mainWindow(), I18N.tr('lang.dialog.title'),
            I18N.tr('lang.dialog.text'), labels, current, False)
        if not ok:
            return
        I18N.set_language(codes[labels.index(label)])
        self._retranslate()

    def _retranslate(self):
        """Riapplica le etichette di menu e aggiorna la Cassetta degli strumenti."""
        if self.action is not None:
            self.action.setText(I18N.tr('plugin.action.calc'))
        if self.action_lang is not None:
            self.action_lang.setText(I18N.tr('plugin.action.lang'))
        if self.provider is not None:
            try:
                self.provider.refreshAlgorithms()
            except Exception:
                pass

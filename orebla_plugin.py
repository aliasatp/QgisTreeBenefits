# -*- coding: utf-8 -*-
"""Plugin QgisTreeBenefits: provider Processing + voce di menu per la finestra a schede."""

from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication
from .provider import OreblaProvider


class OreblaPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.menu = '&QgisTreeBenefits'
        self.action = None
        self._calc_dlg = None

    def initProcessing(self):
        self.provider = OreblaProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        # Tutti gli algoritmi sono nella Cassetta degli strumenti di Processing.
        self.initProcessing()
        # In piu', la Stima benefici ha una finestra dedicata a schede (TAB),
        # richiamabile da menu Plugin (nessuna barra degli strumenti).
        self.action = QAction('Stima benefici (finestra a schede)\u2026',
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run_calc_dialog)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None
        if self.action is not None:
            self.iface.removePluginMenu(self.menu, self.action)
            self.action = None

    def run_calc_dialog(self):
        from .dialog import OreblaCalcDialog
        self._calc_dlg = OreblaCalcDialog(self.iface)
        self._calc_dlg.show()
        self._calc_dlg.raise_()
        self._calc_dlg.activateWindow()

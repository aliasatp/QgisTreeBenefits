# -*- coding: utf-8 -*-
"""Provider Processing di QgisTreeBenefits.

Espone gli strumenti di gestione dell'inventario (creazione e importazione).
La STIMA BENEFICI non e' un algoritmo batch: e' una finestra a schede
(menu Plugin -> QgisTreeBenefits -> Stima benefici).

Exposes the inventory management tools (create and import). The BENEFIT
ASSESSMENT is not a batch algorithm: it is a tabbed window
(Plugins -> QgisTreeBenefits -> Benefit assessment).
"""

import os
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .create_layer_algorithm import OreblaCreateLayerAlgorithm
from .import_algorithm import OreblaImportAlgorithm
from . import orebla_i18n as I18N


class OreblaProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(OreblaCreateLayerAlgorithm())
        self.addAlgorithm(OreblaImportAlgorithm())

    def id(self):
        return 'qgistreebenefits'

    def name(self):
        return 'QgisTreeBenefits'

    def longName(self):
        return I18N.tr('provider.longname')

    def icon(self):
        path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(path):
            return QIcon(path)
        return QgsProcessingProvider.icon(self)

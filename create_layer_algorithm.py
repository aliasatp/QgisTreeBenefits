# -*- coding: utf-8 -*-
"""Algoritmo Processing: crea un inventario alberi vuoto (layer a schede + tendine).
Processing algorithm: create an empty tree inventory (tabbed layer + drop-downs).
"""

from qgis.core import (
    QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException,
    QgsProcessingParameterCrs, QgsProcessingParameterFeatureSink,
    QgsProcessingParameterEnum,
    QgsFields, QgsWkbTypes,
)

from . import orebla_layer as OL
from . import orebla_about as ABOUT
from . import orebla_i18n as I18N


class OreblaCreateLayerAlgorithm(QgsProcessingAlgorithm):

    CRS = 'CRS'
    LANG = 'LANG'
    OUTPUT = 'OUTPUT'

    # 0 = come impostazione del plugin, 1 = italiano, 2 = inglese
    LANG_CODES = [None, 'it', 'en']

    def createInstance(self):
        return OreblaCreateLayerAlgorithm()

    def name(self):
        return 'crea_inventario'

    def displayName(self):
        return I18N.tr('alg1.name')

    def group(self):
        return I18N.tr('group.name')

    def groupId(self):
        return 'orebla'

    def shortHelpString(self):
        return I18N.tr('alg1.help') + ABOUT.about_html()

    def _lang_options(self):
        lbl = I18N.tr('lang.auto')
        return [lbl] + [nm for _c, nm in I18N.LANGS]

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterCrs(
            self.CRS, I18N.tr('alg1.p.crs'), defaultValue='ProjectCrs'))
        self.addParameter(QgsProcessingParameterEnum(
            self.LANG, I18N.tr('alg1.p.lang'), options=self._lang_options(),
            defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, I18N.tr('alg1.p.out'),
            QgsProcessing.SourceType.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        li = self.parameterAsEnum(parameters, self.LANG, context)
        lang = I18N.lang_or_current(self.LANG_CODES[li] if 0 <= li < 3 else None)

        fields = QgsFields()
        for f in OL.tree_field_defs():
            fields.append(f)

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, QgsWkbTypes.Type.Point, crs)
        if sink is None:
            raise QgsProcessingException(I18N.tr('alg1.err', lang))

        # nessuna feature: layer vuoto pronto per la digitalizzazione

        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(
                OL.TreeLayerPostProcessor.create(lang))

        feedback.pushInfo(I18N.tr('alg1.done', lang))
        return {self.OUTPUT: dest_id}

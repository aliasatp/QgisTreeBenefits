# -*- coding: utf-8 -*-
"""Algoritmo Processing: crea un inventario alberi vuoto (layer a schede + tendine)."""

from qgis.core import (
    QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException,
    QgsProcessingParameterCrs, QgsProcessingParameterFeatureSink,
    QgsFields, QgsWkbTypes,
)

from . import orebla_layer as OL
from . import orebla_about as ABOUT


class OreblaCreateLayerAlgorithm(QgsProcessingAlgorithm):

    CRS = 'CRS'
    OUTPUT = 'OUTPUT'

    def createInstance(self):
        return OreblaCreateLayerAlgorithm()

    def name(self):
        return 'crea_inventario'

    def displayName(self):
        return '1 \u00b7 Crea inventario alberi (layer vuoto a schede)'

    def group(self):
        return 'Stima benefici alberi'

    def groupId(self):
        return 'orebla'

    def shortHelpString(self):
        return (
            "Crea un layer di punti vuoto con tutti i campi-parametro come richiesti "
            "dal plugin. Il layer risultante ha:\n"
            "\u2022 etichette dei campi gi\u00e0 adeguati per fornirli alla funzione di stima;\n"
            "\u2022 menu a tendina (ValueMap) per i campi categoriali;\n"
            "\u2022 modulo attributi organizzato in TAB (Dati base / avanzati / climatici).\n\n"
            "Imposta il CRS desiderato, poi digitalizza gli alberi compilando i campi "
            "dai menu a tendina. Per usare le aree di influenza in seguito conviene un "
            "CRS UTM (in metri).\n\n" + ABOUT.about_html())

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterCrs(
            self.CRS, 'CRS del layer alberi', defaultValue='ProjectCrs'))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, 'Inventario alberi', QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        crs = self.parameterAsCrs(parameters, self.CRS, context)

        fields = QgsFields()
        for f in OL.tree_field_defs():
            fields.append(f)

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, QgsWkbTypes.Point, crs)
        if sink is None:
            raise QgsProcessingException('Impossibile creare il layer di output.')

        # nessuna feature: layer vuoto pronto per la digitalizzazione

        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(
                OL.TreeLayerPostProcessor.create())

        feedback.pushInfo('Inventario vuoto creato. Compila gli alberi dai menu a '
                          'tendina, nelle schede del modulo attributi.')
        return {self.OUTPUT: dest_id}

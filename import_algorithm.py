# -*- coding: utf-8 -*-
"""
Algoritmo Processing: importa/adatta un layer alberi esistente verso il formato
del calcolatore Orebla.

- abbina automaticamente la specie sorgente alla libreria (nome piu' simile);
- mappa i dati biometrici indicati;
- crea un layer a schede + tendine con specie e biometria precompilate; gli altri
  parametri restano da completare (con i menu a tendina) dall'utente.

L'abbinamento delle specie viene riportato nel log con il punteggio di
somiglianza; le voci dubbie si correggono poi nel layer (campo specie a tendina).
"""

from qgis.core import (
    QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException,
    QgsProcessingParameterFeatureSource, QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField, QgsProcessingParameterCrs,
    QgsFields, QgsFeature, QgsGeometry, QgsWkbTypes,
    QgsCoordinateTransform, QgsProject, NULL,
)

from . import orebla_core as C
from .orebla_data import SPECIE_DATA
from . import orebla_layer as OL
from . import orebla_about as ABOUT


class OreblaImportAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    F_SPECIE = 'F_SPECIE'
    F_COD = 'F_COD'
    F_H = 'F_H'
    F_DBH = 'F_DBH'
    F_CIRCONF = 'F_CIRCONF'
    F_DCH = 'F_DCH'
    F_INSERC = 'F_INSERC'
    OUTPUT_CRS = 'OUTPUT_CRS'
    OUTPUT = 'OUTPUT'

    NUM_BIOM = {'h': F_H, 'dbh': F_DBH, 'circonf': F_CIRCONF,
                'd_ch': F_DCH, 'inser_c': F_INSERC}

    def createInstance(self):
        return OreblaImportAlgorithm()

    def name(self):
        return 'importa_alberi'

    def displayName(self):
        return '2 \u00b7 Importa/adatta layer alberi esistente'

    def group(self):
        return 'Stima benefici alberi'

    def groupId(self):
        return 'orebla'

    def shortHelpString(self):
        return (
            "Trasforma un layer-alberi dell'utente in un layer compatibile con il "
            "calcolatore (stessi nomi-parametro \u2192 pesi corretti).\n\n"
            "\u2022 La specie viene abbinata automaticamente alla libreria del plugin "
            "scegliendo il nome piu' simile (nome scientifico/comune); il log riporta "
            "ogni abbinamento con la percentuale di somiglianza.\n"
            "\u2022 I dati biometrici indicati vengono copiati.\n"
            "\u2022 Gli altri parametri (stadio, vitalita, posizione, condizioni, "
            "clima\u2026) si completano nel layer risultante, gia' a schede e con i "
            "menu a tendina; le specie dubbie si correggono dal campo a tendina.\n\n"
            + ABOUT.about_html())

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT, 'Layer alberi sorgente', [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterField(
            self.F_SPECIE, 'Campo con la specie',
            parentLayerParameterName=self.INPUT, optional=True))

        def fld(key, label, num=False):
            p = QgsProcessingParameterField(
                key, label, parentLayerParameterName=self.INPUT, optional=True)
            if num:
                p.setDataType(QgsProcessingParameterField.Numeric)
            self.addParameter(p)

        fld(self.F_COD, 'Campo codice albero (identificativo)')
        fld(self.F_H, 'Campo altezza h (m)', num=True)
        fld(self.F_DBH, 'Campo DBH (cm)', num=True)
        fld(self.F_CIRCONF, 'Campo circonferenza (cm)', num=True)
        fld(self.F_DCH, 'Campo diametro chioma (m)', num=True)
        fld(self.F_INSERC, 'Campo inserzione chioma (m)', num=True)

        self.addParameter(QgsProcessingParameterCrs(
            self.OUTPUT_CRS, 'CRS di output', defaultValue='ProjectCrs'))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, 'Alberi Orebla (importato)', QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException('Layer sorgente non valido.')

        def fname(key):
            v = self.parameterAsString(parameters, key, context)
            return v if v else None

        sp_field = fname(self.F_SPECIE)
        cod_field = fname(self.F_COD)
        biom_fields = {k: fname(v) for k, v in self.NUM_BIOM.items()}

        out_crs = self.parameterAsCrs(parameters, self.OUTPUT_CRS, context)
        src_crs = source.sourceCrs()
        if out_crs is None or not out_crs.isValid():
            out_crs = src_crs

        matcher = C.build_species_matcher(SPECIE_DATA)
        match_cache = {}   # valore sorgente -> (nome_libreria, score)

        fields = QgsFields()
        for f in OL.tree_field_defs():
            fields.append(f)

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, QgsWkbTypes.Point, out_crs)
        if sink is None:
            raise QgsProcessingException('Impossibile creare il layer di output.')

        tr = None
        if src_crs.isValid() and out_crs.isValid() and src_crs != out_crs:
            tr = QgsCoordinateTransform(src_crs, out_crs, QgsProject.instance())

        total = source.featureCount() or 0
        step = (100.0 / total) if total else 0
        n_sp = 0

        for current, sf in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
            nf = QgsFeature(fields)

            geom = QgsGeometry(sf.geometry()) if sf.hasGeometry() else QgsGeometry()
            if not geom.isEmpty() and tr is not None:
                try:
                    geom.transform(tr)
                except Exception:
                    pass
            nf.setGeometry(geom)

            if sp_field:
                try:
                    raw = sf[sp_field]
                except KeyError:
                    raw = None
                key = ('' if raw is None or raw == NULL else str(raw)).strip()
                if key:
                    if key not in match_cache:
                        sp, score = matcher(key)
                        match_cache[key] = (sp['nome'] if sp else None, score)
                    lib, _score = match_cache[key]
                    if lib:
                        nf.setAttribute('specie', lib)
                        n_sp += 1

            if cod_field:
                try:
                    rawc = sf[cod_field]
                except KeyError:
                    rawc = None
                if rawc is not None and rawc != NULL:
                    nf.setAttribute('cod_alb', str(rawc))

            for key, fn in biom_fields.items():
                if not fn:
                    continue
                try:
                    rawv = sf[fn]
                except KeyError:
                    rawv = None
                if rawv is None or rawv == NULL or (isinstance(rawv, str) and rawv.strip() == ''):
                    continue
                nf.setAttribute(key, C.pfloat(rawv))

            sink.addFeature(nf)
            if step:
                feedback.setProgress(int(current * step))

        # Log abbinamento specie
        if match_cache:
            feedback.pushInfo('--- Abbinamento specie (sorgente -> libreria | somiglianza) ---')
            for srcval in sorted(match_cache.keys(), key=lambda x: x.lower()):
                lib, score = match_cache[srcval]
                flag = '  <-- VERIFICARE' if score < 0.6 else ''
                feedback.pushInfo('%s -> %s | %d%%%s'
                                  % (srcval, lib, int(round(score * 100)), flag))
            feedback.pushInfo('Alberi con specie abbinata: %d' % n_sp)

        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(
                OL.TreeLayerPostProcessor.create())

        feedback.pushInfo('Completa gli altri parametri nelle schede del modulo '
                          'attributi (menu a tendina).')
        return {self.OUTPUT: dest_id}

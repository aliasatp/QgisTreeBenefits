# -*- coding: utf-8 -*-
"""
Algoritmo Processing: importa/adatta un layer alberi esistente verso il formato
del calcolatore Orebla.
Processing algorithm: import/adapt an existing tree layer into the Orebla
calculator format.

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
    QgsProcessingParameterEnum,
    QgsFields, QgsFeature, QgsGeometry, QgsWkbTypes,
    QgsCoordinateTransform, QgsProject, NULL,
)

from . import orebla_core as C
from .orebla_data import SPECIE_DATA
from . import orebla_layer as OL
from . import orebla_about as ABOUT
from . import orebla_i18n as I18N
from . import orebla_log as LOG


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
    LANG = 'LANG'
    OUTPUT = 'OUTPUT'

    LANG_CODES = [None, 'it', 'en']

    NUM_BIOM = {'h': F_H, 'dbh': F_DBH, 'circonf': F_CIRCONF,
                'd_ch': F_DCH, 'inser_c': F_INSERC}

    def createInstance(self):
        return OreblaImportAlgorithm()

    def name(self):
        return 'importa_alberi'

    def displayName(self):
        return I18N.tr('alg2.name')

    def group(self):
        return I18N.tr('group.name')

    def groupId(self):
        return 'orebla'

    def shortHelpString(self):
        return I18N.tr('alg2.help') + ABOUT.about_html()

    def _lang_options(self):
        return [I18N.tr('lang.auto')] + [nm for _c, nm in I18N.LANGS]

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT, I18N.tr('alg2.p.in'),
            [QgsProcessing.SourceType.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterField(
            self.F_SPECIE, I18N.tr('alg2.p.specie'),
            parentLayerParameterName=self.INPUT, optional=True))

        def fld(key, label, num=False):
            p = QgsProcessingParameterField(
                key, label, parentLayerParameterName=self.INPUT, optional=True)
            if num:
                p.setDataType(QgsProcessingParameterField.DataType.Numeric)
            self.addParameter(p)

        fld(self.F_COD, I18N.tr('alg2.p.cod'))
        fld(self.F_H, I18N.tr('alg2.p.h'), num=True)
        fld(self.F_DBH, I18N.tr('alg2.p.dbh'), num=True)
        fld(self.F_CIRCONF, I18N.tr('alg2.p.circ'), num=True)
        fld(self.F_DCH, I18N.tr('alg2.p.dch'), num=True)
        fld(self.F_INSERC, I18N.tr('alg2.p.insc'), num=True)

        self.addParameter(QgsProcessingParameterCrs(
            self.OUTPUT_CRS, I18N.tr('alg2.p.crs'), defaultValue='ProjectCrs'))
        self.addParameter(QgsProcessingParameterEnum(
            self.LANG, I18N.tr('alg1.p.lang'), options=self._lang_options(),
            defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, I18N.tr('alg2.p.out'),
            QgsProcessing.SourceType.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        li = self.parameterAsEnum(parameters, self.LANG, context)
        lang = I18N.lang_or_current(self.LANG_CODES[li] if 0 <= li < 3 else None)

        if source is None:
            raise QgsProcessingException(I18N.tr('alg2.err', lang))

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
            parameters, self.OUTPUT, context, fields,
            QgsWkbTypes.Type.Point, out_crs)
        if sink is None:
            raise QgsProcessingException(I18N.tr('alg1.err', lang))

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
                except Exception as exc:
                    LOG.ignored('riproiezione della geometria nel CRS di output', exc)
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

        # Log abbinamento specie / species matching log
        if match_cache:
            feedback.pushInfo(I18N.tr('alg2.log.head', lang))
            for srcval in sorted(match_cache.keys(), key=lambda x: x.lower()):
                lib, score = match_cache[srcval]
                flag = I18N.tr('alg2.log.check', lang) if score < 0.6 else ''
                feedback.pushInfo('%s -> %s | %d%%%s'
                                  % (srcval, lib, int(round(score * 100)), flag))
            feedback.pushInfo(I18N.tr('alg2.log.count', lang) % n_sp)

        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(
                OL.TreeLayerPostProcessor.create(lang))

        feedback.pushInfo(I18N.tr('alg2.done', lang))
        return {self.OUTPUT: dest_id}

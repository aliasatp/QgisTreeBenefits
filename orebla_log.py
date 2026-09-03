# -*- coding: utf-8 -*-
"""
orebla_log.py - Registrazione delle eccezioni non bloccanti.
orebla_log.py - Reporting of non-blocking exceptions.

IT: alcune chiamate del plugin sono volutamente "opzionali": servono a
    supportare versioni diverse di QGIS/Qt (API rinominate fra Qt5 e Qt6) o a
    non interrompere l'elaborazione per una singola geometria non valida. In
    questi casi l'eccezione non deve fermare il plugin, ma non deve nemmeno
    sparire in silenzio: viene scritta nel registro messaggi di QGIS, nella
    scheda "QgisTreeBenefits" (Vista -> Pannelli -> Log dei messaggi).

EN: a few calls in the plugin are deliberately optional: they support different
    QGIS/Qt versions (APIs renamed between Qt5 and Qt6) or avoid aborting a whole
    run because of one invalid geometry. Such an exception must not stop the
    plugin, but it must not vanish silently either: it is written to the QGIS
    message log, in the "QgisTreeBenefits" tab
    (View -> Panels -> Log Messages).

Nessuna informazione sensibile viene registrata: solo il contesto dell'
operazione, il tipo di eccezione e il suo messaggio.
"""

LOG_TAG = 'QgisTreeBenefits'


def message(text, level='info'):
    """Scrive una riga nel registro messaggi di QGIS.

    Restituisce True se la riga e' stata scritta, False se il registro non e'
    disponibile (per esempio quando i moduli sono usati fuori da QGIS, nei test).
    """
    try:
        from qgis.core import QgsMessageLog, Qgis
        levels = {'info': Qgis.MessageLevel.Info,
                  'warning': Qgis.MessageLevel.Warning,
                  'critical': Qgis.MessageLevel.Critical}
        QgsMessageLog.logMessage(str(text), LOG_TAG,
                                 levels.get(level, Qgis.MessageLevel.Info))
        return True
    except Exception:
        # Fuori da QGIS non esiste un registro: l'operazione chiamante prosegue.
        return False


def ignored(context, exc, level='info'):
    """Registra un'eccezione volutamente non bloccante e prosegue.

    context: breve descrizione dell'operazione tentata.
    exc:     l'eccezione intercettata.
    """
    return message('%s - %s: %s' % (context, type(exc).__name__, exc), level)

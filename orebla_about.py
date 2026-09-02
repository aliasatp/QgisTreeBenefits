# -*- coding: utf-8 -*-
"""
orebla_about.py - Testi informativi del plugin QgisTreeBenefits (IT/EN).
orebla_about.py - Informative texts of the QgisTreeBenefits plugin (IT/EN).

Disclaimer + sezione Info della versione web Orebla e guida rapida all'uso del
plugin. Usati nell'help degli algoritmi Processing e nelle schede Info/Guida
della finestra di stima benefici.
"""

from . import orebla_i18n as I18N

WEBAPP_URL = "https://map.aliaswebgis.it:5443/ARBoREOSIM/orebla.html"


# ====================================================================
#  ITALIANO
# ====================================================================

DISCLAIMER_HTML_IT = """
<h3 style="color:#b00;margin-bottom:4px;">&#9888; Uso dimostrativo</h3>
<p><b>Strumento di stima del valore dell'albero urbano.</b>
Questo strumento &egrave; fornito esclusivamente a scopo dimostrativo e didattico.
I risultati ottenuti <b>non costituiscono perizia, valutazione tecnica ufficiale
o documento con valore legale o commerciale</b>.</p>
<p>Il plugin riproduce i calcoli della piattaforma ARBOREO di ALIAS ATP.</p>
<p>Il calcolo del valore ornamentale ed ecologico &egrave; basato sul metodo
<b>Orebla</b> descritto nell'articolo a firma di <b>Luigi Sani</b>, pubblicato su
arborete.it. La stima di raffrescamento estivo e runoff evitato &egrave; elaborata
da <b>ALIAS ATP</b> &mdash; aliasinfo.it.</p>
"""

INFO_HTML_IT = """
<h3>Riferimento</h3>
<p>Il plugin riproduce in ambito QGIS i calcoli della piattaforma ARBOREO di ALIAS ATP.</p>

<h3>Metodo di calcolo &ndash; Valore ornamentale ed ecologico</h3>
<p>&#128196; <b>Metodo Orebla</b> &mdash; autore: <b>Luigi Sani</b></p>
<p>Il calcolo del valore ornamentale ed ecologico dell'albero combina parametri
biometrici (circonferenza, altezza, diametro chioma), condizioni fitosanitarie e
strutturali, posizione urbanistica e coerenza fitoclimatica per restituire un valore
monetario.</p>
<p><b>Nota sull'opzione avanzata:</b> il calcolo del valore ecologico in modalit&agrave;
avanzata &egrave; stato introdotto da <b>ALIAS ATP</b>: integra nella CO&#8322; stoccata
il contributo approssimato del settore branche, ridotto per un <i>fattore di
riduzione</i> (qualora indicato dall'utente o letto da un campo del layer).</p>
<p>&#128229; Articolo: <a href="https://arborete.it/download.html">arborete.it/download.html</a></p>

<h3>Metodo di calcolo &ndash; Raffrescamento e Runoff evitato</h3>
<p>&#127777; <b>Modelli di simulazione ambientale</b> &mdash; <b>ALIAS ATP</b></p>
<p>La stima del raffrescamento estivo (&Delta;T, energia risparmiata, CO&#8322;
evitata) e del runoff evitato (annuo e per evento estremo TR50) &egrave; elaborata
da ALIAS ATP. I modelli integrano parametri specie-specifici (LAI, IRU base,
gruppo funzionale), dati climatici locali e caratteristiche biometriche e
stazionali dell'albero.</p>
<p><b>Nota radiazione:</b> il campo <i>rad_globale_giu_ago</i> &egrave; la somma
dei tre mesi estivi in MJ/m&sup2; (valori tipici Italia: 1800&ndash;2400 MJ/m&sup2;).</p>
<p>&#127760; <a href="https://aliasinfo.it">aliasinfo.it</a></p>

<h3>Fonti dati</h3>
<p><b>Libreria specie del plugin:</b> 261 specie arboree con parametri LAI, CRC,
IRU base (specie, urbano compatto, urbano aperto) e gruppo funzionale.</p>
<p><b>Province italiane:</b> 107 province con fascia fitoclimatica Pavari e valori
massimi Orebla (valmax) per il calcolo del valore ornamentale.</p>

<h3>Uso fuori dall'Italia</h3>
<p>Nell'elenco delle province, in prima posizione, &egrave; disponibile la voce
generica <b>&laquo;Media Italia (uso extra-Italia)&raquo;</b> &mdash; sigla
<code>ZZ</code>. Il suo <i>valmax</i> &egrave; la <b>media aritmetica</b> dei valori
massimi delle 107 province italiane (112.399,79 &euro;) e serve a chi lavora fuori
dall'Italia e non dispone di un valore massimo di riferimento locale.</p>
<p>Tutti gli altri moduli (ecologico, runoff, raffrescamento, CO&#8322; avanzata,
mobilit&agrave;) non contengono parametri specifici dell'Italia: funzionano
ovunque, purch&eacute; si inseriscano i <b>dati climatici locali</b>. La latitudine
&egrave; letta automaticamente dalla geometria del punto e il CRS di output UTM
viene proposto secondo il fuso reale del layer, in entrambi gli emisferi.</p>
"""

HELP_HTML_IT = """
<h3>Guida rapida all'uso del plugin</h3>
<p>Il plugin <b>QgisTreeBenefits</b> mette a disposizione due algoritmi nella
<i>Cassetta degli strumenti di Processing &rarr; QgisTreeBenefits</i> e una
finestra a schede per la stima benefici (menu <i>Plugin &rarr; QgisTreeBenefits</i>).</p>
<ol>
<li><b>1 &middot; Crea inventario alberi (layer vuoto)</b> &mdash; crea un layer di
punti con tutti i campi-parametro, organizzato in <i>schede</i> (Dati base /
avanzati / climatici) e con i <i>menu a tendina</i> con le voci della libreria del
plugin. Entra in editing e digitalizza gli alberi.</li>
<li><b>2 &middot; Importa/adatta layer esistente</b> &mdash; trasforma un tuo layer
di alberi in uno compatibile: abbina le specie alla <i>libreria del plugin</i> (per
nome pi&ugrave; simile), mappa i dati biometrici e crea un layer gi&agrave; a
schede/tendine con specie e biometria precompilate; gli altri parametri si
completano con lo stesso schema.</li>
<li><b>3 &middot; Stima benefici</b> &mdash; il calcolo, nella <i>finestra a schede</i>
(menu Plugin): Dati base / avanzati / climatici / Opzioni &amp; Output. I dati
climatici possono arrivare dal layer oppure essere inseriti come <i>valore fisso</i>
per tutti gli alberi.</li>
</ol>
<p><b>Flusso consigliato:</b> crea/importa l'inventario &rarr; completa i parametri
&rarr; esegui la stima benefici.</p>
<p><b>Lingua:</b> l'interfaccia &egrave; disponibile in <b>italiano</b> e
<b>inglese</b>. Si cambia dal selettore in alto nella finestra di stima, oppure dal
menu <i>Plugin &rarr; QgisTreeBenefits &rarr; Lingua / Language</i>. Cambiano solo
le <i>etichette</i>: i <b>nomi dei campi</b> e i <b>valori memorizzati</b> restano
gli stessi, quindi un inventario creato in una lingua si calcola correttamente
anche nell'altra.</p>
<p><b>Fattore di riduzione</b> (per la CO&#8322; avanzata): pu&ograve; essere scelto
come valore predefinito oppure prelevato da un campo del layer alberi.</p>
<p><b>Output in UTM:</b> i risultati sono riproiettati nel CRS UTM scelto (in metri),
cos&igrave; <i>ob_rinf</i> (raggio) e <i>ob_area</i> sono usabili per buffer.
Spuntando l'opzione si generano i poligoni delle <b>aree di influenza</b>.</p>
<p><b>Campi di output</b> (prefisso <code>ob_</code>): valore ecologico
(CO&#8322; stoccata/sequestrata, O&#8322;, inquinanti, &euro;), valore ornamentale,
valore globale, runoff annuo/evento, raffrescamento (&Delta;T, kWh, CO&#8322;,
&euro;, area/raggio influenza, &Delta;T per direzione) e, se attivati, CO&#8322;
avanzata e mobilit&agrave;.</p>
<p><b>Specie:</b> id o nome (anche parziale). <b>Provincia:</b> sigla o nome; fuori
dall'Italia usa la voce <b>&laquo;Media Italia (uso extra-Italia)&raquo;</b>
(sigla <code>ZZ</code>). <b>Latitudine:</b> ricavata automaticamente dalla geometria
del punto.</p>
"""

VERSION_HTML_IT = """
<hr>
<p style="color:#666;font-size:11px;">QgisTreeBenefits &middot; elaborazione
<b>ALIAS ATP</b> &middot; <a href="https://aliasinfo.it">aliasinfo.it</a>
&middot; alias@aliasinfo.it &middot; &copy; 2026</p>
"""


# ====================================================================
#  ENGLISH
# ====================================================================

DISCLAIMER_HTML_EN = """
<h3 style="color:#b00;margin-bottom:4px;">&#9888; Demonstration use only</h3>
<p><b>Urban tree value assessment tool.</b>
This tool is provided for demonstration and teaching purposes only. Its results
<b>do not constitute an expert appraisal, an official technical assessment, or a
document with legal or commercial standing</b>.</p>
<p>The plugin reproduces the calculations of the ARBOREO platform by ALIAS ATP.</p>
<p>The amenity and ecological value calculation follows the <b>Orebla</b> method
described in the article by <b>Luigi Sani</b>, published on arborete.it. The
summer cooling and avoided runoff estimates are developed by <b>ALIAS ATP</b>
&mdash; aliasinfo.it.</p>
"""

INFO_HTML_EN = """
<h3>Reference</h3>
<p>The plugin reproduces inside QGIS the calculations of the ARBOREO platform by
ALIAS ATP.</p>

<h3>Method &ndash; Amenity and ecological value</h3>
<p>&#128196; <b>Orebla method</b> &mdash; author: <b>Luigi Sani</b></p>
<p>The amenity and ecological value of a tree is derived from biometric
parameters (girth, height, crown diameter), health and structural condition,
urban setting and phytoclimatic suitability, returning a monetary value.</p>
<p><b>Note on the advanced option:</b> the advanced ecological value was
introduced by <b>ALIAS ATP</b>: it adds to the stored CO&#8322; an approximate
contribution from the branch compartment, lowered by a <i>reduction factor</i>
(set by the user or read from a layer field).</p>
<p>&#128229; Article: <a href="https://arborete.it/download.html">arborete.it/download.html</a></p>

<h3>Method &ndash; Cooling and avoided runoff</h3>
<p>&#127777; <b>Environmental simulation models</b> &mdash; <b>ALIAS ATP</b></p>
<p>The summer cooling estimate (&Delta;T, energy saved, CO&#8322; avoided) and the
avoided runoff (annual and for an extreme TR50 event) are developed by ALIAS ATP.
The models combine species-specific parameters (LAI, base IRU, functional group),
local climate data and the biometric and site characteristics of the tree.</p>
<p><b>Radiation note:</b> the field <i>rad_globale_giu_ago</i> is the sum over the
three warmest months in MJ/m&sup2;. In the northern hemisphere this is normally
June&ndash;August; <b>in the southern hemisphere use December&ndash;February</b>.
The same applies to the other "warm-season" climate fields. Typical values in
Italy are 1800&ndash;2400 MJ/m&sup2;; use your own local figures.</p>
<p>&#127760; <a href="https://aliasinfo.it">aliasinfo.it</a></p>

<h3>Data sources</h3>
<p><b>Species library:</b> 261 tree species with LAI, CRC, base IRU (species,
compact urban, open urban) and functional group. Botanical and common names are
kept as in the original dataset and are not translated.</p>
<p><b>Italian provinces:</b> 107 provinces with Pavari phytoclimatic belt and
Orebla maximum values (valmax) used for the amenity value.</p>

<h3>Use outside Italy</h3>
<p>The first entry of the province list is the generic
<b>&laquo;Italy average (non-Italian use)&raquo;</b> &mdash; code <code>ZZ</code>.
Its <i>valmax</i> is the <b>arithmetic mean</b> of the maximum values of the 107
Italian provinces (EUR 112,399.79) and is intended for users working outside Italy
who have no local reference maximum. The amenity value is then computed on an
average Italian basis with the same RAM logistic curve; treat it as an order of
magnitude, and where a national or local reference value exists, prefer it.</p>
<p>All the other modules (ecological, runoff, cooling, advanced CO&#8322;,
mobility) contain no Italy-specific parameters: they work anywhere, provided you
enter <b>local climate data</b>. Latitude is read automatically from the point
geometry and the suggested UTM output CRS follows the actual zone of the layer, in
both hemispheres.</p>
<p><b>Monetary unit:</b> all monetary results are expressed in EUR, since the
underlying reference values and the unit costs used (energy, water) are European.
Convert them afterwards if you need another currency.</p>
"""

HELP_HTML_EN = """
<h3>Quick start</h3>
<p><b>QgisTreeBenefits</b> provides two algorithms in the <i>Processing Toolbox
&rarr; QgisTreeBenefits</i> and a tabbed window for the benefit assessment
(<i>Plugins &rarr; QgisTreeBenefits</i> menu).</p>
<ol>
<li><b>1 &middot; Create tree inventory (empty layer)</b> &mdash; creates a point
layer with all the parameter fields, organised in <i>tabs</i> (Basic / Advanced /
Climate data) and with <i>drop-down menus</i> holding the plugin library entries.
Start editing and digitise your trees.</li>
<li><b>2 &middot; Import/adapt an existing layer</b> &mdash; converts your own tree
layer into a compatible one: species are matched against the <i>plugin library</i>
by closest name, the biometric fields you map are copied, and the result is
already tabbed with drop-downs and pre-filled species and biometry; the remaining
parameters are completed in the same form.</li>
<li><b>3 &middot; Benefit assessment</b> &mdash; the calculation itself, in the
<i>tabbed window</i> (Plugins menu): Basic / Advanced / Climate data / Options &amp;
Output. Climate data can come from the layer or be entered once as a
<i>fixed value</i> for every tree.</li>
</ol>
<p><b>Suggested workflow:</b> create or import the inventory &rarr; complete the
parameters &rarr; run the benefit assessment.</p>
<p><b>Language:</b> the interface is available in <b>Italian</b> and <b>English</b>.
Switch it from the selector at the top of the assessment window, or from
<i>Plugins &rarr; QgisTreeBenefits &rarr; Language</i>. Only the <i>labels</i>
change: <b>field names</b> and <b>stored values</b> stay identical, so an inventory
built in one language computes correctly in the other and projects remain fully
interchangeable.</p>
<p><b>Reduction factor</b> (for the advanced CO&#8322;): either chosen as a default
value or read from a field of the tree layer.</p>
<p><b>UTM output:</b> results are reprojected into the chosen UTM CRS (in metres),
so <i>ob_rinf</i> (radius) and <i>ob_area</i> can be used directly for buffers.
Ticking the option also produces the <b>areas of influence</b> polygons.</p>
<p><b>Output fields</b> (prefix <code>ob_</code>): ecological value (stored and
sequestered CO&#8322;, O&#8322;, pollutants, EUR), amenity value, total value,
annual and event runoff, cooling (&Delta;T, kWh, CO&#8322;, EUR, area/radius of
influence, &Delta;T per direction) and, when enabled, advanced CO&#8322; and
mobility.</p>
<p><b>Species:</b> id or name (partial names accepted). <b>Reference area:</b> an
Italian province code or name; outside Italy use
<b>&laquo;Italy average (non-Italian use)&raquo;</b> (code <code>ZZ</code>).
<b>Latitude:</b> taken automatically from the point geometry.</p>
<p><b>Southern hemisphere:</b> enter the summer climate fields for your own warm
season (December&ndash;February) rather than June&ndash;August.</p>
"""

VERSION_HTML_EN = VERSION_HTML_IT


# ====================================================================
#  ACCESSO / ACCESSORS
# ====================================================================

_BLOCKS = {
    'disclaimer': {'it': DISCLAIMER_HTML_IT, 'en': DISCLAIMER_HTML_EN},
    'info': {'it': INFO_HTML_IT, 'en': INFO_HTML_EN},
    'help': {'it': HELP_HTML_IT, 'en': HELP_HTML_EN},
    'version': {'it': VERSION_HTML_IT, 'en': VERSION_HTML_EN},
}


def block(name, lang=None):
    lang = I18N.lang_or_current(lang)
    b = _BLOCKS.get(name, {})
    return b.get(lang) or b.get('it') or ''


def _wrap(*parts):
    return ("<div style='font-family:sans-serif;font-size:12px;'>" + ''.join(parts) + "</div>")


def about_info_html(lang=None):
    """Disclaimer + sezione informativa."""
    return _wrap(block('disclaimer', lang), "<hr>", block('info', lang),
                 block('version', lang))


def about_help_html(lang=None):
    """Guida rapida all'uso del plugin."""
    return _wrap(block('help', lang), block('version', lang))


def about_html(lang=None):
    """Testo completo (per il pannello Guida degli algoritmi Processing)."""
    return _wrap(block('disclaimer', lang), "<hr>", block('help', lang), "<hr>",
                 block('info', lang), block('version', lang))

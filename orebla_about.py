# -*- coding: utf-8 -*-
"""
orebla_about.py - Testi informativi del plugin QgisTreeBenefits.

Disclaimer + sezione Info della versione web Orebla e guida rapida all'uso del
plugin. Usati nell'help degli algoritmi Processing e nelle schede Info/Guida
della finestra di stima benefici.
"""

WEBAPP_URL = "https://map.aliaswebgis.it:5443/ARBoREOSIM/orebla.html"
WEBAPP_REF = ('la versione web Orebla, creata da <b>ALIAS ATP</b> '
              '(<a href="%s">%s</a>)' % (WEBAPP_URL, WEBAPP_URL))

DISCLAIMER_HTML = """
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

INFO_HTML = """
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
giugno&ndash;agosto in MJ/m&sup2; (valori tipici Italia: 1800&ndash;2400 MJ/m&sup2;).</p>
<p>&#127760; <a href="https://aliasinfo.it">aliasinfo.it</a></p>

<h3>Fonti dati</h3>
<p><b>Libreria specie del plugin:</b> 261 specie arboree con parametri LAI, CRC,
IRU base (specie, urbano compatto, urbano aperto) e gruppo funzionale.</p>
<p><b>Province italiane:</b> 107 province con fascia fitoclimatica Pavari e valori
massimi Orebla (valmax) per il calcolo del valore ornamentale.</p>
"""

HELP_HTML = """
<h3>Guida rapida all'uso del plugin</h3>
<p>Il plugin <b>QgisTreeBenefits</b> mette a disposizione tre algoritmi nella
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
<li><b>3 &middot; Stima benefici</b> &mdash; il calcolo. Per una compilazione comoda
usa la <i>finestra a schede</i> (menu Plugin): Dati base / avanzati / climatici /
Opzioni &amp; Output. I dati climatici possono arrivare dal layer oppure essere
inseriti come <i>valore fisso</i> per tutti gli alberi. La stessa funzione &egrave;
disponibile come algoritmo Processing per il batch.</li>
</ol>
<p><b>Flusso consigliato:</b> crea/importa l'inventario &rarr; completa i parametri
&rarr; esegui la stima benefici.</p>
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
<p><b>Specie:</b> id o nome (anche parziale). <b>Provincia:</b> sigla o nome
(serve per il valore ornamentale). <b>Latitudine:</b> ricavata automaticamente
dalla geometria del punto.</p>
"""

VERSION_HTML = """
<hr>
<p style="color:#666;font-size:11px;">QgisTreeBenefits &middot; elaborazione
<b>ALIAS ATP</b> &middot; <a href="https://aliasinfo.it">aliasinfo.it</a>
&middot; alias@aliasinfo.it &middot; &copy; 2026</p>
"""


def _wrap(*parts):
    return ("<div style='font-family:sans-serif;font-size:12px;'>"
            + ''.join(parts) + "</div>")


def about_info_html():
    """Disclaimer + sezione informativa."""
    return _wrap(DISCLAIMER_HTML, "<hr>", INFO_HTML, VERSION_HTML)


def about_help_html():
    """Guida rapida all'uso del plugin."""
    return _wrap(HELP_HTML, VERSION_HTML)


def about_html():
    """Testo completo (per il pannello Guida degli algoritmi Processing)."""
    return _wrap(DISCLAIMER_HTML, "<hr>", HELP_HTML, "<hr>", INFO_HTML, VERSION_HTML)

# -*- coding: utf-8 -*-
"""Orebla Tree Benefits - plugin Processing per QGIS (IT/EN)."""


def classFactory(iface):
    from .orebla_plugin import OreblaPlugin
    return OreblaPlugin(iface)

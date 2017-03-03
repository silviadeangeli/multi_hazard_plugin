# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MultiHazardRisk
                                 A QGIS plugin
 This plugin allows the user to analyse temporal and spatial overlapping of multiple hazards on exposed elements and perform multi-hazard impact assessments
                             -------------------
        begin                : 2017-03-03
        copyright            : (C) 2017 by Silvia De Angeli
        email                : silviadeangeli@gmx.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MultiHazardRisk class from file MultiHazardRisk.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .multi_hazard_risk import MultiHazardRisk
    return MultiHazardRisk(iface)

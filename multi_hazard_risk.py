# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MultiHazardRisk
                                 A QGIS plugin
 This plugin allows the user to analyse temporal and spatial overlapping of multiple hazards on exposed elements and perform multi-hazard impact assessments
                              -------------------
        begin                : 2017-03-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Silvia De Angeli
        email                : silviadeangeli@gmx.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QDialog, QLineEdit, QFileDialog
from qgis.core import QgsMessageLog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from multi_hazard_risk_dialog import MultiHazardRiskDialog
import os.path
# Import hazards list
from hazards import hazards_list, forcings
# Import GDAL for raster calculation
from osgeo import gdal
import sys
from functools import partial
import Tkinter as tk
from show_results import ShowResults
from matplotlib.figure import Figure

import numpy as np
from PyQt4 import QtGui

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from data_plotter import create_rectangle, define_color, obtain_raster_values, make_plot
from click_for_coordinates import PointTool
from qgis.core import *
from qgis.utils import *
from qgis.gui import *



class MultiHazardRisk:
    """QGIS Plugin Implementation."""
    filePath = None

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MultiHazardRisk_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Multi Hazard Risk')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MultiHazardRisk')
        self.toolbar.setObjectName(u'MultiHazardRisk')

        self.dialog_instance = ShowResults()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MultiHazardRisk', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = MultiHazardRiskDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MultiHazardRisk/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Multi Hazard Risk'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def bandlist(self, rasterpath, widget):
        raster = gdal.Open(rasterpath)
        bands_list = []
        for band in range(raster.RasterCount):
            band += 1
            rasterband = raster.GetRasterBand(band)
            bands_list.append(str(rasterband.GetBand()))
            if rasterband is None:
                continue
        widget.addItems(bands_list)

    def single_browse(self, widget, widget2, widget3, widget4, ext):
        self.filePath = QFileDialog.getOpenFileName(None, 'Select file to open','~/Desktop', ext)
        widget.setPlainText(self.filePath)
        raster = gdal.Open(self.filePath)
        bands_list = []
        for band in range(raster.RasterCount):
            band += 1
            rasterband = raster.GetRasterBand(band)
            bands_list.append(str(rasterband.GetBand()))
            if rasterband is None:
                continue
        widget2.addItems(bands_list)
        widget2.setCurrentIndex(-1)
        widget3.addItems(bands_list)
        widget3.setCurrentIndex(-1)
        widget4.addItems(bands_list)
        widget4.setCurrentIndex(-1)

    def coord(self):
        self.tool_identify = PointTool(iface.mapCanvas(), self.m1, self.t1, self.d1, self.path1, self.m2, self.t2, self.d2, self.path2, self.layer1_name, self.layer2_name)
        iface.mapCanvas().setMapTool(self.tool_identify)

    def add_layer(self, path, name_costumize):
        fileName = path
        fileInfo = QFileInfo(fileName)
        name = fileInfo.baseName()
        iface.addRasterLayer(path, name + "_" + name_costumize)

    def add_forcings(self,box_forcings, box_hazards):
        box_forcings.clear()
        box_forcings.addItems(forcings[str(box_hazards.currentText())])
        box_forcings.setCurrentIndex(-1)

    def compute(self):

        self.m1 = self.dlg.magnitude1.currentText()
        self.t1 = self.dlg.time1.currentText()
        self.d1 = self.dlg.duration1.currentText()

        self.m2 = self.dlg.magnitude2.currentText()
        self.t2 = self.dlg.time2.currentText()
        self.d2 = self.dlg.duration2.currentText()

        self.path1 = self.dlg.textBrowser1.toPlainText()
        self.path2 = self.dlg.textBrowser2.toPlainText()

        self.layer1_name = self.dlg.hazardtype1.currentText()
        self.layer2_name = self.dlg.hazardtype2.currentText()

        self.add_layer(self.path1, self.layer1_name)
        self.add_layer(self.path2, self.layer2_name)

        self.dlg.close()
        self.dialog_instance.exec_()

        pass

    def run(self):
        """Run method that performs all the real work"""

        #layers = self.iface.legendInterface().layers()
        #layer_list = []
        #for layer in layers:
        #layer_list.append(layer.name())
        #self.dlg.layer1.addItems(layer_list)

        self.dlg.hazardtype1.clear()
        self.dlg.hazardtype1.addItems(hazards_list)
        self.dlg.hazardtype1.setCurrentIndex(-1)
        self.dlg.hazardtype2.clear()
        self.dlg.hazardtype2.addItems(hazards_list)
        self.dlg.hazardtype2.setCurrentIndex(-1)

        #Browser button for h1
    	self.dlg.browse1.clicked.connect(partial(self.single_browse, widget=self.dlg.textBrowser1, widget2=self.dlg.magnitude1, widget3=self.dlg.duration1, widget4=self.dlg.time1, ext='*.tif'))
        self.dlg.update()

        #Browser button for h2
        self.dlg.browse2.clicked.connect(partial(self.single_browse, widget=self.dlg.textBrowser2, widget2=self.dlg.magnitude2, widget3=self.dlg.duration2, widget4=self.dlg.time2, ext='*.tif'))
        self.dlg.update()


        #Browser button for exposure
        #self.dlg.browseE1.clicked.connect(partial(self.single_browse, widget=self.dlg.textBrowserE1, ext='*.shp'))
        #self.dlg.update()

        #while self.dlg.magnitude1.currentText() == "":
            #self.dlg.button_box.setEnabled(False)

        self.dlg.button_box.clicked.connect(self.compute)

        self.dialog_instance.button_box2.clicked.connect(self.coord)

        self.dlg.connect(self.dlg.hazardtype1, SIGNAL("currentIndexChanged(const QString&)"),
                         partial(self.add_forcings, box_forcings=self.dlg.hazardparam1,
                                 box_hazards=self.dlg.hazardtype1))

        self.dlg.connect(self.dlg.hazardtype2, SIGNAL("currentIndexChanged(const QString&)"),
                         partial(self.add_forcings, box_forcings=self.dlg.hazardparam2,
                                 box_hazards=self.dlg.hazardtype2))
		
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


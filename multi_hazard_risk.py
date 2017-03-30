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
from PyQt4.QtGui import QAction, QIcon, QDialog, QLineEdit, QFileDialog, QMessageBox
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
from hazard_structure import hazard


class MultiHazardRisk:
    """QGIS Plugin Implementation."""
    filePath = None
    hazards = []
    message_list = []
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
        self.tool_identify = PointTool(iface.mapCanvas(), self.hazards)
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

    def add_message(self,text,title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()

    def store_values(self):

        #Stores the values contained in the GUI

        m1 = self.dlg.magnitude1.currentText()
        t1 = self.dlg.time1.currentText()
        d1 = self.dlg.duration1.currentText()

        m2 = self.dlg.magnitude2.currentText()
        t2 = self.dlg.time2.currentText()
        d2 = self.dlg.duration2.currentText()

        path1 = self.dlg.textBrowser1.toPlainText()
        path2 = self.dlg.textBrowser2.toPlainText()

        hazard_type1 = self.dlg.hazardtype1.currentText()
        hazard_type2 = self.dlg.hazardtype2.currentText()

        hazard_forcing1 = self.dlg.hazardparam1.currentText()
        hazard_forcing2 = self.dlg.hazardparam2.currentText()

        hazard_1 = hazard(m1, t1, d1, path1, hazard_type1, hazard_forcing1)
        hazard_2 = hazard(m2, t2, d2, path2, hazard_type2, hazard_forcing2)
        if hazard_1.path != "":
            self.hazards.append(hazard_1)
            self.message_list.append(hazard_1.name + " as " + hazard_1.hazard_type)
        if hazard_2.path != "":
            self.hazards.append(hazard_2)
            self.message_list.append(hazard_2.name + " as " + hazard_2.hazard_type)

        self.add_message('The following layers have been saved up to now:' + str(self.message_list), title = 'Hazards upload')


        #Cleans the GUI to insert new hazards

        self.dlg.magnitude1.setCurrentIndex(-1)
        self.dlg.time1.setCurrentIndex(-1)
        self.dlg.duration1.setCurrentIndex(-1)

        self.dlg.magnitude2.setCurrentIndex(-1)
        self.dlg.time2.setCurrentIndex(-1)
        self.dlg.duration2.setCurrentIndex(-1)

        self.dlg.textBrowser1.clear()
        self.dlg.textBrowser2.clear()

        self.dlg.hazardtype1.setCurrentIndex(-1)
        self.dlg.hazardtype2.setCurrentIndex(-1)

        self.dlg.hazardparam1.setCurrentIndex(-1)
        self.dlg.hazardparam2.setCurrentIndex(-1)

        for hazard_i in self.hazards:
            hazard_i.print_debug()

    def compute(self):
        for hazard_i in self.hazards:
            self.add_layer(hazard_i.path, hazard_i.hazard_type)

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


        self.dlg.button_box.accepted.connect(self.compute)

        self.dialog_instance.button_box2.clicked.connect(self.coord)

        self.dlg.connect(self.dlg.hazardtype1, SIGNAL("currentIndexChanged(const QString&)"),
                         partial(self.add_forcings, box_forcings=self.dlg.hazardparam1,
                                 box_hazards=self.dlg.hazardtype1))

        self.dlg.connect(self.dlg.hazardtype2, SIGNAL("currentIndexChanged(const QString&)"),
                         partial(self.add_forcings, box_forcings=self.dlg.hazardparam2,
                                 box_hazards=self.dlg.hazardtype2))

        self.dlg.save_hazards.clicked.connect(self.store_values)
        self.dlg.save_hazards.clicked.connect(partial(self.add_message, text= ('The following layers have been saved up to now:'+ str(self.message_list)), title='Hazards upload'))


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


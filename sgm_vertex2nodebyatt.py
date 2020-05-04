# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmVertex2NodeByAtt
    * Plugin type:   QGIS 3 plugin
    * Module:        Main
    * Description:   Modify the placement of the vertices (the start-point and
    *                the end-point) of lines to put them at the placement  
    *                of 2 node objects, thanks to 1 attribute of the line
    *                that contains the 2 ids of the 2 nodes objects, with
    *                a separator.
    *                For example:
    *                   - the layer LINES has an attribute named REGIDS
    *                   - the layer NODES has an attribute named PTID
    *                   - a LINES object has the value 'R1-R2' for REGIDS
    *                   - a NODES object has the value 'R1' for PTID
    *                   - another NODES object has the value 'R2' for PTID
    *                   - then the result is:
    *                       1) the start-point of the LINES object is moved
    *                          to the first NODES object position
    *                       2) the end-point of the LINES object is moved
    *                          to the second NODES object position
    *                       3) the reverse is possible (the NODES objects
    *                          are moved to the position of the start and
    *                          end points of the LINES object)
    * Specific lib:  None
    * First release: 2017-05-11
    * Last release:  2020-04-30
    * Copyright:     (C)2020 SIGMOE
    * Email:         em at sigmoe.fr
    * License:       GPL v3
    ***************************************************************************
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program. If not, see <http://www.gnu.org/licenses/>.
    ***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject
from qgis.utils import iface

import os

from .sgm_vertex2nodebyatt_tr import *
from . import sgm_vertex2nodebyatt_rsc

class SgmVertex2NodeByAtt:
    
    # Initialisation
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SgmVertex2NodeByAtt_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
            
        self.settings = QSettings()
        self.sgm_menu = None
        self.vtx_nodes_tr = None
        
        # Global texts
        self.mnu_title_txt = self.tr("SIGMOE")
        self.fnc_title_txt = self.tr("Moves lines to points by attribute")
        self.err_title_txt = self.tr("Process stopped")
        self.end_txt = self.tr("Move completed")
        self.err_noedit_txt = self.tr("Layer %s is not editable")
        self.err_noatt_txt = self.tr("Field %s is not usable")
        self.gbl_text = [self.fnc_title_txt, self.err_title_txt, self.end_txt, self.err_noedit_txt, self.err_noatt_txt]
    
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SgmVertex2NodeByAtt', message)

    # Function to add menus
    def sgm_add_submenu(self, submenu):
        if self.sgm_menu != None:
            self.sgm_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&Sigmoe", submenu.menuAction())
            
    # Initialisation of the menu and the toolbar
    def initGui(self):
        # Add Sigmoe to QGIS menu
        self.sgm_menu = QMenu(QCoreApplication.translate("SigmoeVtxto2NdByatt", self.mnu_title_txt))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.sgm_menu)
        
        # Add Sigmoe toolbar
        self.toolbar = self.iface.addToolBar(self.mnu_title_txt)
        self.toolbar.setObjectName("SigmoeVtxto2NdByattTB")
        
        # Create actions
        icon = QIcon(r":/icons/sgm_vtx2ndbatt")
        self.transfo_action = QAction(icon, self.fnc_title_txt, self.iface.mainWindow())
               
        # Add actions to the toolbar
        self.toolbar.addActions([self.transfo_action])
        
        # Add actions to the menu
        self.sgm_menu.addActions([self.transfo_action])
        
        # Manage signals
        self.transfo_action.triggered.connect(self.transfo)
                
    # Unload actions
    def unload(self):
        if self.sgm_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.sgm_menu.menuAction())
            self.sgm_menu.deleteLater()
            self.iface.mainWindow().removeToolBar(self.toolbar)
        else:
            self.iface.removePluginMenu("&SigmoeVtxto2NdByatt", self.sgm_menu.menuAction())
            self.sgm_menu.deleteLater()
        
    # Main function
    def transfo(self):
        '''
            Launch the transformation with the possibility of setting the parameters
        '''
        self.vtx_nodes_tr = Vertex2NodeByAttTr (
                                self.iface,
                                self.canvas,
                                self.project,
                                self.plugin_dir,
                                self.gbl_text
                                )
        self.vtx_nodes_tr.vtx_nodes_modify()


        

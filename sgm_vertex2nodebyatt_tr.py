# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmVertex2NodeByAtt
    * Plugin type:   QGIS 3 plugin
    * Module:        Classes to do the job
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
    * Last release:  2020-05-07
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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal, QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtWidgets import QMessageBox, QWidget
from qgis.core import QgsWkbTypes, QgsRectangle, QgsFeatureRequest, QgsMapLayer, QgsMessageLog
from qgis.utils import iface

import os
import json
import codecs
import locale

gui_dlg_vtnbaparams, _ = uic.loadUiType(
        os.path.join(os.path.dirname(__file__), r"gui/sgm_vertex2nodebyatt_dlgparams.ui"))

class Vertex2NodeByAttTr :
    
    # Initialisation
    def __init__(self, iface, canvas, project, plugin_dir, gbl_text):
        self.iface = iface
        self.canvas = canvas
        self.project = project
        self.plugin_dir = plugin_dir
            
        # Global texts
        self.fnc_title_txt = gbl_text[0]
        self.err_title_txt = gbl_text[1]
        self.end_txt = gbl_text[2]
        self.err_noedit_txt = gbl_text[3]
        self.err_noatt_txt = gbl_text[4]

    # Do the modifications of the objects
    def vtx_nodes_modify(self) :
        # Prepare the parameters window
        self.nw_vtx_nodes_params = ParamVtxNodes(self.project, self.plugin_dir)
        # Capture the dic of parameters when closing the dlg window
        self.nw_vtx_nodes_params.send_nw_params.connect(self.ok_param) 
        # Modal window
        self.nw_vtx_nodes_params.setWindowModality(Qt.ApplicationModal)
        # Show the parameters window
        self.nw_vtx_nodes_params.show()
            
    # Launch the process of modification once the param window is validated
    def ok_param(self, dic_param):
        
        # To avoid problem of layer names not found
        try:
            # Find the layer objects
            lyr_lines = self.project.mapLayersByName(dic_param["lin_lyr"])[0]
            lyr_nodes = self.project.mapLayersByName(dic_param["nod_lyr"])[0]
            # Start editing line or node layer
            if dic_param["move_mode"] == 0:
                if not lyr_lines.startEditing():
                    QMessageBox.information(
                        self.iface.mainWindow(), 
                        self.err_title_txt, 
                        self.err_noedit_txt 
                        % (dic_param["lin_lyr"]))
                    return
            else:
                if not lyr_nodes.startEditing():
                    QMessageBox.information(
                        self.iface.mainWindow(), 
                        self.err_title_txt, 
                        self.err_noedit_txt
                        % (dic_param["nod_lyr"]))
                    return
            # Reviews all the line objects
            for lin_obj in lyr_lines.getFeatures():
                # Find the node references in the line object
                # Only the 2 first references are processed
                try:
                    val_attsnode = lin_obj[dic_param["lin_att1"]].split(dic_param["lin_att_sep"])
                except: 
                    QMessageBox.information(
                        self.iface.mainWindow(), 
                        self.err_title_txt, 
                        self.err_noatt_txt 
                        % (dic_param["lin_att1"]))
                    break
                # Check if 2 point numbers found
                if len(val_attsnode) > 1:
                    # Reviews all the node objects
                    for node_obj in lyr_nodes.getFeatures():
                        if node_obj[dic_param["nod_att"]] == val_attsnode[0]:
                            # The first vertex of the line is moved to the position of the node
                            if dic_param["move_mode"] == 0:
                                node_geom = node_obj.geometry().asPoint()
                                lyr_lines.moveVertex(node_geom.x(), node_geom.y(), lin_obj.id(), 0)
                            # The node is moved to the position of the first vertex of the line 
                            else:
                                line_geom = lin_obj.geometry()
                                line_geom.convertToSingleType()
                                line_geompl = line_geom.asPolyline()
                                node_geom = node_obj.geometry()
                                lyr_nodes.moveVertex(line_geompl[0][0], line_geompl[0][1], node_obj.id(), 0)
                        if node_obj[dic_param["nod_att"]] == val_attsnode[1]:
                            line_geom = lin_obj.geometry()
                            line_geom.convertToSingleType()
                            line_geompl = line_geom.asPolyline()
                            # The last vertex of the line is moved to the position of the node
                            if dic_param["move_mode"] == 0:
                                last_vtx = len(line_geompl) - 1
                                node_geom = node_obj.geometry().asPoint()
                                lyr_lines.moveVertex(node_geom.x(), node_geom.y(), lin_obj.id(), last_vtx)
                            # The node is moved to the position of the last vertex of the line
                            else:
                                last_vtx = len(line_geompl) - 1
                                node_geom = node_obj.geometry()
                                lyr_nodes.moveVertex(line_geompl[last_vtx][0], line_geompl[last_vtx][1], node_obj.id(), 0)
            # Validate the modification of the line or the node layer
            if dic_param["move_mode"] == 0:
                lyr_lines.commitChanges()
            else:
                lyr_nodes.commitChanges()
            # Refresh the canvas
            self.canvas.refresh()
        except:
            pass
        # End message
        QMessageBox.information(self.iface.mainWindow(), self.fnc_title_txt, self.end_txt)
        
# Manage the window of parameters
class ParamVtxNodes(QWidget, gui_dlg_vtnbaparams):

    send_nw_params = pyqtSignal(dict)
    
    # Initialization
    def __init__(self, project, plugin_dir, parent=None):
        super(ParamVtxNodes, self).__init__(parent)
        self.setupUi(self)
        self.project = project
        self.plugin_dir = plugin_dir
        # Initialization of the closing method (False = quit by red cross)
        self.quitValid = False
        self.params = {}
        # Connections
        self.validButt.clicked.connect(self.butt_ok)
        self.lineLyrCmb.currentIndexChanged.connect(self.populate_line_att)
        self.nodeLyrCmb.currentIndexChanged.connect(self.populate_node_att)
        # Delete Widget on close event
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Load the original parameters
        try:
            self.params_path = os.path.join(self.plugin_dir, r"sgm_vertex2nodebyatt_params.json")
        except IOError as error:
            raise error
        with codecs.open(self.params_path, encoding='utf-8', mode='r') as json_file:
            self.json_params = json.load(json_file)
            self.old_params = self.json_params[r"vtx2nds_params"]
        # Populate lineLyrCmb
        self.populate_lyrcmb(self.lineLyrCmb, [QgsWkbTypes.LineGeometry], "lin_lyr")
        # Populate nodeLyrCmb
        self.populate_lyrcmb(self.nodeLyrCmb, [QgsWkbTypes.PointGeometry], "nod_lyr")
        # Populate lineAttSepLe
        sep_txt = self.old_params["lin_att_sep"]
        self.lineAttSepLe.setText(sep_txt)
        # Populate modeRadio
        if self.old_params["move_mode"] == 0:
            self.modeRadio1.setChecked(True)
        else:
            self.modeRadio2.setChecked(True)
            
    # Populate lineAttCmb
    def populate_line_att(self):
        self.populate_flds(self.lineLyrCmb, self.lineAttCmb, "lin_att1")
    
    # Populate nodeAttCmb
    def populate_node_att(self):
        self.populate_flds(self.nodeLyrCmb, self.nodeAttCmb, "nod_att")
        
    # Close the window when clicking on the OK button
    def butt_ok(self):
        self.quitValid = True
        self.close()
        
    # Send the parameters when the windows is quit
    def closeEvent(self, event):
        if self.quitValid:
            # Save the different parameters
            self.params["lin_lyr"] = self.lineLyrCmb.currentText()
            self.params["lin_att1"] = self.lineAttCmb.currentText()
            self.params["lin_att_sep"] = self.lineAttSepLe.text()
            self.params["nod_lyr"] = self.nodeLyrCmb.currentText()
            self.params["nod_att"] = self.nodeAttCmb.currentText()
            if self.modeRadio1.isChecked():
                self.params["move_mode"] = 0
            else:
                self.params["move_mode"] = 1
            self.hide()
            # Update the new parameters in the json file
            json_params = {}
            json_params["vtx2nds_params"] = self.params
            with codecs.open(self.params_path, encoding='utf-8', mode='w') as json_file:
                json_file.write(json.dumps(json_params, indent=4, separators=(',', ': '), ensure_ascii=False))
            # Send the parameters
            self.send_nw_params.emit(self.params)
        else:
            # Hide the window
            self.hide()
    
    # Populate a combobox (lyr_cmb) with the list of layers filtered by type 
    # (obj_type = [QGis.Point] or [QGis.Line], ...)
    # json_dft = the name of the json key to use as the default value
    def populate_lyrcmb(self, lyr_cmb, obj_type, json_dft):
        # Create sorted list of the names of layers by type
        lyrs = self.get_layer_names(self.project, obj_type)
        lyr_dft = None
        lyr_cur_idx = 0
        if json_dft in self.old_params:
            lyr_dft = self.old_params[json_dft]
            if lyr_dft in lyrs:
                lyr_cur_idx = lyrs.index(lyr_dft)
        for lyr_name in lyrs:
            lyr_cmb.addItem(lyr_name)
        lyr_cmb.setCurrentIndex(lyr_cur_idx)
    
    # Populate a combobox (att_cmb) with the fields of the layer written in lyr_cmb
    # json_dft = the name of the json key to use as the default value
    def populate_flds(self, lyr_cmb, att_cmb, json_dft):
        att_cmb.clear()
        lyr_name = lyr_cmb.currentText()
        cur_lyr = self.project.mapLayersByName(lyr_name)[0]
        atts = []
        if cur_lyr:
            atts = get_layer_fields(cur_lyr)
        att_dft = None
        att_cur_idx = 0
        if json_dft in self.old_params:
            att_dft = self.old_params[json_dft]
            if att_dft in atts:
                att_cur_idx = atts.index(att_dft)
            # else:
                # att_cmb.addItem(att_dft)
                # att_cmb.setItemData(0, QColor("red"), Qt.TextColorRole)
        for att_name in atts:
            att_cmb.addItem(att_name)
        att_cmb.setCurrentIndex(att_cur_idx)
        

    # Return list of names of layers in the project
    # vtypes - list of layer types allowed (e.g. QgsWkbTypes.PointGeometry, 
    #     QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry or "all" or "raster")
    # return sorted list of layer names
    def get_layer_names(self, project, vtypes):
        layermap = project.mapLayers()
        layerlist = []
        if vtypes == "all":
            for name, layer in layermap.items():
                layerlist.append(layer.name())
        else:
            for name, layer in layermap.items():
                if layer.type() == QgsMapLayer.VectorLayer:
                    if layer.geometryType() in vtypes:
                        layerlist.append(layer.name())
                elif layer.type() == QgsMapLayer.RasterLayer:
                    if "raster" in vtypes:
                        layerlist.append(layer.name())
        return sorted(layerlist, key=locale.strxfrm)
        
# Return sorted list of fields of a layer instance
def get_layer_fields(layer):
    fld_lst = []
    for field in layer.fields():
        fld_lst.append(field.name())
    return sorted(fld_lst, key=locale.strxfrm)

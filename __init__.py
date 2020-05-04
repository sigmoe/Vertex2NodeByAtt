# -*- coding: utf-8 -*-

"""
    ***************************************************************************
    * Plugin name:   SgmVertex2NodeByAtt
    * Plugin type:   QGIS 3 plugin
    * Module:        Initialization
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
    * Last release:  2020-04-06
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
   
    This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load SgmVertex2NodeByAtt class from file sgm_vertex2nodebyatt
    from .sgm_vertex2nodebyatt import SgmVertex2NodeByAtt
    return SgmVertex2NodeByAtt(iface)

# Vertex2NodeByAtt
QGIS plugin : Move lines on points by attribute (and vice versa)

Description
===========
**Vertex2NodeByAtt** is a QGIS plugin that modifies the position of the vertices (the start-point and the end-point) of lines to put them at the position of 2 node objects, thanks to 1 attribute of the line that contains the 2 ids of the 2 nodes objects, with a separator. The reverse is also possible: move points on lines.

French description
==================
**Vertex2NodeByAtt** est une extension QGIS permettant de modifier la position des sommets de lignes (premier point et dernier point) pour les repositionner à l'emplacement de 2 objets ponctuels, grâce à la valeur d'un attribut correspondant à l'identifiant de chacun de ces 2 points (avec un séparateur spécifique entre les 2 identifiants dans la valeur d'attribut). L'inverse est également possible: déplacer les points sur les lignes.

Prerequisite
============
* QGIS 3.10 LTR

Documentation
=============
See the video (in French): https://youtu.be/kHRJkvIrJzo

Example of use:
- the layer LINES has an attribute named REGIDS
- the layer NODES has an attribute named PTID
- a LINES object has the value 'R1-R2' in REGIDS
- a NODES object has the value 'R1' in PTID
- another NODES object has the value 'R2' in PTID
- then the result is:
  1. the start-point of the LINES object is moved to the first NODES object position (R1)
  2. the end-point of the LINES object is moved to the second NODES object position(R2)
  3. the reverse is possible (the NODES objects are moved to the position of the start and end points of the LINES object)

Author
======
* Etienne MORO
* e-mail: em@sigmoe.fr
* website: www.sigmoe.fr

License
=======
GNU Public License (GPL) Version 3


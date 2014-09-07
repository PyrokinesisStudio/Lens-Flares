'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, os, bpy, mathutils, inspect
import xml.etree.ElementTree as ET
from bpy.app.handlers import persistent
sys.path.append(os.path.dirname(__file__))
from lens_flare_utils import *
from lens_flare_create_object_utils import *
from lens_flare_constraint_utils import *
from lens_flare_driver_utils import *
from lens_flare_animation_utils import *
from lens_flare_material_and_node_utils import *


bl_info = {
	"name":        "Lens Flares",
	"description": "",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 1),
	"location":    "View 3D > Tool Shelf",
	"category":    "3D View",
	"warning":	   "alpha"
	}
	
elementsFolder = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] + "elements\\"
	
flareControlerPrefix = "flare controler"
angleCalculatorPrefix = "angle calculator"
startDistanceCalculatorPrefix = "start distance calculator"
flareElementPrefix = "flare element"
cameraCenterPrefix = "center of camera"
cameraDirectionCalculatorPrefix = "camera direction calculator"
startElementPrefix = "start element"
endElementPrefix = "end element"
flareElementEmptyPrefix = "flare element data"
elementEmptyNamesContainerPrefix = "element data names container"
targetEmptyPrefix = "target empty"

dofDistanceName = "dof distance"
plainDistanceName = "plane distance"
directionXName = "direction x"
directionYName = "direction y"
directionZName = "direction z"
angleName = "angle"
startDistanceName = "start distance"
avoidArtefactsOffsetName = "offset to avoid artefacts"
currentElementOffsetName = "current offset"
elementPositionName = "element position"
planeWidthFactorName = "width factor"
scaleXName = "scale x"
scaleYName = "scale y"
imagePathName = "image path"
colorMultiplyName = "multiply color"
additionalRotationName = "additional rotation"
trackToCenterInfluenceName = "track to center influence"
intensityNodeName = "intensity"
intensityName = "intensity"
imageNodeName = "image node"
colorMultiplyNodeName = "color multiply node"
childOfFlarePropertyName = "child of flare"
targetPropertyName = "flare target"
cameraOfFlarePropertyName = "camera of this flare"
startElementPropertyName = "start element"
endElementPropertyName = "end element"
dataElementPropertyName = "data element"
elementEmptyNamesContainerPropertyName = "element data names container"
elementEmptyNamePropertyName = "element data name"
elementPlainNamePropertyName = "element plane name"
flareNamePropertyName = "flare name"
linkToFlareControlerPropertyName = "flare link from target"
targetNamePropertyName = "target empty"

anglePath = getDataPath(angleName)
startDistancePath = getDataPath(startDistanceName)
directionXPath = getDataPath(directionXName)
directionYPath = getDataPath(directionYName)
directionZPath = getDataPath(directionZName)
dofDistancePath = getDataPath(dofDistanceName)
avoidArtefactsOffsetPath = getDataPath(avoidArtefactsOffsetName)
elementPositionPath = getDataPath(elementPositionName)
planeWidthFactorPath = getDataPath(planeWidthFactorName)
scaleXPath = getDataPath(scaleXName)
scaleYPath = getDataPath(scaleYName)
additionalRotationPath = getDataPath(additionalRotationName)
trackToCenterInfluencePath = getDataPath(trackToCenterInfluenceName)
intensityPath = getDataPath(intensityName)
elementEmptyNamePropertyPath = getDataPath(elementEmptyNamePropertyName)
flareNamePropertyPath = getDataPath(flareNamePropertyName)


# new lens flare
###################################

def newLensFlareFromDictionary(camera, target, flareDataDictionary):
	flareControler = newLensFlare(camera, target)
	setFlareDataDictionaryOnFlare(flareControler, flareDataDictionary)
	return flareControler

def newLensFlare(camera, target):
	setCurrentOffsetPropertyOnCamera(camera)
	center = getCenterEmpty(camera)
	targetEmpty = newTargetEmpty(target)
	flareControler = newFlareControler(camera, targetEmpty, center)	
	setCustomProperty(targetEmpty, linkToFlareControlerPropertyName, flareControler.name)
	angleCalculator = newAngleCalculator(flareControler, camera, targetEmpty, center)
	startDistanceCalculator = newStartDistanceCalculator(flareControler, angleCalculator, center, camera)
	
	startElement = newStartElement(flareControler, camera, startDistanceCalculator)
	endElement = newEndElement(flareControler, startElement, center, camera)
	
	elementEmptyNamesContainer = newElementEmptyNamesContainer(flareControler)
	
	setCustomProperty(flareControler, startElementPropertyName, startElement.name)
	setCustomProperty(flareControler, endElementPropertyName, endElement.name)
	setCustomProperty(flareControler, elementEmptyNamesContainerPropertyName, elementEmptyNamesContainer.name)
	setCustomProperty(flareControler, targetNamePropertyName, targetEmpty.name)
	setParentWithoutInverse(targetEmpty, camera)
	makePartOfFlareControler(targetEmpty, flareControler)
	
	flareControler.hide =  True
	angleCalculator.hide = True
	startDistanceCalculator.hide = True
	startElement.hide = True
	endElement.hide = True
	elementEmptyNamesContainer.hide = True
	targetEmpty.hide = True
	
	return flareControler
	
def setCurrentOffsetPropertyOnCamera(camera):
	if currentElementOffsetName not in camera:
		setCustomProperty(camera, currentElementOffsetName, -0.002)
		
def newTargetEmpty(target):
	targetEmpty = newEmpty(name = targetEmptyPrefix)
	constraint = targetEmpty.constraints.new(type = "COPY_LOCATION")
	constraint.target = target
	return targetEmpty

# camera direction calculator

def getCameraDirectionCalculator(camera):
	directionCalculators = getCameraDirectionCalculators()
	for calculator in directionCalculators:
		if calculator.parent == camera:
			return calculator
	return newCameraDirectionCalculator(camera)
	
def getCameraDirectionCalculators():
	calculators = []
	for object in bpy.data.objects:
		if hasPrefix(object.name, cameraDirectionCalculatorPrefix):
			calculators.append(object)
	return calculators
	
def newCameraDirectionCalculator(camera):
	calculator = newEmpty(name = cameraDirectionCalculatorPrefix)
	setParentWithoutInverse(calculator, camera)
	calculator.location.z = -1
	lockCurrentLocalLocation(calculator)
	setCameraDirectionProperties(calculator, camera)
	calculator.hide = True
	return calculator
	
def setCameraDirectionProperties(directionCalculator, camera):
	setTransformDifferenceAsProperty(directionCalculator, camera, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(directionCalculator, camera, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(directionCalculator, camera, directionZName, "LOC_Z", normalized = True)
	
# center creation	

def getCenterEmpty(camera):
	centers = getCenterEmpties()
	for center in centers:
		if center.parent == camera:
			return center
	return newCenterEmpty(camera)
	
def getCenterEmpties():
	centers = []
	for object in bpy.data.objects:
		if hasPrefix(object.name, cameraCenterPrefix):
			centers.append(object)
	return centers
	
def newCenterEmpty(camera):
	center = newEmpty(name = cameraCenterPrefix, type = "SPHERE")
	setParentWithoutInverse(center, camera)
	center.empty_draw_size = 0.1
	center.hide = True
	setCenterDistance(center, camera)
	lockCurrentLocalLocation(center, zAxes = False)
	return center
	
def setCenterDistance(center, camera):
	directionCalculator = getCameraDirectionCalculator(camera)
	
	driver = newDriver(center, "location", index = 2)
	linkFloatPropertyToDriver(driver, "distance", getCameraFromObject(camera), "dof_distance", idType = "CAMERA")
	linkTransformChannelToDriver(driver, "scale", camera, "SCALE_Z")
	driver.expression = "-max(distance, 1)/scale"
	
# flare controler creation	

def newFlareControler(camera, target, center):
	flareControler = newEmpty(name = flareControlerPrefix)
	makePartOfFlareControler(flareControler, flareControler)
	setCustomProperty(flareControler, flareNamePropertyName, "Lens Flare")
	setCustomProperty(flareControler, intensityName, 1.0, min = 0.0)
	setObjectReference(flareControler, cameraOfFlarePropertyName, camera)
	setObjectReference(flareControler, targetPropertyName, target)
	setParentWithoutInverse(flareControler, camera)	
	lockCurrentLocalLocation(flareControler)
	setTargetDirectionProperties(flareControler, target)
	return flareControler
	
def setTargetDirectionProperties(flareControler, target):
	setTransformDifferenceAsProperty(flareControler, target, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionZName, "LOC_Z", normalized = True)
	
# angle calculator

def newAngleCalculator(flareControler, camera, target, center):
	angleCalculator = newEmpty(name = angleCalculatorPrefix)
	makePartOfFlareControler(angleCalculator, flareControler)
	setParentWithoutInverse(angleCalculator, flareControler)
	setTargetAngleProperty(angleCalculator, flareControler, getCameraDirectionCalculator(camera))
	return angleCalculator
	
def setTargetAngleProperty(angleCalculator, flareControler, cameraDirectionCalculator):
	setCustomProperty(angleCalculator, angleName)
	driver = newDriver(angleCalculator, anglePath)
	linkFloatPropertyToDriver(driver, "x1", flareControler, directionXPath)
	linkFloatPropertyToDriver(driver, "y1", flareControler, directionYPath)
	linkFloatPropertyToDriver(driver, "z1", flareControler, directionZPath)	
	linkFloatPropertyToDriver(driver, "x2", cameraDirectionCalculator, directionXPath)
	linkFloatPropertyToDriver(driver, "y2", cameraDirectionCalculator, directionYPath)
	linkFloatPropertyToDriver(driver, "z2", cameraDirectionCalculator, directionZPath)
	driver.expression = "degrees(acos(x1*x2+y1*y2+z1*z2))"
	
# start distance calculator
	
def newStartDistanceCalculator(flareControler, angleCalculator, center, camera):
	startDistanceCalculator = newEmpty(name = startDistanceCalculatorPrefix)
	makePartOfFlareControler(startDistanceCalculator, flareControler)
	setParentWithoutInverse(startDistanceCalculator, flareControler)
	setStartDistanceProperty(startDistanceCalculator, angleCalculator, center, camera)
	return startDistanceCalculator
	
def setStartDistanceProperty(startDistanceCalculator, angleCalculator, center, camera):
	setCustomProperty(startDistanceCalculator, startDistanceName)
	driver = newDriver(startDistanceCalculator, startDistancePath)
	linkDistanceToDriver(driver, "distance", center, camera)
	linkFloatPropertyToDriver(driver, "angle", angleCalculator, anglePath)
	driver.expression = "-distance/cos(radians(angle))"

# start element creation
	
def newStartElement(flareControler, camera, startDistanceCalculator):
	startElement = newEmpty(name = startElementPrefix)
	makePartOfFlareControler(startElement, flareControler)
	setParentWithoutInverse(startElement, flareControler)
	setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator)
	return startElement
	
def setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator):
	constraint = startElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	
	for val in [".min", ".max"]:
		driver = newDriver(startElement, constraintPath + val + "_x")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionXPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_X")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_y")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionYPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Y")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_z")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionZPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Z")
		driver.expression = "direction*distance+cam"
	
# end element creation

def newEndElement(flareControler, startElement, center, camera):
	endElement = newEmpty(name = endElementPrefix)
	makePartOfFlareControler(endElement, flareControler)
	setParentWithoutInverse(endElement, flareControler)
	setEndLocationDrivers(endElement, startElement, center)
	return endElement
	
def setEndLocationDrivers(endElement, startElement, center):
	constraint = endElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)

	for val in [".min", ".max"]:
		driver = newDriver(endElement, constraintPath + val + "_x")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_X")
		linkTransformChannelToDriver(driver, "center", center, "LOC_X")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_y")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Y")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Y")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_z")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Z")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Z")
		driver.expression = "2*center - start"
	
# element data names container
	
def newElementEmptyNamesContainer(flareControler):
	elementEmptyNamesContainer = newEmpty(name = elementEmptyNamesContainerPrefix)
	makePartOfFlareControler(elementEmptyNamesContainer, flareControler)
	setParentWithoutInverse(elementEmptyNamesContainer, flareControler)
	return elementEmptyNamesContainer
	

	
	
# new element
#########################################

def newFlareElementFromDictionary(flareControler, elementDataDictionary):
	name = elementDataDictionary[elementEmptyNamePropertyName]
	image = getImage(elementDataDictionary[imagePathName])
	(elementEmpty, plane) = newFlareElement(flareControler, image, name)
	setElementDataDictionaryOnElement(elementEmpty, elementDataDictionary)
	
def newFlareElement(flareControler, image, name = "element"):
	camera = getCameraFromFlareControler(flareControler)
	camera[currentElementOffsetName] += 0.0003
	startElement = getStartElement(flareControler)
	endElement = getEndElement(flareControler)
	
	elementEmpty = newFlareElementEmpty(flareControler, startElement, endElement, camera)
	flareElement = newFlareElementPlane(image, elementEmpty, flareControler, camera)	
	
	setCustomProperty(elementEmpty, elementPlainNamePropertyName, flareElement.name)
	
	makePartOfFlareElement(elementEmpty, elementEmpty)
	makePartOfFlareElement(flareElement, elementEmpty)
	
	elementEmptyNamesContainer = getElementEmptyNamesContainer(flareControler)
	appendObjectReference(elementEmptyNamesContainer, elementEmpty)
	
	setCustomProperty(elementEmpty, elementEmptyNamePropertyName, name)
	
	return (elementEmpty, flareElement)
	
def newFlareElementEmpty(flareControler, startElement, endElement, camera):
	dataEmpty = newEmpty(name = flareElementEmptyPrefix)
	makePartOfFlareControler(dataEmpty, flareControler)
	dataEmpty.empty_draw_size = 0.01
	
	setParentWithoutInverse(dataEmpty, flareControler)
	setCustomProperty(dataEmpty, elementEmptyNamePropertyName, "Glow", description = "This name shows up in the element list.")
	setCustomProperty(dataEmpty, avoidArtefactsOffsetName, camera[currentElementOffsetName], description = "Random offset of every object to avoid overlapping.")
	setCustomProperty(dataEmpty, elementPositionName, 0.2, description = "Relative element position. 0: element is on target; 1: opposite side")
	setCustomProperty(dataEmpty, scaleXName, 1.0, min = 0.0, description = "Width of this element.")
	setCustomProperty(dataEmpty, scaleYName, 1.0, min = 0.0, description = "Height of this element.")
	setCustomProperty(dataEmpty, trackToCenterInfluenceName, 0.0, min = 0.0, max = 1.0, description = "0: normal; 1: rotate element to center")
	setCustomProperty(dataEmpty, intensityName, 1.0, min = 0.0, description = "Brightness of this element.")
	setCustomProperty(dataEmpty, additionalRotationName, 0, description = "Rotation in camera direction.")
	
	constraint = dataEmpty.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	
	for val in [".min", ".max"]:
		driver = newDriver(dataEmpty, constraintPath + val + "_x")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_X")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_X")
		linkFloatPropertyToDriver(driver, "position", dataEmpty, elementPositionPath)
		driver.expression = "start * (1-position) + end * position"
		
		driver = newDriver(dataEmpty, constraintPath + val + "_y")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Y")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_Y")
		linkFloatPropertyToDriver(driver, "position", dataEmpty, elementPositionPath)
		driver.expression = "start * (1-position) + end * position"
		
		driver = newDriver(dataEmpty, constraintPath + val + "_z")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Z")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_Z")
		linkFloatPropertyToDriver(driver, "position", dataEmpty, elementPositionPath)
		driver.expression = "start * (1-position) + end * position"
		
	return dataEmpty

def newFlareElementPlane(image, elementEmpty, flareControler, camera):
	plane = newPlane(name = flareElementPrefix, size = 0.1)
	makePartOfFlareControler(plane, flareControler)
	setCustomProperty(plane, planeWidthFactorName, image.size[0] / image.size[1])
	makeOnlyVisibleToCamera(plane)
	material = newCyclesFlareMaterial(image)
	setMaterialOnObject(plane, material)
	
	setParentWithoutInverse(plane, elementEmpty)
	constraint = plane.constraints.new(type = "LIMIT_SCALE")
	constraintPath = getConstraintPath(constraint)
	setUseMinMaxToTrue(constraint)
	
	for val in [".min", ".max"]:
		driver = newDriver(plane, constraintPath + val + "_x")
		linkDistanceToDriver(driver, "distance", plane, camera)
		linkFloatPropertyToDriver(driver, "factor", plane, planeWidthFactorPath)
		linkFloatPropertyToDriver(driver, "scale", elementEmpty, scaleXPath)
		driver.expression = "factor * scale * distance / 1"
		
		driver = newDriver(plane, constraintPath + val + "_y")
		linkDistanceToDriver(driver, "distance", plane, camera)
		linkFloatPropertyToDriver(driver, "scale", elementEmpty, scaleYPath)
		driver.expression = "scale * distance / 1"
		
		driver = newDriver(plane, constraintPath + val + "_z")
		linkDistanceToDriver(driver, "distance", plane, camera)
		driver.expression = "distance / 1"
	
	constraint = plane.constraints.new(type = "TRACK_TO")
	constraint.target = getCenterEmpty(camera)
	constraint.track_axis = "TRACK_X"
	constraint.use_target_z = True
	constraintPath = getConstraintPath(constraint)
	driver = newDriver(plane, constraintPath + ".influence", type = "SUM")
	linkFloatPropertyToDriver(driver, "var", elementEmpty, trackToCenterInfluencePath)
	
	constraint = plane.constraints.new(type = "LIMIT_ROTATION")
	constraint.owner_space = "LOCAL"
	constraint.use_limit_y = True
	
	constraint = plane.constraints.new(type = "LIMIT_LOCATION")
	constraint.owner_space = "LOCAL"
	constraint.use_min_z = True
	constraint.use_max_z = True
	constraintPath = getConstraintPath(constraint)
	for channel in [".min_z", ".max_z"]:
		driver = newDriver(plane, constraintPath + channel)
		linkFloatPropertyToDriver(driver, "offset", elementEmpty, avoidArtefactsOffsetPath)
		linkDistanceToDriver(driver, "distance", elementEmpty, camera)
		driver.expression = "offset*distance"
	
	driver = newDriver(getNodeWithNameInObject(plane, intensityNodeName).inputs[1], "default_value")
	linkFloatPropertyToDriver(driver, "special", elementEmpty, intensityPath)
	linkFloatPropertyToDriver(driver, "general", flareControler, intensityPath)
	driver.expression = "special * general"
	
	driver = newDriver(plane, "rotation_euler", index = 2)
	linkFloatPropertyToDriver(driver, "var", elementEmpty, additionalRotationPath)
	driver.expression = "radians(var)"
	
	return plane
	
def newCyclesFlareMaterial(image):
	material = newCyclesMaterial()
	cleanMaterial(material)
	
	nodeTree = material.node_tree
	textureCoordinatesNode = newTextureCoordinatesNode(nodeTree)
	imageNode = newImageTextureNode(nodeTree)
	colorRamp = newColorRampNode(nodeTree)
	colorMultiply = newColorMixNode(nodeTree, type = "MULTIPLY", factor = 1.0, default2 = [1.0, 1.0, 1.0, 1.0])
	rerouteImage = newRerouteNode(nodeTree)
	toBw = newRgbToBwNode(nodeTree)
	mixColor = newColorMixNode(nodeTree, type = "DIVIDE", factor = 1.0)
	emission = newEmissionNode(nodeTree)
	intensityNode = newMathNode(nodeTree, type = "MULTIPLY", default = 1.0)
	transparent = newTransparentNode(nodeTree)
	mixShader = newMixShader(nodeTree)
	output = newOutputNode(nodeTree)
	
	imageNode.image = image
	intensityNode.name = intensityNodeName
	imageNode.name = imageNodeName
	colorMultiply.name = colorMultiplyNodeName
	
	newNodeLink(nodeTree, textureCoordinatesNode.outputs["Generated"], imageNode.inputs[0])
	newNodeLink(nodeTree, imageNode.outputs[0], colorRamp.inputs[0])
	newNodeLink(nodeTree, colorRamp.outputs[0], colorMultiply.inputs[1])
	newNodeLink(nodeTree, colorMultiply.outputs[0], rerouteImage.inputs[0])
	newNodeLink(nodeTree, rerouteImage.outputs[0], toBw.inputs[0])
	newNodeLink(nodeTree, rerouteImage.outputs[0], mixColor.inputs[1])
	newNodeLink(nodeTree, toBw.outputs[0], mixColor.inputs[2])
	newNodeLink(nodeTree, mixColor.outputs[0], emission.inputs[0])
	newNodeLink(nodeTree, rerouteImage.outputs[0], intensityNode.inputs[0])
	linkToMixShader(nodeTree, transparent.outputs[0], emission.outputs[0], mixShader, factor = intensityNode.outputs[0])
	newNodeLink(nodeTree, mixShader.outputs[0], output.inputs[0])
	return material
	
	
	
# utils
################################

def getAllFlares():
	flareControlers = []
	for object in bpy.data.objects:
		if hasFlareControlerAttribute(object) or hasLinkToFlareControler(object):
			flareControler = getCorrespondingFlareControler(object)
			if flareControler not in flareControlers and flareControler is not None:
				flareControlers.append(flareControler)
	return flareControlers

def getSelectedFlares():
	flareControlers = []
	selection = getSelectedObjects()
	selection.append(getActive())
	for object in selection:
		if hasFlareControlerAttribute(object) or hasLinkToFlareControler(object):
			flareControler = getCorrespondingFlareControler(object)
			if flareControler not in flareControlers and flareControler is not None:
				flareControlers.append(flareControler)
	return flareControlers
	
def getSelectedFlareElementEmpties():	
	flareElementEmpties = []
	selection = getSelectedObjects()
	for object in selection:
		if hasFlareElementAttribute(object):
			elementEmpty = getCorrespondingDataElement(object)
			if elementEmpty not in flareElementEmpties and elementEmpty is not None:
				flareElementEmpties.append(elementEmpty)
	return flareElementEmpties
	
def getDataElementsFromFlare(flareControler):
	elementEmptyNamesContainer = getElementEmptyNamesContainer(flareControler)
	elementEmpties = getObjectReferences(elementEmptyNamesContainer)
	return elementEmpties
	
def getCameraFromFlareControler(flareControler):
	return flareControler.parent
	
def getStartElement(flareControler):
	return bpy.data.objects[flareControler[startElementPropertyName]]
def getEndElement(flareControler):
	return bpy.data.objects[flareControler[endElementPropertyName]]
def getElementEmptyObjects(flareControler):
	container = getElementEmptyNamesContainer(flareControler)
	return getObjectReferences(container)
def getElementEmptyNamesContainer(flareControler):
	return bpy.data.objects[flareControler[elementEmptyNamesContainerPropertyName]]

def makePartOfFlareControler(object, flareControler):
	setCustomProperty(object, childOfFlarePropertyName, flareControler.name)
def isPartOfFlareControler(object, flareControler):
	return object.get(childOfFlarePropertyName) == flareControler.name
def getCorrespondingFlareControler(object):
	if hasFlareControlerAttribute(object): return bpy.data.objects.get(object[childOfFlarePropertyName])
	if hasLinkToFlareControler(object): return bpy.data.objects.get(object[linkToFlareControlerPropertyName])
def hasFlareControlerAttribute(object):
	return childOfFlarePropertyName in object
def hasLinkToFlareControler(object):
	return linkToFlareControlerPropertyName in object
	
def makePartOfFlareElement(object, dataElement):
	setCustomProperty(object, dataElementPropertyName, dataElement.name)
def getCorrespondingDataElement(object):
	return bpy.data.objects.get(object[dataElementPropertyName])
def hasFlareElementAttribute(object):
	return dataElementPropertyName in object
	
def getTargetEmpty(flareControler):
	return bpy.data.objects[flareControler[targetNamePropertyName]]
	
def getPlaneFromData(data):
	return bpy.data.objects[data[elementPlainNamePropertyName]]
	
def getImageFromElementEmpty(data):
	plane = getPlaneFromData(data)
	node = getNodeWithNameInObject(plane, imageNodeName)
	return node.image
	
def setImagePathOnElementPlane(plane, imagePath):
	image = getImage(imagePath)
	getNodeWithNameInObject(plane, imageNodeName).image = image
	plane[planeWidthFactorName] = image.size[0] / image.size[1]
	
def setMultiplyColorOnElementPlane(plane, color):
	getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2].default_value = color
	
def getFlareDataDictionaryFromFlare(flareControler):
	return {	flareNamePropertyName : flareControler[flareNamePropertyName],
				intensityName : flareControler[intensityName] }
				
def setFlareDataDictionaryOnFlare(flareControler, flareDataDictionary):
	flareControler[flareNamePropertyName] = flareDataDictionary[flareNamePropertyName]
	flareControler[intensityName] = flareDataDictionary[intensityName]
	
def getElementDataDictionaryFromElement(element):
	plane = getPlaneFromData(element)
	return { 	elementPositionName : element[elementPositionName],
				elementEmptyNamePropertyName : element[elementEmptyNamePropertyName],
				imagePathName : getImageFromElementEmpty(element).filepath,
				scaleXName : element[scaleXName],
				scaleYName : element[scaleYName],
				trackToCenterInfluenceName : element[trackToCenterInfluenceName],
				intensityName : element[intensityName],
				additionalRotationName : element[additionalRotationName],
				colorMultiplyName : getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2].default_value }
	
def setElementDataDictionaryOnElement(elementEmpty, dataDictionary):	
	plane = getPlaneFromData(elementEmpty)
	elementEmpty[elementEmptyNamePropertyName] = dataDictionary[elementEmptyNamePropertyName]
	elementEmpty[elementPositionName] = dataDictionary[elementPositionName]
	elementEmpty[scaleXName] = dataDictionary[scaleXName]
	elementEmpty[scaleYName] = dataDictionary[scaleYName]
	elementEmpty[trackToCenterInfluenceName] = dataDictionary[trackToCenterInfluenceName]
	elementEmpty[intensityName] = dataDictionary[intensityName]
	elementEmpty[additionalRotationName] = dataDictionary[additionalRotationName]
	setImagePathOnElementPlane(plane, dataDictionary[imagePathName])
	setMultiplyColorOnElementPlane(plane, dataDictionary[colorMultiplyName])
	
def deleteFlare(flareControler):
	for object in bpy.data.objects:
		if isPartOfFlareControler(object, flareControler) and object != flareControler:
			delete(object)
	delete(flareControler)
	
def deleteFlareElement(elementEmpty):
	flareControler = getCorrespondingFlareControler(elementEmpty)
	delete(getPlaneFromData(elementEmpty))
	delete(elementEmpty)
	cleanReferenceList(getElementEmptyNamesContainer(flareControler))
	
def duplicateFlareElement(elementEmpty):
	flareControler = getCorrespondingFlareControler(elementEmpty)
	elementDataDictionary = getElementDataDictionaryFromElement(elementEmpty)
	newFlareElementFromDictionary(flareControler, elementDataDictionary)
	
def duplicateLensFlare(flareControler):
	flareDataDictionary = getFlareDataDictionaryFromFlare(flareControler)
	elements = getElementEmptyObjects(flareControler)
	elementDatas = []
	for element in elements:
		elementDatas.append(getElementDataDictionaryFromElement(element))
	generateLensFlare(getActiveCamera(), getActive(), flareDataDictionary, elementDatas)
	
def generateLensFlare(camera, target, flareDataDictionary, elementDatas):
	flareControler = newLensFlareFromDictionary(camera, target, flareDataDictionary)
	for elementData in elementDatas:
		newFlareElementFromDictionary(flareControler, elementData)
	
def saveLensFlare(flareControler, path):
	flare = ET.Element("Flare")
	flare.set("name", flareControler[flareNamePropertyName])
	flare.set("intensity", str(flareControler[intensityName]))
	
	elements = getElementEmptyObjects(flareControler)
	for element in elements:
		plane = getPlaneFromData(element)
		el = ET.SubElement(flare, "Element")
		el.set("name", element[elementEmptyNamePropertyName])
		
		el.set("position", str(element[elementPositionName]))
		el.set("intensity", str(element[intensityName]))
		el.set("rotation", str(element[additionalRotationName]))
		el.set("centerRotation", str(element[trackToCenterInfluenceName]))
		el.set("width", str(element[scaleXName]))
		el.set("height", str(element[scaleYName]))
		el.set("imageName", str(getImageFromElementEmpty(element).name))
		
		multiplyColor = ET.SubElement(el, "multiplyColor")
		color = getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2].default_value
		multiplyColor.set("red", str(color[0]))
		multiplyColor.set("green", str(color[1]))
		multiplyColor.set("blue", str(color[2]))
	
	ET.ElementTree(flare).write(path)
	
	
# interface
##################################

class LensFlaresPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout		
		
		flares = getAllFlares()
		if len(flares) == 0: layout.label("no flares in this scene", icon = "INFO")
		else:
			col = layout.column(align = True)
			for flare in flares:
				row = col.row(align = True)
				row.scale_y = 1.35
				selectFlare = row.operator("lens_flares.select_flare", text = flare[flareNamePropertyName])
				selectFlare.flareName = flare.name
				saveFlare = row.operator("lens_flares.save_lens_flare", text = "", icon = "SAVE_COPY")
				saveFlare.flareName = flare.name
				deleteFlare = row.operator("lens_flares.delete_lens_flare", text = "", icon = "X")
				deleteFlare.flareName = flare.name
		layout.operator("lens_flares.new_lens_flare", icon = 'PLUS')
		
class LensFlareSettingsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares Settings"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return len(getSelectedFlares()) > 0
	
	def draw(self, context):
		layout = self.layout
		
		flare = getSelectedFlares()[0]
		target = getTargetEmpty(flare)
		self.bl_label = "Settings: " + flare[flareNamePropertyName]
		
		row = layout.row(align = True)
		row.prop(flare, flareNamePropertyPath, text = "Name")
		duplicateFlare = row.operator("lens_flares.duplicate_lens_flare", text = "", icon = "NEW")
		duplicateFlare.flareName = flare.name
		
		layout.prop(target.constraints[0], 'target', text = "Target")
		layout.prop(flare, intensityPath, text = "Intensity")
				
		allDatas = getDataElementsFromFlare(flare)
		box = layout.box()
		if len(allDatas) == 0: box.label("no elements on this flare", icon = "INFO")
		else:
			col = box.column(align = True)
			for data in allDatas:
				row = col.row(align = True)
				row.scale_y = 1.35
				selectElement = row.operator("lens_flares.select_flare_element", text = data[elementEmptyNamePropertyName])
				selectElement.elementName = data.name
				deleteElement = row.operator("lens_flares.delete_flare_element", text = "", icon = "X")
				deleteElement.elementName = data.name
		newElement = box.operator("lens_flares.new_flare_element", icon = 'PLUS')
		newElement.flareName = flare.name
		
		for data in allDatas:
			if data.select or getPlaneFromData(data).select:
				layout.separator()
				
				row = layout.row(align = True)
				row.prop(data, elementEmptyNamePropertyPath, text = "Name")
				duplicateElement = row.operator("lens_flares.duplicate_flare_element", text = "", icon = "NEW")
				duplicateElement.elementName = data.name
				
				layout.prop(data, elementPositionPath, text = "Position")
				layout.prop(data, intensityPath, text = "Intensity")
				
				col = layout.column(align = True)
				col.prop(data, additionalRotationPath, text = "Rotation")
				col.prop(data, trackToCenterInfluencePath, text = "Center Influence")
				
				col = layout.column(align = True)
				col.prop(data, scaleXPath, text = "Width")
				col.prop(data, scaleYPath, text = "Height")
				
				plane = getPlaneFromData(data)
				layout.prop(getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2], "default_value")
		
		
# operators
###################################
		
class NewLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.new_lens_flare"
	bl_label = "New Lens Flare"
	bl_description = "Create a new Lens Flare on active object."
	
	def execute(self, context):
		newLensFlare(getActiveCamera(), getActive())
		return{"FINISHED"}
		
class NewFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.new_flare_element"
	bl_label = "New Flare Element"
	bl_description = "Create a new Element in active Lens Flare."

	flareName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")

	def execute(self, context):
		newFlareElement(bpy.data.objects[self.flareName], getImage(self.filepath), getFileName(self.filepath))
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = elementsFolder
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class SaveLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.save_lens_flare"
	bl_label = "Save Lens Flare"
	bl_description = "Save this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		saveLensFlare(bpy.data.objects[self.flareName], self.filepath)
		return{"FINISHED"}
		
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class SelectFlare(bpy.types.Operator):
	bl_idname = "lens_flares.select_flare"
	bl_label = "Select Flare"
	bl_description = "Select this flare to see its elements."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		onlySelect(bpy.data.objects[self.flareName])
		return{"FINISHED"}
		
class SelectFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.select_flare_element"
	bl_label = "Select Flare Element"
	bl_description = "Select this element to change its settings."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		onlySelect(bpy.data.objects[self.elementName])
		return{"FINISHED"}
		
class DeleteLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.delete_lens_flare"
	bl_label = "Delete Lens Flare"
	bl_description = "Delete this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		selectionBefore = getSelectedObjects()
		deleteFlare(bpy.data.objects[self.flareName])
		setSelectedObjects(selectionBefore)
		return{"FINISHED"}
		
class DeleteFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.delete_flare_element"
	bl_label = "Delete Flare Element"
	bl_description = "Delete this Element."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		selectionBefore = getSelectedObjects()
		deleteFlareElement(bpy.data.objects[self.elementName])
		setSelectedObjects(selectionBefore)
		return{"FINISHED"}

class DuplicateFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.duplicate_flare_element"
	bl_label = "Duplicate Flare Element"
	bl_description = "Duplicate this Element."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		duplicateFlareElement(bpy.data.objects[self.elementName])
		return{"FINISHED"}
		
class DuplicateLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.duplicate_lens_flare"
	bl_label = "Duplicate Lens Flare"
	bl_description = "Duplicate this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		duplicateLensFlare(bpy.data.objects[self.flareName])
		return{"FINISHED"}
		
		
		
# register
##################################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
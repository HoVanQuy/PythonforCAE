from abaqus import*
from abaqusConstants import*
import regionToolset

session.viewports['Viewport: 1'].setValues(displayedObject=None)

mdb.models.changeKey(fromName='Model-1', toName='Electrical Switch')
switchModel = mdb.models['Electrical Switch']

import sketch
import part

switchSketch = switchModel.ConstrainedSketch(name='Switch Sketch', sheetSize=50)
switchSketch.Line(point1=(0,0), point2=(20,0))
switchSketch.Line(point1=(2,2), point2=(4,2))
switchSketch.Line(point1=(4,2), point2=(6,4))
switchSketch.Line(point1=(6,4), point2=(10,2))
switchSketch.Line(point1=(10,2), point2=(20,2))
#Use BaseShellExtrude() to create feature object
switchPart = switchModel.Part(name='Switch Part', dimensionality=THREE_D, type=DEFORMABLE_BODY)
switchPart.BaseShellExtrude(sketch=switchSketch, depth=2)

import material

switchMaterial = switchModel.Material(name='Generic Steel')
switchMaterial.Elastic(table=((210E3,0.3),))

import section

switchSection = switchModel.HomogeneousShellSection(name='Switch Section', material='Generic Steel', thicknessType=UNIFORM, thickness=0.15)
#Indentify all the faces by using findAt()
point1 = (10,0,0)
point2 = (3,2,0)
point3 = (5,3,0)
point4 = (8,3,0)
point5 = (15,2,0)
all_faces = switchPart.faces.findAt((point1,), (point2,), (point3,), (point4,), (point5,))
switchRegion = (all_faces,)
switchPart.SectionAssignment(region=switchRegion, sectionName='Switch Section', offset=0, offsetType=MIDDLE_SURFACE, offsetField='')

#For contact analysis, you will have to define the element normals.
#This should be done by using the flipNormal() method.
#Finding the direction of the face orientation can be challenging.
#So it is recommended to try up to this point, find if the flipping direction is correct or not, and then proceed further.
#We have to make sure that purple-colored faces (can be seen in the GUI) must be facing each other.
#The regionToolset module is used to define the region and then assign the element normals. """
flippingface_point = (10,0,0)
flippingface = switchPart.faces.findAt((flippingface_point,))
flippingface_region = regionToolset.Region(faces=flippingface)
switchPart.flipNormal(regions=flippingface_region)

import assembly

switchAssembly = switchModel.rootAssembly
swithInstance = switchAssembly.Instance(name='Switch Instance', part=switchPart, dependent=ON)

import step

switchModel.StaticStep(name='Load Step', previous='Initial', description='Apply forces in this step', nlgeom=ON)

#Apply boundary conditions
#Indentify 2 edges on the right side
rightedge_point1 = (20,0,1)
rightedge_point2 = (20,2,1)
rightedges = swithInstance.edges.findAt((rightedge_point1,), (rightedge_point2,))
rightedges_region = regionToolset.Region(edges=rightedges)
switchModel.EncastreBC(name='Encastre Edge', createStepName='Initial', region=rightedges_region)

#Next, we have to apply displacement boundary condition to edge
displacementedge_point = (6,4,1)
displacementedge = swithInstance.edges.findAt((displacementedge_point,))
displacementedge_region = switchAssembly.Set(edges=displacementedge, name='Displacement Set')
switchModel.DisplacementBC(name='Displacement BC', createStepName='Load Step', region=displacementedge_region, u1=UNSET, u2=-3, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

#Create datum plane and partition
switchPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=10)
face_to_partition = switchPart.faces.findAt(((10,0,0),))
switchPart.PartitionFaceByDatumPlane(datumPlane=switchPart.datums[4], faces=face_to_partition)

#Define interaction properties
import interaction
#Define contact properties like tangential and normal behavior
switchModel.ContactProperty('Interaction Property')
switchModel.interactionProperties['Interaction Property'].TangentialBehavior(formulation=FRICTIONLESS)
switchModel.interactionProperties['Interaction Property'].NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, contactStiffness=DEFAULT, contactStiffnessScaleFactor=1, clearanceAtZeroContactPressure=0, stiffnessBehavior=LINEAR, constraintEnforcementMethod=PENALTY)
#Define master and slave surfaces
#side...faces() to create direction of surfaces  
master_surface_point = (5,0,1)
master_surface = swithInstance.faces.findAt((master_surface_point,))
master_surface_region = switchAssembly.Surface(side2Faces=master_surface, name='Master Surface')

slave_surface_point = (3,2,1)
slave_surface = swithInstance.faces.findAt((slave_surface_point,))
slave_surface_region = switchAssembly.Surface(side1Faces=slave_surface, name='Slave Surface')

#Refer scripting manual for the correct usage of this statement
switchModel.SurfaceToSurfaceContactStd(name='SurfaceToSurfaceContact', createStepName='Initial', master=master_surface_region, slave=slave_surface_region, sliding=FINITE, thickness=ON, interactionProperty='Interaction Property', adjustMethod=NONE, initialClearance=OMIT, datumAxis=None, clearanceRegion=None)

import mesh

elemType = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
pickedRegions = switchPart.faces.getSequenceFromMask(mask=('[#3f]',),)
switchPart.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)

switchPart.seedEdgeBySize(edges=swithInstance.edges, size=0.25, deviationFactor=0.1, constraint=FINER)
switchPart.generateMesh()

import job

mdb.Job(name='SwitchContactJob', model='Electrical Switch', description='Contact analysis of switch', type=ANALYSIS, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['SwitchContactJob'].submit(consistencyChecking=OFF)
mdb.jobs['SwitchContactJob'].waitForCompletion()

import visualization

switchViewport = session.Viewport(name='Switch contact analysis Viewport')
switch_Odb_Path = 'SwitchContactJob.odb'
odb_object = session.openOdb(name=switch_Odb_Path)
switchViewport.setValues(displayedObject=odb_object)
switchViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))

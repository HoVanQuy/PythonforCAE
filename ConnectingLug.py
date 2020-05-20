from abaqus import*
from abaqusConstants import*
import regionToolset

session.viewports['Viewport: 1'].setValues(displayedObject=None)

mdb.models.changeKey(fromName='Model-1', toName='Connecting Lug')
conLugModel = mdb.models['Connecting Lug']

import sketch
import part

#Use ArcByCenterEnds() to create Arc by center and 2 point
#Use CircleByCenterPerimeter() to create Circle by center and perimeter
conLugSketch = conLugModel.ConstrainedSketch(name='Conlug Profile', sheetSize=1)
conLugSketch.Line(point1=(0,0.025), point2=(-0.125,0.025))
conLugSketch.Line(point1=(-0.125,0.025), point2=(-0.125,-0.025))
conLugSketch.Line(point1=(-0.125,-0.025), point2=(0,-0.025))
conLugSketch.ArcByCenterEnds(center=(0,0), point1=(0,-0.025), point2=(0,0.025))
conLugSketch.CircleByCenterPerimeter(center=(0,0), point1=(0,0.015))

conLugPart = conLugModel.Part(name='Connecting Lug', dimensionality=THREE_D, type=DEFORMABLE_BODY)
conLugPart.BaseSolidExtrude(sketch=conLugSketch, depth=0.02)

import material

conLugMaterial = conLugModel.Material(name='Steel')
conLugMaterial.Density(table=((7800,), ))
conLugMaterial.Elastic(table=((200E9,0.3), ))

import section

conLugSection = conLugModel.HomogeneousSolidSection(name='Connecting Lug Section', material='Steel')
conLug_region = (conLugPart.cells,)
conLugPart.SectionAssignment(region=conLug_region, sectionName='Connecting Lug Section')

import assembly

conLugAssembly = conLugModel.rootAssembly
conLugInstance = conLugAssembly.Instance(name='Connecting Lug Instance', part=conLugPart, dependent=ON)

import step

conLugModel.StaticStep(name='Apply Load', previous='Initial', description='Load is applied during this step')

conLugModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Required Field Outputs')
conLugModel.fieldOutputRequests['Required Field Outputs'].setValues(variables=('S','E','PEMAG','U','RF','CF'))

#Definition of history output requests
#Create new history output and delete existing one. This is done only for illustration purposes
conLugModel.HistoryOutputRequest(name='Default History Outputs', createStepName='Apply Load', variables=PRESELECT)
del conLugModel.historyOutputRequests['H-Output-1']

#Identify the face by partitioning for load application
#To partition part, we will create datum plane and then use PartitionCellByDatumPlane
conLugPart.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0)
conLugPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0)
conLugPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=-0.025)

conLugCells = conLugPart.cells

allconLugCells = conLugCells.findAt((-0.0625,0,0.01),)
conLugPart.PartitionCellByDatumPlane(datumPlane=conLugPart.datums[3], cells=allconLugCells)

allconLugCells = conLugCells.findAt((-0.0625,0.02,0.01),)
conLugPart.PartitionCellByDatumPlane(datumPlane=conLugPart.datums[4], cells=allconLugCells)

allconLugCells = conLugCells.findAt((-0.0625,-0.02,0.01),)
conLugPart.PartitionCellByDatumPlane(datumPlane=conLugPart.datums[4], cells=allconLugCells)

allconLugCells = conLugCells.findAt((-0.0625,0.02,0.01),)
conLugPart.PartitionCellByDatumPlane(datumPlane=conLugPart.datums[5], cells=allconLugCells)

allconLugCells = conLugCells.findAt((-0.0625,-0.02,0.01),)
conLugPart.PartitionCellByDatumPlane(datumPlane=conLugPart.datums[5], cells=allconLugCells)


#Finding bottom curved surface so that it can be used for loading
#Now we have already partitioned part along YZ plane, wehave to find 2 face to apply load
#Face 1
conLug_bottomcurve_surface_point1 = (0.015/sqrt(2),-0.015/sqrt(2),0.01)
conLug_bottomcurve_surface1 = conLugInstance.faces.findAt((conLug_bottomcurve_surface_point1,))
conLugAssembly.Surface(side1Faces=conLug_bottomcurve_surface1, name='Bottom Curved Surface 1')
conLug_load_region1 = conLugAssembly.surfaces['Bottom Curved Surface 1']
#Face 2
conLug_bottomcurve_surface_point2 = (-0.015/sqrt(2),-0.015/sqrt(2),0.01)
conLug_bottomcurve_surface2 = conLugInstance.faces.findAt((conLug_bottomcurve_surface_point2,))
conLugAssembly.Surface(side1Faces=conLug_bottomcurve_surface2, name='Bottom Curved Surface 2')
conLug_load_region2 = conLugAssembly.surfaces['Bottom Curved Surface 2']
#Apply the pressure loads
conLugModel.Pressure(name='Load-1', createStepName='Apply Load', region=conLug_load_region1, distributionType=UNIFORM, magnitude=2.5E7, amplitude=UNSET)
conLugModel.Pressure(name='Load-2', createStepName='Apply Load', region=conLug_load_region2, distributionType=UNIFORM, magnitude=2.5E7, amplitude=UNSET)

#Identify faces and apply boundary conditions
#Now we have already partitioned part along XZ plane, we have to identify 2 faces that represent the fixed end and fix them
#Face 1
bc_face1_point_x = -0.125
bc_face1_point_y = 0.0125
bc_face1_point_z = 0.01

bc_face1_point = (bc_face1_point_x, bc_face1_point_y, bc_face1_point_z)
bc_face1 = conLugInstance.faces.findAt((bc_face1_point,))
bc_face1_region = regionToolset.Region(faces=bc_face1)

#Face 2
bc_face2_point_x = -0.125
bc_face2_point_y = -0.0125
bc_face2_point_z = 0.01

bc_face2_point = (bc_face2_point_x, bc_face2_point_y, bc_face2_point_z)
bc_face2 = conLugInstance.faces.findAt((bc_face2_point,))
bc_face2_region = regionToolset.Region(faces=bc_face2)

#Apply EncastreBC
conLugModel.EncastreBC(name='Encastre top face', createStepName='Initial', region=bc_face1_region)
conLugModel.EncastreBC(name='Encastre bottom face', createStepName='Initial', region=bc_face2_region)

import mesh

element_type_for_mesh = mesh.ElemType(elemCode=C3D20R, elemLibrary=STANDARD, kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT)
conLugMeshRegion = (allconLugCells,)
conLugPart.setElementType(regions=conLugMeshRegion, elemTypes=(element_type_for_mesh,))
conLugPart.seedPart(size=0.0025, deviationFactor=0.1)
conLugPart.generateMesh()

import job

mdb.Job(name='ConnectingLugJob', model='Connecting Lug', type=ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, description='Simulating a connecting lug', parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT, numDomains=1, userSubroutine='', numCpus=1, memory=50, memoryUnits=PERCENTAGE, scratch='', echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF)

mdb.jobs['ConnectingLugJob'].submit(consistencyChecking=OFF)
mdb.jobs['ConnectingLugJob'].waitForCompletion()

import visualization

connecting_lug_viewport = session.Viewport(name='Connecting Lug Results Viewport')
connecting_lug_Odb_Path = 'ConnectingLugJob.odb'
odb_object_1 = session.openOdb(name=connecting_lug_Odb_Path)
connecting_lug_viewport.setValues(displayedObject=odb_object_1)
connecting_lug_viewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))

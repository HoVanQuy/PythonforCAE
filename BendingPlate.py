from abaqus import*
from abaqusConstants import*
import regionToolset

mdb.models.changeKey(fromName='Model-1', toName='Bending Plate')
plateModel = mdb.models['Bending Plate']

import sketch
import part

plateSketch = plateModel.ConstrainedSketch(name='Plate Sketch', sheetSize=3)
plateSketch.rectangle(point1=(0,0), point2=(1,0.4))

platePart = plateModel.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
platePart.BaseShell(sketch=plateSketch)

import material

plateMaterial = plateModel.Material(name='Steel')
plateMaterial.Density(table=((7800,),))
plateMaterial.Elastic(table=((200E9,0.29),))

import section
#Create shell section using HomogeneousShellSection()
plateSection = plateModel.HomogeneousShellSection(name='Plate Section', material='Steel', thicknessType=UNIFORM, thickness=0.01)
#Identify a point on plate and assign them to region
point_on_plate = (0.5,0.2,0)
face_on_plate = platePart.faces.findAt((point_on_plate,))
region_of_plate = (face_on_plate,)
platePart.SectionAssignment(region=region_of_plate, sectionName='Plate Section', offset=0, offsetType=MIDDLE_SURFACE, offsetField='')

import assembly

plateAssembly = plateModel.rootAssembly
plateInstance = plateAssembly.Instance(name='Plate Instance', part=platePart, dependent=ON)

import step

plateModel.StaticStep(name='Load Step', previous='Initial', description='Apply pressure in this step', nlgeom=ON)

plateModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Required Field Outputs')
plateModel.fieldOutputRequests['Required Field Outputs'].setValues(variables=('S','RF','UT','U'))

plateModel.HistoryOutputRequest(name='Default History Outputs', createStepName='Load Step', variables=PRESELECT)
del plateModel.historyOutputRequests['H-Output-1']

#Partitioning
#Create datum points using DatumPointByCoordinate()
platePart.DatumPointByCoordinate(coords=(0.5,0,0))
platePart.DatumPointByCoordinate(coords=(0.5,0.4,0))
datums_keys = platePart.datums.keys()
datums_keys.sort()
datum_point1 = platePart.datums[datums_keys[0]]
datum_point2 = platePart.datums[datums_keys[1]]
#Select entire top face using findAt() and partition using 2 points
point_on_face_to_partition = (0.5,0.2,0)
face_to_partition = platePart.faces.findAt((point_on_face_to_partition,))
platePart.PartitionFaceByShortestPath(point1=datum_point1, point2=datum_point2, faces=face_to_partition)

#Identify left edge and fix it
edge_to_fix = plateInstance.edges.findAt(((0,0.2,0),))
edge_to_fix_region = regionToolset.Region(edges=edge_to_fix)
plateModel.EncastreBC(name='Encastre Edge', createStepName='Initial', region=edge_to_fix_region)

#Identify right edge and apply rolling condition using DisplacementBC()
edge_that_rolls = plateInstance.edges.findAt(((1,0.2,0),))
edge_that_rolls_region = regionToolset.Region(edges=edge_that_rolls)
plateModel.DisplacementBC(name='Rolling Edge', createStepName='Initial', region=edge_that_rolls_region, u1=UNSET, u2=UNSET, u3=SET, amplitude=UNSET, distributionType=UNIFORM)

#Define faces and then apply pressure
pressure_faces = plateInstance.faces.findAt(((0.25,0.2,0),),((0.75,0.2,0),))
pressure_faces_region = regionToolset.Region(side1Faces=pressure_faces)
plateModel.Pressure(name='Apply Pressure', createStepName='Load Step', region=pressure_faces_region, magnitude=2E3)

import mesh

element_type_for_mesh = mesh.ElemType(elemCode=S8R5, elemLibrary=STANDARD)
plate_mesh_region = region_of_plate
platePart.setElementType(regions=plate_mesh_region, elemTypes=(element_type_for_mesh,))
#Identify edges and then seeding them by number
horizontal_edges = platePart.edges.findAt(((0.25,0,0),),((0.75,0,0),),((0.75,0.4,0),),((0.25,0.4,0),))
vertical_edges = platePart.edges.findAt(((0,0.2,0),),((1,0.2,0),))
platePart.seedEdgeByNumber(edges=horizontal_edges, number=20)
platePart.seedEdgeByNumber(edges=vertical_edges, number=16)
platePart.generateMesh()

import job

mdb.Job(name='PlateJob', model='Bending Plate', type=ANALYSIS, description='Job simulates the bending of plate under load of 2MPa')

mdb.jobs['PlateJob'].submit(consistencyChecking=OFF)
mdb.jobs['PlateJob'].waitForCompletion()

import visualization

plate_viewport = session.Viewport(name='Bending Plate Results Viewport')
plate_path = 'PlateJob.odb'
plate_odb_object = session.openOdb(name=plate_path)
plate_viewport.setValues(displayedObject=plate_odb_object)
plate_viewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))

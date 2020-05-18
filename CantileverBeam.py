from abaqus import*
from abaqusConstants import*
import regionToolset

session.viewports['Viewport: 1'].setValues(displayedObject=None)

mdb.models.changeKey(fromName='Model-1', toName='Cantilever Beam')
cantileverModel = mdb.models['Cantilever Beam']

import sketch
import part
#Rectangke() method is used to draw the rectangular cross section
cantileverSketch = cantileverModel.ConstrainedSketch(name='Beam Cross Section', sheetSize=5)
cantileverSketch.rectangle(point1=(0,0), point2=(25,20))
#BaseSolidExtrude() is used to create a feature object
cantileverPart = cantileverModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
cantileverPart.BaseSolidExtrude(sketch=cantileverSketch, depth=200)

import material
cantileverMaterial = cantileverModel.Material(name='Steel')
cantileverMaterial.Density(table=((7800, ), ))
cantileverMaterial.Elastic(table=((200E9,0.29), ))

import section
#Create a solid section using HomogeneousSolidSection() method
cantileverSection = cantileverModel.HomogeneousSolidSection(name='Cantilever Section', material='Steel')
#Identify all the cells of part and assign them to region.
#The comma used here is to indicate that we are creating a Region object, which wuold be a sequence of cells
#This sequence can be vertex objects, edge objects, node objects or face objects
region_of_cantilever = (cantileverPart.cells,)
cantileverPart.SectionAssignment(region=region_of_cantilever, sectionName='Cantilever Section')

import assembly
cantileverAssembly = cantileverModel.rootAssembly
cantileverInstance = cantileverAssembly.Instance(name='Cantilever Instance', part=cantileverPart, dependent=ON)

import step
cantileverModel.StaticStep(name='Apply Pressure Load', previous='Initial', description='Load is applied now')

#Definition of field output requests
cantileverModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Required Field Outputs')
cantileverModel.fieldOutputRequests['Required Field Outputs'].setValues(variables=('S','E','PEMAG','U','RF','CF'))

#Apply pressure loads
#First, indentify the face on which pressure load is applied
#Use findAt() method
point_on_topface_xcoord = 12.5
point_on_topface_ycoord = 20
point_on_topface_zcoord = 100
point_top_face = (point_on_topface_xcoord, point_on_topface_ycoord, point_on_topface_zcoord)
top_face = cantileverInstance.faces.findAt((point_top_face,))
#Convert indentified face into region
top_face_region = regionToolset.Region(side1Faces=top_face)

cantileverModel.Pressure(name='Uniform Applied Pressure', createStepName='Apply Pressure Load', region=top_face_region, distributionType=UNIFORM, magnitude=0.5, amplitude=UNSET)

#Apply boundary conditions
point_on_fixedface_xcoord = 12.5
point_on_fixedface_ycoord = 10
point_on_fixedface_zcoord = 0
point_on_fixed_face = (point_on_fixedface_xcoord, point_on_fixedface_ycoord, point_on_fixedface_zcoord)
fixed_face = cantileverInstance.faces.findAt((point_on_fixed_face,))
fixed_face_region = regionToolset.Region(faces=fixed_face)
#Note that boundary conditions applied in the initial step
cantileverModel.EncastreBC(name='Fix one end', createStepName='Initial', region=fixed_face_region)

#Mesh creation
import mesh

element_type_for_mesh = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT)
#The region for meshing is selected from all the cells of the beam
cantilever_interior_xcoord = 12.5
cantilever_interior_ycoord = 10
cantilever_interior_zcoord = 100
cantileverCells = cantileverPart.cells
requiredcantileverCells = cantileverCells.findAt((cantilever_interior_xcoord, cantilever_interior_ycoord, cantilever_interior_zcoord),)

cantilever_mesh_region = (requiredcantileverCells,)
#There is a comma at the end. This means that input for region is a sequence of cells
#Once we have chosen mesh region, pre-defined element type is assigned which is followed by sedding part
cantileverPart.setElementType(regions=cantilever_mesh_region, elemTypes=(element_type_for_mesh,))
#You can reduce value of 'size' to generate finer mesh
cantileverPart.seedPart(size=10, deviationFactor=0.1)
cantileverPart.generateMesh()

#Create job and running
import job

mdb.Job(name='CantileverJob', model='Cantilever Beam', type=ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, description='Simulating a cantilever beam', parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT, numDomains=1, userSubroutine='', numCpus=1, memory=50, memoryUnits=PERCENTAGE, scratch='', echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF)

mdb.jobs['CantileverJob'].submit(consistencyChecking=OFF)
mdb.jobs['CantileverJob'].waitForCompletion()

#Post processing
import visualization

cantilever_viewport = session.Viewport(name='Cantilever Beam Results viewport')
cantilever_odb_path = 'CantileverJob.odb'
cantilever_odb_object = session.openOdb(name=cantilever_odb_path)
cantilever_viewport.setValues(displayedObject=cantilever_odb_object)
cantilever_viewport.odbDisplay.display.setValues(plotState=(DEFORMED,))

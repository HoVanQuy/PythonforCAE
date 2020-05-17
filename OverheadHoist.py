#Creating an analysis model of an overhead hoist
from abaqus import* #Import the required ABAQUS modules
from abaqusConstants import* #Import the symbolic constants
import regionToolset #Access the objects of Region() method inside regionToolset module

#Make ABAQUS viewport display nothing
session.viewports['Viewport: 1'].setValues(displayedObject=None)

#Model creation
#Default, ABAQUS creates model named 'Model-1'
#Use changeKey() method to change name of model.mdb (model database)
mdb.models.changeKey(fromName='Model-1', toName='Overhoist')
overhoistModel = mdb.models['Overhoist']

#Part creation
import sketch
import part

#Define a sketch by using the ConstrainedSketch() method. This method in turn has Line() method
overhoistSketch = overhoistModel.ConstrainedSketch(name='overhoist sketch 2D', sheetSize=10.0)
overhoistSketch.Line(point1=(0,0), point2=(1,0))
overhoistSketch.Line(point1=(1,0), point2=(2,0))
overhoistSketch.Line(point1=(0,0), point2=(0.5,0.866))
overhoistSketch.Line(point1=(0.5,0.866), point2=(1.5,0.866))
overhoistSketch.Line(point1=(1.5,0.866), point2=(2,0))
overhoistSketch.Line(point1=(0.5,0.866), point2=(1,0))
overhoistSketch.Line(point1=(1,0), point2=(1.5,0.866))

#Create Part unsing Part() method
#TWO_D_PLANAR is SYMBOLIC CONSTANTS
#BaseWire() method to create feature object based on the sketch
overhoistPart = overhoistModel.Part(name='overhoist', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
overhoistPart.BaseWire(sketch=overhoistSketch)

#Material creation
import material #Access to objects relating materials
overhoistMaterial = overhoistModel.Material(name='Overhoist Steel')
#Input to Density() a table with density value with respect to temperature. Here we don't need that
#Elastic() it is a table with Young's modulus with respect to Poissons' ratio
overhoistMaterial.Density(table=((7800, ), ))
overhoistMaterial.Elastic(table=((200E9,0.3), ))

#Section creation and assignment
import section
#Create a truss section using TrussSection()
overhoistSection = overhoistModel.TrussSection(name='Overhoist Section', material='Overhoist Steel', area=1.963E-5)
#Assign the created section using findAt() to find the edges at provided vertices of the part
#With the edges, we can create a region being assigned to the created Section
overhoist_section_edges = overhoistPart.edges.findAt(((0.5,0,0), ),((1.50,0,0), ),((0.25,0.433,0), ),((1,0.866,0), ),((1.75,0.433,0), ),((0.75,0.433,0), ),((1.25,0.433,0),))
overhoist_region = regionToolset.Region(edges=overhoist_section_edges)
overhoistPart.SectionAssignment(region=overhoist_region, sectionName='Overhoist Section')

#Assembly creation
import assembly
#The rootAssembly is an assembly object of Model object
overhoistAssembly = overhoistModel.rootAssembly
#Create instance using Instance() method. By default, the 'dependent' parameter is set to OFF
overhoistInstance = overhoistAssembly.Instance(name='Overhoist Instance', part=overhoistPart, dependent=ON)

#Step creation
import step
#Create static step using StaticStep(). This step (loading) next to 'Initial' step created by default
overhoistModel.StaticStep(name='Loading Step', previous='Initial', description='Loads will be applied in this step')

#Define field output requests
overhoistModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Required Field Outputs')
overhoistModel.fieldOutputRequests['Required Field Outputs'].setValues(variables=('S','U','RF','CF'))

#Apply loads at vertex(1,0,0)
#ConcentratedForce() is used
vertex_for_force = (1,0,0)
force_vertex = overhoistInstance.vertices.findAt((vertex_for_force,))
overhoistModel.ConcentratedForce(name='Force1', createStepName='Loading Step', region=(force_vertex,), cf2=-1000, distributionType=UNIFORM)

#Apply boundary conditions
vertex_coords_encastre = (0,0,0)
vertex_coords_rolling = (2,0,0)
vertices_for_encastre = overhoistInstance.vertices.findAt((vertex_coords_encastre,))
vertices_for_rolling = overhoistInstance.vertices.findAt((vertex_coords_rolling,))
#EncastreBC() is used to Encastre joint.
#DisplacementBC() is used to displacement behavior on the region
#Symbolic constant 'SET' means we have constrained the dofs
#In this example, we have constrained the translation DOFS in the y direction
overhoistModel.EncastreBC(name='EncastreBC', createStepName='Initial', region=(vertices_for_encastre,))
overhoistModel.DisplacementBC(name='RollingjointBC', createStepName='Initial', region=(vertices_for_rolling,), u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM)

#Mesh creation
import mesh
#Use predefined regions for element type definition and for seeding edges
#T2D2 is the 2D element type for truss elements
#Define mesh size by seeding edges by a number
#Use generateMesh() to have a finer mesh
element_type_for_mesh = mesh.ElemType(elemCode=T2D2, elemLibrary=STANDARD)
overhoistPart.setElementType(regions=overhoist_region, elemTypes=(element_type_for_mesh,))
overhoistPart.seedEdgeByNumber(edges=overhoist_section_edges,number=2)
overhoistPart.generateMesh()

#Job creation
import job
#The Job() is used to create job. Make sure enter correct name of model
#Most of arguments entered here are not mandatory. You can edit values based on your requirements
mdb.Job(name='OverhoistAnalysisJob', model='Overhoist', type=ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, description='Analysis of an overhoist crane with concentrated loads', parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT, numDomains=1, userSubroutine='', numCpus=1, memory=50, memoryUnits=PERCENTAGE, scratch='', echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF)
#The submit() is used to submit job for analysis
#The waitForCompletion() makes ABAQUS wait till job is fully excuted
mdb.jobs['OverhoistAnalysisJob'].submit(consistencyChecking=OFF)
mdb.jobs['OverhoistAnalysisJob'].waitForCompletion()

#Post processing
import visualization
#Save the odb object and path to variables used for visualization.
#The node and element labels are turned on for better clarity
#The viewport size can also be set
overhoistPath = 'OverhoistAnalysisJob.odb'
odb_object = session.openOdb(name=overhoistPath)
session.viewports['Viewport: 1'].setValues(displayedObject=odb_object)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED,))
overhoist_deformed_viewport = session.Viewport(name='Overhoist in Deformed State')
overhoist_deformed_viewport.setValues(displayedObject=odb_object)
overhoist_deformed_viewport.odbDisplay.display.setValues(plotState=(UNDEFORMED, DEFORMED,))
overhoist_deformed_viewport.odbDisplay.commonOptions.setValues(nodeLabels=ON)
overhoist_deformed_viewport.odbDisplay.commonOptions.setValues(elemLabels=ON)
overhoist_deformed_viewport.setValues(origin=(0,0), width=150, height=150)

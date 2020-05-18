from abaqus import *
from abaqusConstants import*
import regionToolset
session.viewports['Viewport: 1'].setValues(displayedObject=None)
mdb.models.changeKey(fromName='Model-1', toName='Cantilever Beam')
cantileverModel = mdb.models['Cantilever Beam']
import sketch
import part
cantileverSketch = cantileverModel.ConstrainedSketch(name='Beam Cross Section', sheetSize=5)
cantileverSketch.rectangle(point1=(0.0,0.0), point2=(25.0,20.0))
cantileverPart = cantileverModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
cantileverPart.BaseSolidExtrude(sketch=cantileverSketch, depth=200.0)
import material
cantileverMaterial = cantileverModel.Material(name='Steel')
cantileverMaterial.Density(table=((7800, ),     ))
cantileverMaterial.Elastic(table=((200E9, 0.29),  ))
import section
cantileverSection = cantileverModel.HomogeneousSolidSection(name='Cantilever Section', material='Steel')
region_of_cantilever = (cantileverPart.cells,)
cantileverPart.SectionAssignment(region=region_of_cantilever, sectionName='Cantilever Section')
import assembly
cantileverAssembly = cantileverModel.rootAssembly
cantileverInstance = cantileverAssembly.Instance(name='Cantilever Instance', part=cantileverPart, dependent=ON)
import step
cantileverModel.StaticStep(name='Apply Pressure Load', previous='Initial', description='Load is applied now')
cantileverModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Required Field Outputs')
cantileverModel.fieldOutputRequests['Required Field Outputs'].setValues(variables=('S', 'E', 'PEMAG', 'U', 'RF', 'CF'))
point_on_topface_xcoord = 12.5
point_on_topface_ycoord = 20.0
point_on_topface_zcoord = 100.0
point_top_face = (point_on_topface_xcoord,point_on_topface_ycoord,point_on_topface_zcoord)
top_face = cantileverInstance.faces.findAt((point_top_face,))
top_face_region=regionToolset.Region(side1Faces=top_face)
cantileverModel.Pressure(name='Uniform Applied Pressure', createStepName='Apply Pressure Load', region=top_face_region, distributionType=UNIFORM, magnitude=0.5, amplitude=UNSET)
point_on_fixedface_xcoord = 12.5
point_on_fixedface_ycoord = 10.0
point_on_fixedface_zcoord = 0.0
point_on_fixed_face = (point_on_fixedface_xcoord, point_on_fixedface_ycoord, point_on_fixedface_zcoord)
fixed_face = cantileverInstance.faces.findAt((point_on_fixed_face,))
fixed_face_region = regionToolset.Region(faces=fixed_face)
cantileverModel.EncastreBC(name='Fix one end', createStepName='Initial', region=fixed_face_region)
import mesh
elem_type_for_mesh = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT)
cantilever_interior_xcoord = 12.5
cantilever_interior_ycoord = 10.0
cantilever_interior_zcoord = 100.0
cantileverCells = cantileverPart.cells
requiredcantileverCells = cantileverCells.findAt((cantilever_interior_xcoord,cantilever_interior_ycoord,cantilever_interior_zcoord),)
cantilever_mesh_region=(requiredcantileverCells,)
cantileverPart.setElementType(regions=cantilever_mesh_region, elemTypes=(elem_type_for_mesh,))
cantileverPart.seedPart(size=10.0, deviationFactor=0.1)
cantileverPart.generateMesh()
import job
mdb.Job(name='CantilverJob', model='Cantilever Beam', type=ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, description='Simulating a cantilever beam', parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT, numDomains=1, userSubroutine='', numCpus=1, memory=50, memoryUnits=PERCENTAGE, scratch='', echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF)
mdb.jobs['CantilverJob'].submit(consistencyChecking=OFF)
mdb.jobs['CantilverJob'].waitForCompletion()
import visualization
cantilever_viewport = session.Viewport(name='Cantilever Beam Results Viewport')
cantilever_odb_path = 'CantilverJob.odb'
cantilever_odb_object = session.openOdb(name=cantilever_odb_path)
cantilever_viewport.setValues(displayedObject=cantilever_odb_object)
cantilever_viewport.odbDisplay.display.setValues(plotState=(DEFORMED, ))

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
#Create a solid section using HomogenousSolidSection() method
cantileverSection = cantileverModel.HomogenousSolidSection(name='Cantilever Section', material='Steel')
#Identify all the cells of part and assign them to region.
#The comma used here is to indicate that we are creating a Region object, which wuold be a sequence of cells
#This sequence can be vertex objects, edge objects, node objects or face objects
region_of_cantilever = (cantileverPart.cells,)

import assembly
cantileverAssembly = cantileverModel.rootAssembly
cantileverInstance = cantileverAssembly.Instance(name='Cantilever Instance', part=cantileverPart, dependent=ON)

import step

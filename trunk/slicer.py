import vtk
import time
import os
from Tkinter import Tk
from tkFileDialog import askopenfilename

class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera): #defines all the mouse interactions for the render views
    def __init__(self,parent=None):
        self.AddObserver("MiddleButtonPressEvent",self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent",self.middleButtonReleaseEvent)

    def middleButtonPressEvent(self,obj,event):
        self.OnMiddleButtonDown()
        return
        
    def middleButtonReleaseEvent(self,obj,event):
        self.OnMiddleButtonUp()
        return 

class slicer():
    def OpenModel(self, filename):
        self.filename = filename
        self.reader = vtk.vtkSTLReader()
        self.reader.MergingOn()
        self.reader.SetFileName(str(self.filename))
        self.clean = vtk.vtkCleanPolyData()
        self.clean.SetInputConnection(self.reader.GetOutputPort())
        self.clean.PointMergingOn()
         
    def slice(self):
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        self.slicingplane=vtk.vtkPlane()
        self.slicingplane.SetOrigin(0,0,20)
        self.slicingplane.SetNormal(0,0,1)
        
        self.cutter=vtk.vtkCutter()         #create cutter
        self.cutter.SetCutFunction(self.slicingplane)
        self.cutter.SetInputConnection(self.clean.GetOutputPort())
        self.cutter.Update()
        
        self.cutStrips = vtk.vtkStripper() #Forms loops (closed polylines) from cutter
        self.cutStrips.SetInputConnection(self.cutter.GetOutputPort())
        self.cutStrips.Update()
        self.cutPoly = vtk.vtkPolyData() #This trick defines polygons as polyline loop
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        
        self.cutTriangles = vtk.vtkTriangleFilter()         # Triangle filter
        self.cutTriangles.SetInput(self.cutPoly)
        self.cutTriangles.Update()
        
        self.cutterMapper=vtk.vtkPolyDataMapper()        #cutter mapper
        self.cutterMapper.SetInput(self.cutPoly)
        self.cutterMapper.SetInputConnection(self.cutTriangles.GetOutputPort())
        
        self.slicingplaneActor=vtk.vtkActor()         #create plane actor
        self.slicingplaneActor.GetProperty().SetColor(1.0,1.0,1.0)
        self.slicingplaneActor.GetProperty().SetLineWidth(4)
        self.slicingplaneActor.SetMapper(self.cutterMapper)
 
        self.sliceren = vtk.vtkRenderer()
        self.sliceren.AddActor(self.slicingplaneActor)
        self.sliceren.ResetCamera()
        self.sliceren.ResetCameraClippingRange(-100.0,100.0,-100.0,100.0,-100.0,100.0)
        self.sliceren.InteractiveOff() #why doesnt this work?!
        
        #Add renderer to renderwindow and render
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.sliceren)
        self.renWin.SetSize(self.imageheight, self.imagewidth)
        self.renWin.SetWindowName("3DLP STL SLicer")      
        self.renWin.Render()
        
        os.chdir(os.getcwd()+"\\slices") #change to slices directory       
        x = self.startingdepth
        layercount = 0
        starttime = time.time()
        while x < self.endingdepth:
            x += self.layerincrement
            layercount = layercount + 1
            self.UpdateSlicingPlane(x)
            self.WindowToImage("slice%s.png"%(str(layercount).zfill(4)))

        elapsedtime = time.time() - starttime
        print elapsedtime
        print layercount

    def UpdateSlicingPlane(self, value):
        #self.previousPlaneZVal = self.slicingplane.GetOrigin()[2] #pull Z coordinate off plane origin 
        self.slicingplane.SetOrigin(0,0,value)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.sliceren.Render()
        self.sliceren.Render()
        self.renWin.Render()
        
    def WindowToImage(self, filename):
        self.w2i = vtk.vtkWindowToImageFilter()
        self.writer = vtk.vtkPNGWriter()
        self.w2i.SetInput(self.renWin)
        self.w2i.Update()
        self.writer.SetInputConnection(self.w2i.GetOutputPort())
        self.writer.SetFileName(filename)
        #writer.WriteToMemoryOn()
        self.writer.Write()
              
#slicer = slicer()
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
#slicer.OpenModel(filename)
#slicer.slice()
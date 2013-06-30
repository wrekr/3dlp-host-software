import vtk
import time
import os
import ConfigParser
import cPickle as pickle
import zipfile
import StringIO
import numpy
import Image
from vtk.util.numpy_support import vtk_to_numpy

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
    def __init__(self, parent):
        self.parent = parent
        self.outputFile = self.parent.outputFile
        os.chdir(os.path.split(str(self.outputFile))[0]) #change to base dir of the selected filename
        self.zfile = zipfile.ZipFile(os.path.split(str(self.outputFile))[1], 'w')
         
    def close_window(self, iren):
        render_window = iren.GetRenderWindow()
        render_window.Finalize()
        #iren.TerminateApp()
    
    def slice(self):
        #create a plane to cut,here it cuts in the XY direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        self.slicingplane=vtk.vtkPlane()
        self.slicingplane.SetOrigin(0,0,0)
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
        
        self.sliceCorrelations = []

        x = self.startingdepth
        layercount = 0
        starttime = time.time()
        while x < self.endingdepth:
            x += self.layerincrement
            layercount = layercount + 1
            self.UpdateSlicingPlane(x)
            self.WindowToImage("slice%s.png"%(str(layercount).zfill(4)))
            self.sliceCorrelations.append([layercount,x]) #store correlations between slice plane and layer number for later visualization in 3DLP Host
            
        self.close_window(self.sliceren)
        del self.sliceren

        elapsedtime = time.time() - starttime
        print elapsedtime
        print layercount
        self.GenerateConfigFile()

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

        vtk_image = self.w2i.GetOutput()
        
        height, width, _ = vtk_image.GetDimensions()
        vtk_array = vtk_image.GetPointData().GetScalars()
        components = vtk_array.GetNumberOfComponents()
        
        array = vtk_to_numpy(vtk_array).reshape(height, width, components)
        
        stringio3 = StringIO.StringIO()
        im = Image.fromarray(numpy.uint8(array))
        im.save(stringio3, "PNG")
        self.zfile.writestr("\\slices\\" + filename, stringio3.getvalue())
         
    def GenerateConfigFile(self):
        Config = ConfigParser.ConfigParser()
        Config.add_section('print_settings')
        Config.set('print_settings', 'layer_thickness', self.layerincrement)
        Config.add_section('preview_settings')
        base, file = os.path.split(str(self.filename)) #can't be QString
        Config.set('preview_settings', 'STL_name', file)
        
        stringio = StringIO.StringIO()
        Config.write(stringio)        
 
        self.zfile.writestr("printconfiguration.ini", stringio.getvalue())#arcname = "printconfiguration.ini")

        stringio2 = StringIO.StringIO()
        pickle.dump(self.sliceCorrelations, stringio2)
        
        self.zfile.writestr("slices.p", stringio2.getvalue()) #pickle and save the layer-plane correlations 
        
        self.zfile.write(str(self.filename), arcname = file)    
        
        self.zfile.close()
               
#slicer = slicer()
#slicer.imagewidth = 640
#slicer.imageheight = 480
#slicer.startingdepth = -2
#slicer.endingdepth = 4
#slicer.layerincrement = .1
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
#slicer.OpenModel(filename)
#slicer.slice()
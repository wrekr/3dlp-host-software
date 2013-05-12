import slicer
import vtk
import sys
from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
from slicer_gui import Ui_MainWindow
from slicer_settings_dialog_gui import Ui_Dialog
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

###IDEA TO SPEED UP SLICER: slice in one thread, send data through queue to another thread which saves data to hard drive at its leisure

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

class StartSettingsDialog(QtGui.QDialog, Ui_Dialog, Ui_MainWindow):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        
    def accept(self):
        self.emit(QtCore.SIGNAL('ApplySettings()'))
        self.reject()

    def quit(self):
        self.reject()

    # Create a class for our main window
class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        pass
        #self.ModelView.resize(self.ui.ModelFrame.geometry().width()-15,self.ui.ModelFrame.geometry().height()-39)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Slicer", None, QtGui.QApplication.UnicodeUTF8))

        #load previous settings from config file here:
        self.imageHeight = ""
        self.imageWidth = ""
        self.layerThickness = ""
        self.startingDepth = ""
        self.endingDepth = ""
        self.slicingIncrement = ""
        self.slicingplane = "XZ"
        self.slicingplaneDict = {"XZ":0, "XY":1, "YZ":2}

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(.4,.4,.4)
        
        # create the modelview widget
        self.ModelView = QVTKRenderWindowInteractor(self.ui.ModelFrame)
        self.ModelView.SetInteractorStyle(MyInteractorStyle())
        self.ModelView.Initialize()
        self.ModelView.Start()

        self.renWin=self.ModelView.GetRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.ModelView.show()

        self.ModelView.resize(1006-17,716-39)
        #self.ModelView.resize(self.ui.ModelFrame.geometry().width()-1,self.ui.ModelFrame.geometry().height()-1)

    def OpenModel(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                QtGui.QMessageBox.critical(self, 'Error loading model',"You have already loaded a model into the slicer. Please restart to load another model.", QtGui.QMessageBox.Ok)
                return 
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            pass
        
        self.filename = QtGui.QFileDialog.getOpenFileName()
#        self.ui.displayfilenamelabel.setText(self.filename)

        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(str(self.filename))
        
        self.plane=vtk.vtkPlane()
        self.plane.SetOrigin(0,0,20)
        self.plane.SetNormal(0,0,1)
        
        self.extrude = vtk.vtkLinearExtrusionFilter()
        self.extrude.SetExtrusionType(2)
        self.extrude.SetScaleFactor(20.0)
         
        #self.polyDataOutput = self.reader.GetOutput()       
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
        
        self.mapper_plane = vtk.vtkPolyDataMapper()
        #self.mapper_plane.SetInput(self.extrude.GetOutputPort())
        
        self.planeActor = vtk.vtkActor()
        self.planeActor.GetProperty().SetColor(1,0,0)
        self.planeActor.GetProperty().SetOpacity(1)
        self.planeActor.SetMapper(self.mapper_plane)
        
        #create model actor
        self.modelActor = vtk.vtkActor()
        self.modelActor.GetProperty().SetColor(1,1,1)
        self.modelActor.GetProperty().SetOpacity(1)
        self.modelActor.SetMapper(self.mapper)

        #create outline mapper
        self.outline = vtk.vtkOutlineFilter()
        self.outline.SetInputConnection(self.reader.GetOutputPort())
        self.outlineMapper = vtk.vtkPolyDataMapper()
        self.outlineMapper.SetInputConnection(self.outline.GetOutputPort())
        
        #create outline actor
        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(self.outlineMapper)
        
        #create annotated cube anchor actor
        self.axesActor = vtk.vtkAnnotatedCubeActor();
        self.axesActor.SetXPlusFaceText('Right')
        self.axesActor.SetXMinusFaceText('Left')
        self.axesActor.SetYMinusFaceText('Front')
        self.axesActor.SetYPlusFaceText('Back')
        self.axesActor.SetZMinusFaceText('Bot')
        self.axesActor.SetZPlusFaceText('Top')
        self.axesActor.GetTextEdgesProperty().SetColor(.8,.8,.8)
        self.axesActor.GetZPlusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetZMinusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetXPlusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetXMinusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetYPlusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetYMinusFaceProperty().SetColor(.8,.8,.8)
        self.axesActor.GetTextEdgesProperty().SetLineWidth(2)
        self.axesActor.GetCubeProperty().SetColor(.2,.2,.2)
        self.axesActor.SetFaceTextScale(0.25)
        self.axesActor.SetZFaceTextRotation(90)
        self.ren.AddActor(self.modelActor)
        self.ren.AddActor(self.planeActor)
        self.ren.AddActor(self.outlineActor)
       
        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ren.ResetCamera()  
        self.ModelView.Render() #update model view
        self.transform = vtk.vtkTransform()
        self.CurrentXPosition = 0.0
        self.CurrentYPosition = 0.0
        self.CurrentZPosition = 0.0
        self.CurrentXRotation = 0.0
        self.CurrentYRotation = 0.0
        self.CurrentZRotation = 0.0
        self.CurrentXScale = 0.0
        self.CurrentYScale = 0.0
        self.CurrentZScale = 0.0
        self.ui.Transform_groupbox.setEnabled(True)
    
    def SliceModel(self):
        self.slicer = slicer.slicer(self)
        self.slicer.imageheight = int(self.imageHeight)
        self.slicer.imagewidth = int(self.imageWidth)
        # check to see if starting depth is less than ending depth!! this assumption is crucial
        self.slicer.startingdepth = float(self.startingDepth)
        self.slicer.endingdepth = float(self.endingDepth)
        self.slicer.layerincrement = float(self.slicingIncrement)
        self.slicer.OpenModel(self.filename)
        self.slicer.slice()
        
    def UpdateModelOpacity(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                opacity, ok = QtGui.QInputDialog.getText(self, 'Model Opacity', 'Enter the desired opacity (0-100):')
                if not ok: #the user hit the "cancel" button
                    return
                self.modelActor.GetProperty().SetOpacity(float(opacity)/100)
                self.ren.Render()
                self.ModelView.Render()
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            QtGui.QMessageBox.critical(self, 'Error setting opacity',"You must first load a model to change its opacity!", QtGui.QMessageBox.Ok)        
            
    def Update_Position_X(self, position):
        self.transform.Translate((float(position)-self.CurrentXPosition), 0.0, 0.0)
        self.CurrentXPosition = self.CurrentXPosition + (float(position)-self.CurrentXPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Position_Y(self, position):
        self.transform.Translate(0.0, (float(position)-self.CurrentYPosition), 0.0)
        self.CurrentYPosition = self.CurrentYPosition + (float(position)-self.CurrentYPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Position_Z(self, position):
        self.transform.Translate(0.0, 0.0, (float(position)-self.CurrentZPosition))
        self.CurrentZPosition = self.CurrentZPosition + (float(position)-self.CurrentZPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_X(self, rotation):
        self.transform.RotateX((float(rotation)-self.CurrentXRotation))
        self.CurrentXRotation = self.CurrentXRotation + (float(rotation)-self.CurrentXRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_Y(self, rotation):
        self.transform.RotateY((float(rotation)-self.CurrentYRotation))
        self.CurrentYRotation = self.CurrentYRotation + (float(rotation)-self.CurrentYRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_Z(self, rotation):
        self.transform.RotateZ((float(rotation)-self.CurrentZRotation))
        self.CurrentZRotation = self.CurrentZRotation + (float(rotation)-self.CurrentZRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Scale_X(self, scale):
        self.transform.Scale((float(scale)-self.CurrentXScale)/100, 0.0, 0.0)
        self.CurrentXScale = self.CurrentXScale + (float(scale)-self.CurrentXScale)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(self.transform)
        transformFilter.SetInputConnection(self.reader.GetOutputPort())
        transformFilter.Update()
        self.mapper.SetInputConnection(transformFilter.GetOutputPort())
        self.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Scale_Y(self, scale):
        pass
    
    def Update_Scale_Z(self, scale):
        pass
 
    def OpenSettingsDialog(self):
        self.SettingsDialog = StartSettingsDialog(self)
        self.connect(self.SettingsDialog, QtCore.SIGNAL('ApplySettings()'), self.getSettingsDialogValues)
        self.SettingsDialog.imageHeight.setText(self.imageHeight)
        self.SettingsDialog.imageWidth.setText(self.imageWidth)
        self.SettingsDialog.layerThickness.setText(self.layerThickness)
        self.SettingsDialog.startingDepth.setText(self.startingDepth)
        self.SettingsDialog.endingDepth.setText(self.endingDepth)
        self.SettingsDialog.slicingIncrement.setText(self.slicingIncrement)
        try:
            self.SettingsDialog.slicingPlane.setCurrentIndex(self.slicingplaneDict[self.slicingplane])
        except: #anything other than a valid entry will default to XZ (index 0)
            self.SettingsDialog.slicingPlane.setCurrentIndex(0)
        self.SettingsDialog.exec_()
        
    def getSettingsDialogValues(self):
        self.imageHeight = self.SettingsDialog.imageHeight.text()
        self.imageWidth = self.SettingsDialog.imageWidth.text()
        self.layerThickness = self.SettingsDialog.layerThickness.text()
        self.startingDepth = self.SettingsDialog.startingDepth.text()
        self.endingDepth = self.SettingsDialog.endingDepth.text()
        self.slicingIncrement = self.SettingsDialog.slicingIncrement.text()
        self.slicingplane = self.SettingsDialog.slicingPlane.currentText()
           
def main():
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
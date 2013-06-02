import slicer
import vtk
import sys
from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
from PyQt4.QtGui import QFileDialog, QPixmap, QSplashScreen
#from PyQt4.Qt import *
from slicer_gui import Ui_MainWindow
from slicer_settings_dialog_gui import Ui_Dialog
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ConfigParser import SafeConfigParser
import os
import shutil

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
        
        
class model():
    def __init__(self, parent, filename):
        self.parent = parent
        self.filename = filename
        self.transform = vtk.vtkTransform()
        self.CurrentXPosition = 0.0
        self.CurrentYPosition = 0.0
        self.CurrentZPosition = 0.0
        self.CurrentXRotation = 0.0
        self.CurrentYRotation = 0.0
        self.CurrentZRotation = 0.0
        self.CurrentScale = 0.0
        self.load()
            
    def load(self):
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(str(self.filename))   
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
        
        #create model actor
        self.actor = vtk.vtkActor()
        self.actor.GetProperty().SetColor(1,1,1)
        self.actor.GetProperty().SetOpacity(1)
        self.actor.SetMapper(self.mapper)

        #create outline mapper
        self.outline = vtk.vtkOutlineFilter()
        self.outline.SetInputConnection(self.reader.GetOutputPort())
        self.outlineMapper = vtk.vtkPolyDataMapper()
        self.outlineMapper.SetInputConnection(self.outline.GetOutputPort())
        
        #create outline actor
        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(self.outlineMapper)
        
        #add actors to parent render window
        self.parent.ren.AddActor(self.actor)
        self.parent.ren.AddActor(self.outlineActor)
        
        
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
        self.parser = SafeConfigParser()
        filename = 'sliceconfig.ini'
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller >= 1.6
            os.chdir(sys._MEIPASS)
            filename = os.path.join(sys._MEIPASS, filename)
            APPNAME = '3DLP'
            APPDATA = os.path.join(os.environ['APPDATA'], APPNAME)
            if not os.path.isdir(os.path.join(APPDATA)):
                os.mkdir(os.path.join(APPDATA))
                shutil.copy(filename, os.path.join(APPDATA, ''))
                self.parser.read(os.path.join(APPDATA, 'sliceconfig.ini'))
                self.LoadSettingsFromConfigFile()
            else:
                if not os.path.isfile(os.path.join(APPDATA, 'sliceconfig.ini')):
                    shutil.copy(filename, os.path.join(APPDATA))
                else:
                    self.parser.read(os.path.join(APPDATA, 'sliceconfig.ini'))
                    self.LoadSettingsFromConfigFile()
        else: #otherwise it's running in pydev environment: use the dev config file
            os.chdir(os.path.dirname(sys.argv[0]))
            filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
            self.parser.read('sliceconfig.ini')
            self.LoadSettingsFromConfigFile()
        
 
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
        
        self.modelList = [] 
        
        
    def AddModel(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open 3D Model', '.', '*.stl')
        if filename == '': #user hit cancel
            return
        modelObject = model(self, filename)
        self.modelList.append(modelObject)
        self.ui.modelList.addItem(os.path.basename(str(filename)))
        if len(self.modelList) == 1:
            self.FirstOpen()
            
        self.ren.ResetCamera()  
        self.ModelView.Render() #update model view
            
    def FirstOpen(self):
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
   
        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ui.Transform_groupbox.setEnabled(True)
    
    def SliceModel(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            QtGui.QMessageBox.critical(self, 'Error slicing model',"You must first load a model to slice it!", QtGui.QMessageBox.Ok)   
            return
        self.outputFile = str(QFileDialog.getSaveFileName(self, "Save file", "", ".3dlp"))
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
            
    def ModelIndexChanged(self, new, previous):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        self.ui.positionX.setValue(modelObject.CurrentXPosition)
        self.ui.positionY.setValue(modelObject.CurrentYPosition)
        self.ui.positionZ.setValue(modelObject.CurrentZPosition)
        self.ui.rotationX.setValue(modelObject.CurrentXRotation)
        self.ui.rotationY.setValue(modelObject.CurrentYRotation)
        self.ui.rotationZ.setValue(modelObject.CurrentZRotation)
        self.ui.scale.setValue(modelObject.CurrentScale)
            
    def Update_Position_X(self, position):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.Translate((float(position)-modelObject.CurrentXPosition), 0.0, 0.0)
        modelObject.CurrentXPosition = modelObject.CurrentXPosition + (float(position)-modelObject.CurrentXPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Position_Y(self, position):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.Translate(0.0, (float(position)-modelObject.CurrentYPosition), 0.0)
        modelObject.CurrentYPosition = modelObject.CurrentYPosition + (float(position)-modelObject.CurrentYPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Position_Z(self, position):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.Translate(0.0, 0.0, (float(position)-modelObject.CurrentZPosition))
        modelObject.CurrentZPosition = modelObject.CurrentZPosition + (float(position)-modelObject.CurrentZPosition)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_X(self, rotation):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.RotateX((float(rotation)-modelObject.CurrentXRotation))
        modelObject.CurrentXRotation = modelObject.CurrentXRotation + (float(rotation)-modelObject.CurrentXRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_Y(self, rotation):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.RotateY((float(rotation)-modelObject.CurrentYRotation))
        modelObject.CurrentYRotation = modelObject.CurrentYRotation + (float(rotation)-modelObject.CurrentYRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Rotation_Z(self, rotation):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        transform.RotateZ((float(rotation)-modelObject.CurrentZRotation))
        modelObject.CurrentZRotation = modelObject.CurrentZRotation + (float(rotation)-modelObject.CurrentZRotation)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    
    def Update_Scale(self, scale):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        #transform.Scale((float(scale)-modelObject.CurrentScale)/100.0, (float(scale)-modelObject.CurrentScale)/100.0, (float(scale)-modelObject.CurrentScale)/100.0)
        transform.Scale(2.0, 2.0, 2.0)
        modelObject.CurrentScale = modelObject.CurrentScale + (float(scale)-modelObject.CurrentScale)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(modelObject.transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        self.ren.Render()
        self.ModelView.Render()
    

    def LoadSettingsFromConfigFile(self):
        self.imageHeight = int(self.parser.get('slicing_settings', 'Image_Height'))
        self.imageWidth = int(self.parser.get('slicing_settings', 'Image_Width'))
        self.startingDepth = int(self.parser.get('slicing_settings', 'Starting_Depth'))
        self.endingDepth = int(self.parser.get('slicing_settings', 'Ending_Depth'))
        self.slicingIncrement = int(self.parser.get('slicing_settings', 'Slicing_Increment'))
        self.slicingplane = self.parser.get('slicing_settings', 'Slicing_Plane')

    def OpenSettingsDialog(self):
        self.SettingsDialog = StartSettingsDialog(self)
        self.connect(self.SettingsDialog, QtCore.SIGNAL('ApplySettings()'), self.getSettingsDialogValues)
        self.SettingsDialog.imageHeight.setText(str(self.imageHeight))
        self.SettingsDialog.imageWidth.setText(str(self.imageWidth))
        self.SettingsDialog.startingDepth.setText(str(self.startingDepth))
        self.SettingsDialog.endingDepth.setText(str(self.endingDepth))
        self.SettingsDialog.slicingIncrement.setText(str(self.slicingIncrement))
        self.slicingplaneDict = {"XZ":0, "XY":1, "YZ":2}
        try:
            self.SettingsDialog.slicingPlane.setCurrentIndex(self.slicingplaneDict[self.slicingplane])
        except: #anything other than a valid entry will default to XZ (index 0)
            self.SettingsDialog.slicingPlane.setCurrentIndex(0)
        self.SettingsDialog.exec_()
        
    def getSettingsDialogValues(self):
        self.imageHeight = int(self.SettingsDialog.imageHeight.text())
        self.parser.set('slicing_settings', 'Image_Height', "%s"%self.imageHeight)
        self.imageWidth = int(self.SettingsDialog.imageWidth.text())
        self.parser.set('slicing_settings', 'Image_Width', "%s"%self.imageWidth)
        self.startingDepth = int(self.SettingsDialog.startingDepth.text())
        self.parser.set('slicing_settings', 'Starting_Depth', "%s"%self.startingDepth)
        self.endingDepth = int(self.SettingsDialog.endingDepth.text())
        self.parser.set('slicing_settings', 'Ending_Depth', "%s"%self.endingDepth)
        self.slicingIncrement = int(self.SettingsDialog.slicingIncrement.text())
        self.parser.set('slicing_settings', 'Slicing_Increment', "%s"%self.slicingIncrement)
        self.slicingplane = self.SettingsDialog.slicingPlane.currentText()
        self.parser.set('slicing_settings', 'Slicing_Plane', "%s"%self.slicingplane)
        
        filename = 'sliceconfig.ini'
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller >= 1.6
            APPNAME = '3DLP'
            APPDATA = os.path.join(os.environ['APPDATA'], APPNAME)
            filename = os.path.join(APPDATA, filename)
            outputini = open(filename, 'w') #open a file pointer for the config file parser to write changes to
            self.parser.write(outputini)
            outputini.close() #done writing config file changes
        else: #otherwise it's running in pydev environment: use the dev config file
            os.chdir(os.path.dirname(sys.argv[0]))
            filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
            outputini = open(filename, 'w') #open a file pointer for the config file parser to write changes to
            self.parser.write(outputini)
            outputini.close() #done writing config file changes
        ##
        
def main():
    app = QtGui.QApplication(sys.argv)
    
    splash_pix = QPixmap(':/splash/3dlp_slicer_splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    
    window=Main()
    window.show()
    splash.finish(window)

    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
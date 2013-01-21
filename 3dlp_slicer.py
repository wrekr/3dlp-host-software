
import slicer
import vtk
import sys
from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
from slicer_gui import Ui_MainWindow
from slicer_settings_dialog_gui import Ui_Dialog
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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
        ui.getvalues()

    def quit(self):
        print "quitting"

    # Create a class for our main window
class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        pass
        #self.ModelView.resize(self.ui.ModelFrame.geometry().width()-15,self.ui.ModelFrame.geometry().height()-39)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Host", None, QtGui.QApplication.UnicodeUTF8))

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
        self.filename = QtGui.QFileDialog.getOpenFileName()
#        self.ui.displayfilenamelabel.setText(self.filename)

        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(str(self.filename))
         
        self.polyDataOutput = self.reader.GetOutput()       
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
         
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
        self.ren.AddActor(self.outlineActor)
       
        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ren.ResetCamera()  
        self.ModelView.Render() #update model view
    
    def SliceModel(self):
        self.slicer = slicer.slicer()
        self.slicer.imageheight = 800
        self.slicer.imagewidth = 600
        # check to see if starting depth is less than ending depth!! this assumption is crucial
        self.slicer.startingdepth = 0.0
        self.slicer.endingdepth = 50.0
        self.slicer.layerincrement = 0.5       
        self.slicer.OpenModel("wfu_cbi_skull_cleaned.stl")
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
            QtGui.QMessageBox.critical(self, 'Error setting opacity',"You must load a model to change the opacity!", QtGui.QMessageBox.Ok)        
            
    def getvalues(self):
        print "got here"
            
    def OpenSettingsDialog(self):
        self.SettingsDialog = StartSettingsDialog(self)
        self.SettingsDialog.exec_()
        
    def getSettingsDialogValues(self):
        pass
         
    def openhelp(self):
        webbrowser.open("http://www.chrismarion.net/3dlp/software/help")
 
    def openaboutdialog(self):
        dialog = OpenAbout(self)
        dialog.exec_()
           
def main():
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
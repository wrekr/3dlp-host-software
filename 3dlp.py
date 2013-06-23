# -*- coding: utf-8 -*-
"""
Created on Thu Apr 05 22:20:39 2012

@author: Chris Marion Copyright 2012-2013
www.chrismarion.net

Still to add/known issues:
    -projector control functionality is not finished.
    -still looking for a good method of calibrating for X and Y (image size)
    -raise the bed to a final position after build is complete
    -Trapezoidal motion profiling of Z movement
    -custom firmware configurator and uploader
    -scripting commands for motor speed, GPIO (solenoids, etc), PWM control of gearmotors with encoder feedback, and pause
    -custom scripting for different sections of layers
    -ability to save custom hardware profiles for different printers
"""
import sys

import comscan
import webbrowser
from ConfigParser import *
import printmodel
import vtk
from settingsdialog import Ui_SettingsDialogBaseClass
from manual_control_gui import Ui_Manual_Control
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import hardware
import cPickle as pickle
from time import sleep
import zipfile
import StringIO
import tempfile
import shutil

#**********************************

import os
from qtgui import Ui_MainWindow #import generated class from ui file from designer 

from aboutdialoggui import Ui_Dialog
from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

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

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))
        
class StartSettingsDialog(QtGui.QDialog, Ui_SettingsDialogBaseClass):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        
    def ApplySettings(self):
        print "Applying Settings"
        self.emit(QtCore.SIGNAL('ApplySettings()'))
        self.reject()

class StartManualControl(QtGui.QDialog, Ui_Manual_Control):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.printer = parent.printer
        self.setupUi(self)
        self.mm_per_step = float(parent.pitch)/float(parent.stepsPerRev)
        self.microstepping = 0.0625 #1/16th microstepping
        print self.microstepping
        self.mm_per_step = self.mm_per_step#/self.microstepping
        self.Zpos = 0.0
        self.Xpos = 0.0
        self.printer.EnableZ()

    def Z_up(self):
        if self.Z_01.isChecked(): #Z 0.1mm is checked
            self.Zpos = self.Zpos+.1
            self.DRO_Z.display(float(self.DRO_Z.value())+.1)
            self.printer.IncrementZ(200)
            #print "incrementing %r steps"%(.1/self.mm_per_step)
        elif self.Z_1.isChecked(): #Z 1mm is checked
            self.Zpos = self.Zpos+1
            self.DRO_Z.display(float(self.DRO_Z.value())+1)
            self.printer.IncrementZ(1/self.mm_per_step)
            #print "incrementing %r steps"%(1/self.mm_per_step)
        elif self.Z_10.isChecked(): #Z 10mm is checked
            self.Zpos = self.Zpos+10
            self.DRO_Z.display(float(self.DRO_Z.value())+10)
            self.printer.IncrementZ((10/self.mm_per_step))
            #print "incrementing %r steps"%(10/self.mm_per_step)

    def Z_down(self):
        if self.Z_01.isChecked(): #Z 0.1mm is checked
            self.Zpos = self.Zpos-.1
            self.DRO_Z.display(float(self.DRO_Z.value())-.1)
            self.printer.IncrementZ(-.1/self.mm_per_step)
            #print "incrementing %r steps"%(-.1/self.mm_per_step)
        elif self.Z_1.isChecked(): #Z 1mm is checked
            self.Zpos = self.Zpos-1
            self.DRO_Z.display(float(self.DRO_Z.value())-1)
            self.printer.IncrementZ(-1/self.mm_per_step)
            #print "incrementing %r steps"%(-1/self.mm_per_step)
        elif self.Z_10.isChecked(): #Z 10mm is checked
            self.Zpos = self.Zpos-10
            self.DRO_Z.display(float(self.DRO_Z.value())-10)
            self.printer.IncrementZ(-10/self.mm_per_step)
            #print "incrementing %r steps"%(10/self.mm_per_step)
   
    def Zero_Z(self):
        self.Zpos = 0
        self.DRO_Z.display(0)
        
    def activateX(self):
        pass
    
class _3dlpfile():
    def __init__(self):
        print "init"
        self.name = ""
        self.description = ""
        self.notes = ""
        
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
        self.PreviousScale = 0.0
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
        self.parent.renPre.AddActor(self.actor)
        self.parent.renPre.AddActor(self.outlineActor)
        
#######################GUI class and event handling#############################
class OpenAbout(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        try:
            self.ModelView.resize(self.ui.frame.geometry().width()-16,self.ui.frame.geometry().height()-30)
            self.ui.toolbar.resize(QSize(43,658))
            self.slicepreview.resize(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height())
            self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
            self.slicepreview.setPixmap(self.pmscaled)  
        except: #no frames to resize
            pass    
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure you want to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Host", None, QtGui.QApplication.UnicodeUTF8))
        
        self.pm = QtGui.QPixmap(':/blank/10x10black.png')
        
        #add toolbar labels
        label = QtGui.QLabel(" Current Layer: ")
        self.ui.toolBar_3.addWidget(label)
        self.layercount = QtGui.QLabel("0 of 0")
        self.ui.toolBar_3.addWidget(self.layercount)
        self.cwd = os.getcwd() #get current execution (working) directory
        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        self.screencount = QtGui.QDesktopWidget().numScreens()
        print "number of monitors: ", self.screencount

        self.ports = comscan.comscan() #returns a list with each entry being a dict of useful information
        print self.ports
        self.numports = len(self.ports) #how many dicts did comscan return?
        
        #print "Found %d ports, %d available." %(self.numports, numports)

        self.parser = SafeConfigParser()
        ##to make sure it can find the config.ini file originally bundled with the .exe by Pyinstaller
        filename = 'config.ini'
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller >= 1.6
            os.chdir(sys._MEIPASS)
            filename = os.path.join(sys._MEIPASS, filename)
            APPNAME = '3DLP'
            APPDATA = os.path.join(os.environ['APPDATA'], APPNAME)
            if not os.path.isdir(os.path.join(APPDATA)):
                os.mkdir(os.path.join(APPDATA))
                shutil.copy(filename, os.path.join(APPDATA, ''))
                self.parser.read(os.path.join(APPDATA, 'config.ini'))
                self.LoadSettingsFromConfigFile()
            else:
                if not os.path.isfile(os.path.join(APPDATA, 'config.ini')):
                    shutil.copy(filename, os.path.join(APPDATA))
                else:
                    self.parser.read(os.path.join(APPDATA, 'config.ini'))
                    self.LoadSettingsFromConfigFile()
        else: #otherwise it's running in pydev environment: use the dev config file
            os.chdir(os.path.dirname(sys.argv[0]))
            filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
            self.parser.read('config.ini')
            self.LoadSettingsFromConfigFile()
            
        self.modelList = [] 
            
        ####pre-slice setup
        
        self.renPre = vtk.vtkRenderer()
        self.renPre.SetBackground(.4,.4,.4)
        
        self.ModelViewPre = QVTKRenderWindowInteractor(self.ui.modelFramePre)
        self.ModelViewPre.SetInteractorStyle(MyInteractorStyle())
        self.ModelViewPre.Initialize()
        self.ModelViewPre.Start()
        
        self.renWinPre=self.ModelViewPre.GetRenderWindow()
        self.renWinPre.AddRenderer(self.renPre)
        
        ###post-slice setup
        
        self.renPost = vtk.vtkRenderer()
        self.renPost.SetBackground(.4,.4,.4)
        
        self.ModelViewPost = QVTKRenderWindowInteractor(self.ui.modelFramePost)
        self.ModelViewPost.SetInteractorStyle(MyInteractorStyle())
        self.ModelViewPost.Initialize()
        self.ModelViewPost.Start()
        
        self.renWin=self.ModelViewPost.GetRenderWindow()
        self.renWin.AddRenderer(self.renPost)
        

        ########
        self.ChangeWorkspacePostSlice()
        
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__     
        self.printer.close()      #close serial connection to printer if open
        
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.ui.consoletext.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.consoletext.setTextCursor(cursor)
        self.ui.consoletext.ensureCursorVisible()
        
    def ChangeWorkspacePreSlice(self):
        self.ui.preSliceBar.show()
        self.ui.sliceListBar.hide()
        self.ui.printJobInfoBar.hide()
        self.ui.workspacePost.hide()
        self.ui.workspacePre.show()
        
        self.ModelViewPre.show()
        self.ModelViewPre.resize(self.ui.modelFramePre.geometry().width(), self.ui.modelFramePre.geometry().height())
        
        self.ui.printJobInfoBar.hide()
        self.ui.sliceListBar.hide()
        self.ui.actionPreSlice.setChecked(True)
        self.ui.actionPostSlice.setChecked(False)
            
    def ChangeWorkspacePostSlice(self):
        self.ui.preSliceBar.hide()
        self.ui.sliceListBar.show()
        self.ui.printJobInfoBar.show()
        self.ui.workspacePost.show()
        self.ui.workspacePre.hide()

        self.ModelViewPost.show()
        self.ModelViewPost.resize(self.ui.modelFramePost.geometry().width(), self.ui.modelFramePost.geometry().height())
            
        self.slicepreview = QtGui.QLabel(self.ui.sliceFramePost)
        filename = '10x10black.png'
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller >= 1.6
            os.chdir(sys._MEIPASS)
            filename = os.path.join(sys._MEIPASS, filename)
        else: #otherwise it's running in pydev environment: use the 10x10black.png file in the dev folder
            os.chdir(os.path.dirname(sys.argv[0]))
            filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
        pm = QtGui.QPixmap(filename)
        pmscaled = pm.scaled(400, 600)
        self.slicepreview.setPixmap(pmscaled) #set black pixmap for blank slide     
        
            #this is needed here to resize after the window is created to fill frames
        self.slicepreview.resize(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height())
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
          
        self.ui.actionPreSlice.setChecked(False)
        self.ui.actionPostSlice.setChecked(True)

    def OpenPrintJob(self):
        self._3dlpfile = zipfile.ZipFile(str(QtGui.QFileDialog.getOpenFileName(self, 'Open 3DLP Print Job', '.', '*.3dlp')))
        
        self.FileList = []
        for file in self._3dlpfile.namelist(): 
            if file.startswith("/slices/") and file.endswith(".png"): #if it's a supported image type in the slices directory
                temp = tempfile.SpooledTemporaryFile()
                temp.write(self._3dlpfile.read(file))
                temp.seek(0)
                self.FileList.append(temp)
        print self.FileList
        if len(self.FileList)<1:
            print "no valid slice images were found"
            return
        if not "printconfiguration.ini" in self._3dlpfile.namelist():
            print "no print configuration file was found"
            return
        try:
            self.printconfigparser = SafeConfigParser()
            ini = self._3dlpfile.open("printconfiguration.ini")
            string = StringIO.StringIO(ini.read())
            self.printconfigparser.readfp(string)
        except:
            print "unknown error encountered while trying to parse print configuration file"
            return
        
        #extract model for opening - can't open it from memory unfortunately :(
        temp = tempfile.NamedTemporaryFile()
        self._3dlpfile.extract((self.printconfigparser.get('preview_settings', 'STL_name')), os.getcwd())
        self.OpenModel(self.printconfigparser.get('preview_settings', 'STL_name'))
        
        if not "slices.p" in self._3dlpfile.namelist():
            print "Error loading slices.p"
            QtGui.QMessageBox.information(self, 'Error loading preview correlations',"Error finding or loading slices.p. You will not be able to preview slices in real-time within the 3D model.", QtGui.QMessageBox.Ok)
            self.preview = False
        else:
            p = self._3dlpfile.read("slices.p")
            string = StringIO.StringIO(p)
            self.sliceCorrelations = pickle.load(string)
            print self.sliceCorrelations
            self.preview = True
        self.currentlayer = 1
        self.numberOfLayers = len(self.FileList)
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm = QtGui.QPixmap() #remember to compensate for 0-index
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read())
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
        self.UpdateModelLayer(self.sliceCorrelations[self.currentlayer-1][1])
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        self.slicepreview.resize(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height())

    def AddModel(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open 3D Model', '.', '*.stl')
        if filename == '': #user hit cancel
            return
        modelObject = model(self, filename)
        self.modelList.append(modelObject)
        self.ui.modelList.addItem(os.path.basename(str(filename)))
        if len(self.modelList) == 1:
            self.FirstOpen()
            
        self.renPre.ResetCamera()  
        self.ModelViewPre.Render() #update model view
        
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
        self.axes.SetInteractor(self.ModelViewPre)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ui.Transform_groupbox.setEnabled(True)

    def OpenModel(self, filename):
        self.ModelView.resize(self.ui.frame.geometry().width()-16,self.ui.frame.geometry().height()-30) #just in case resizeEvent() hasn't been called yet

        self.filename = filename
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(filename)
        self.polyDataOutput = self.reader.GetOutput()       
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
         
        #create model actor
        self.modelActor = vtk.vtkActor()
        self.modelActor.GetProperty().SetColor(0,.8,0)
        self.modelActor.GetProperty().SetOpacity(1)
        self.modelActor.SetMapper(self.mapper)
        
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        self.slicingplane=vtk.vtkPlane()
        self.slicingplane.SetOrigin(0,0,20)
        self.slicingplane.SetNormal(0,0,1)
        
        #create cutter
        self.cutter=vtk.vtkCutter()
        self.cutter.SetCutFunction(self.slicingplane)
        self.cutter.SetInputConnection(self.reader.GetOutputPort())
        self.cutter.Update()
        
        self.FeatureEdges = vtk.vtkFeatureEdges()
        self.FeatureEdges.SetInputConnection(self.cutter.GetOutputPort())
        self.FeatureEdges.BoundaryEdgesOn()
        self.FeatureEdges.FeatureEdgesOff()
        self.FeatureEdges.NonManifoldEdgesOff()
        self.FeatureEdges.ManifoldEdgesOff()
        self.FeatureEdges.Update()

        self.cutStrips = vtk.vtkStripper() #Forms loops (closed polylines) from cutter
        self.cutStrips.SetInputConnection(self.cutter.GetOutputPort())
        self.cutStrips.Update()
        self.cutPoly = vtk.vtkPolyData() #This trick defines polygons as polyline loop
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        
        # Triangle filter
        self.cutTriangles = vtk.vtkTriangleFilter()
        self.cutTriangles.SetInput(self.cutPoly)
        self.cutTriangles.Update()
        
        #cutter mapper
        self.cutterMapper=vtk.vtkPolyDataMapper()
        self.cutterMapper.SetInput(self.cutPoly)
        self.cutterMapper.SetInputConnection(self.cutTriangles.GetOutputPort())

        self.cutterOutlineMapper=vtk.vtkPolyDataMapper()
        self.cutterOutlineMapper.SetInputConnection(self.cutter.GetOutputPort())          
             
#        #create plane actor
        self.slicingplaneActor=vtk.vtkActor()
        self.slicingplaneActor.GetProperty().SetColor(1.0,1.0,1.0)
        self.slicingplaneActor.GetProperty().SetLineWidth(4)
        self.slicingplaneActor.SetMapper(self.cutterMapper)
#        
        #create plane actor
        self.slicingplaneoutlineActor=vtk.vtkActor()
        self.slicingplaneoutlineActor.GetProperty().SetColor(1.0,0,0)
        self.slicingplaneoutlineActor.GetProperty().SetLineWidth(4)
        self.slicingplaneoutlineActor.SetMapper(self.cutterOutlineMapper)

        #create outline mapper
        self.outline = vtk.vtkOutlineFilter()
        self.outline.SetInputConnection(self.reader.GetOutputPort())
        self.outlineMapper = vtk.vtkPolyDataMapper()
        self.outlineMapper.SetInputConnection(self.outline.GetOutputPort())
        
        #create outline actor
        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(self.outlineMapper)
        
        #create annotated cube anchor actor
        self.axesActor = vtk.vtkAnnotatedCubeActor()
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
        self.ren.AddActor(self.slicingplaneActor)
        self.ren.AddActor(self.slicingplaneoutlineActor)
        self.ren.AddActor(self.outlineActor)

        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ren.ResetCamera()  
        self.ModelView.Render() #update model view
    
    def IncrementSlicingPlanePositive(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            return
        if  self.currentlayer == len(self.FileList):
            return
        #####slice preview
        self.currentlayer = self.currentlayer + 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read())
        self.FileList[self.currentlayer-1].seek(0)
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)    
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        #####model preview
        if not self.preview:
            return
        else:
            self.slicingplane.SetOrigin(0,0,self.sliceCorrelations[self.currentlayer-1][1])
            self.cutter.Update()
            self.cutStrips.Update()
            self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
            self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
            self.cutPoly.Update()
            self.cutTriangles.Update()
            self.ren.Render()
            self.ModelView.Render()
        
    def IncrementSlicingPlaneNegative(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            return   
        if  self.currentlayer == 1:
            return
        #####slice preview
        self.currentlayer = self.currentlayer - 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read())
        self.FileList[self.currentlayer-1].seek(0)
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)    
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        #####model preview
        if not self.preview:
            return
        else:
            self.slicingplane.SetOrigin(0,0,self.sliceCorrelations[self.currentlayer-1][1])
            self.cutter.Update()
            self.cutStrips.Update()
            self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
            self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
            self.cutPoly.Update()
            self.cutTriangles.Update()
            self.ren.Render()
            self.ModelView.Render()
        
    def GoToLayer(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            QtGui.QMessageBox.critical(self, 'Error changing current layer',"You must load a model to navigate between layers!", QtGui.QMessageBox.Ok)
            return   
        layer, ok = QtGui.QInputDialog.getText(self, 'Go To Layer', 'Enter the desired layer (1 - %s)' %(int(len(self.FileList))))
        if not ok: #the user hit the "cancel" button
            return
        if int(layer)<0:
            QtGui.QMessageBox.critical(self, 'Error going to layer',"You must enter a layer between 1 and %s" %(int(len(self.FileList))), QtGui.QMessageBox.Ok)
            return
        #####slice preview
        self.currentlayer = int(layer)
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read())
        self.FileList[self.currentlayer-1].seek(0)
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        #####model preview
        if not self.preview:
            return
        else:
            self.slicingplane.SetOrigin(0,0,self.sliceCorrelations[self.currentlayer-1][1])
            self.cutter.Update()
            self.cutStrips.Update()
            self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
            self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
            self.cutPoly.Update()
            self.cutTriangles.Update()
            self.ren.Render()
            self.ModelView.Render()
        
    def GoToFirstLayer(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            return   
        self.currentlayer = 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read()) #remember to compensate for 0-index
        self.FileList[self.currentlayer-1].seek(0)
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        #####model preview
        if not self.preview:
            return
        else:
            self.slicingplane.SetOrigin(0,0,self.sliceCorrelations[self.currentlayer-1][1])
            self.cutter.Update()
            self.cutStrips.Update()
            self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
            self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
            self.cutPoly.Update()
            self.cutTriangles.Update()
            self.ren.Render()
            self.ModelView.Render()
        
    def GoToLastLayer(self):
        try:
            if self.modelActor: #check to see if a model is loaded, if not it will throw an exception
                pass
        except: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            return
        self.currentlayer = int(self.numberOfLayers)
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm.loadFromData(self.FileList[self.currentlayer-1].read()) #remember to compensate for 0-index
        self.FileList[self.currentlayer-1].seek(0)
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
        QApplication.processEvents() #make sure the toolbar gets updated with new text 
        #####model preview
        if not self.preview:
            return
        else:
            self.slicingplane.SetOrigin(0,0,self.sliceCorrelations[self.currentlayer-1][1])
            self.cutter.Update()
            self.cutStrips.Update()
            self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
            self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
            self.cutPoly.Update()
            self.cutTriangles.Update()
            self.ren.Render()
            self.ModelView.Render()
        
    def UpdateModelLayer(self, z):
        self.slicingplane.SetOrigin(0,0,z)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.ren.Render()
        self.ModelView.Render()
                
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
            
    def ModelIndexChanged(self, new, previous):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        self.ui.positionX.setValue(modelObject.CurrentXPosition)
        self.ui.positionY.setValue(modelObject.CurrentYPosition)
        self.ui.positionZ.setValue(modelObject.CurrentZPosition)
        self.ui.rotationX.setValue(modelObject.CurrentXRotation)
        self.ui.rotationY.setValue(modelObject.CurrentYRotation)
        self.ui.rotationZ.setValue(modelObject.CurrentZRotation)
        self.ui.scale.setValue(modelObject.CurrentScale)
            
    def UpdatePositionX(self, position):
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
    
    def UpdatePositionY(self, position):
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
    
    def UpdatePositionZ(self, position):
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
    
    def UpdateRotationX(self, rotation):
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
    
    def UpdateRotationY(self, rotation):
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
    
    def UpdateRotationZ(self, rotation):
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
    
    def UpdateScale(self, scale):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        transform = modelObject.transform
        
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

        
        delta = modelObject.PreviousScale - modelObject.CurrentScale
        modelObject.transform
        #transform.Scale((float(scale)-modelObject.CurrentScale)/100.0, (float(scale)-modelObject.CurrentScale)/100.0, (float(scale)-modelObject.CurrentScale)/100.0)
        transform.Scale
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
        self.printerBaud = int(self.parser.get('program_defaults', 'printerBAUD'))
        self.zScript = self.parser.get('scripting', 'sequence')
        self.projectorPowerOffCommand = self.parser.get('projector_settings', 'PowerOffCommand')
        self.projectorBaud = self.parser.get('projector_settings', 'projectorBAUD')
        self.exposeTime = self.parser.get('program_defaults', 'ExposeTime')
        self.numberOfStartLayers = self.parser.get('program_defaults', 'NumStartLayers')
        self.startLayersExposureTime = self.parser.get('program_defaults', 'StartLayersExposeTime')
        
        if self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO_UNO':
            self.controller = "arduinoUNO"
        elif self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO_MEGA':
            self.controller = "arduinoMEGA"
        elif self.parser.get('program_defaults', 'printercontroller') == 'PYMCU':
            self.controller = "pymcu"
        elif self.parser.get('program_defaults', 'printercontroller') == 'RAMPS':
            self.controller = "ramps"
        if self.parser.get('program_defaults', 'slideshowenabled') == 'True':
            self.slideshowEnabled = True
        else:
            self.slideshowEnabled = False
        if self.parser.get('program_defaults', 'printercontrol') == 'True':
            self.enablePrinterControl = True
        else:
            self.enablePrinterControl = False
        if self.parser.get('projector_settings', 'projectorcontrol') == 'True':
            self.projectorControlEnabled = True
        else:
            self.projectorControlEnabled = False
            
        self.COM_Port = self.parser.get('program_defaults', 'printerCOM')
        self.screenNumber = self.parser.get('program_defaults', 'screennumber')
        
        self.pitch = int(self.parser.get('printer_hardware', 'Leadscrew_pitch'))
        self.stepsPerRev = int(self.parser.get('printer_hardware', 'Steps_per_rev'))
            
    def OpenSettingsDialog(self):
        self.SettingsDialog = StartSettingsDialog(self)
        
        for x in range(self.numports):
            portentry = self.ports[x] #switch to dict x
            if portentry['available'] == True: #if it is currently available
                portname = portentry['name'] #find the name of the port
                #print portname 
                self.SettingsDialog.pickcom.addItem(portname)
                self.SettingsDialog.pickcom.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))

        ####setup screen picker####
        for x in range(self.screencount):
            self.SettingsDialog.pickscreen.addItem("")
            self.SettingsDialog.pickscreen.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%d"%x, None, QtGui.QApplication.UnicodeUTF8))
            
        bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        #self. = bauddict[self.parser.get('program_defaults', 'projectorBAUD')]
 
        #insert all other values from current namespace
        self.SettingsDialog.zscript.setPlainText(self.zScript)
        self.SettingsDialog.projector_poweroffcommand.setText(self.projectorPowerOffCommand)

        self.SettingsDialog.exposure_time.setText(str(self.exposeTime))
        self.SettingsDialog.starting_layers.setText(str(self.numberOfStartLayers))
        self.SettingsDialog.starting_layer_exposure.setText(str(self.startLayersExposureTime))
        
        self.SettingsDialog.pitch.setText(str(self.pitch))
        self.SettingsDialog.stepsPerRev.setText(str(self.stepsPerRev))
        
        if self.controller == 'arduinoUNO':
            self.SettingsDialog.radio_arduinoUno.click()
        elif self.controller == 'arduinoMEGA':
            self.SettingsDialog.radio_arduinoMega.click()
        elif self.controller == 'pymcu':
            self.SettingsDialog.radio_pyMCU.click()
        elif self.controller == 'ramps':
            self.SettingsDialog.radio_ramps.click()
        if self.parser.get('program_defaults', 'slideshowenabled') == 'True':
            self.SettingsDialog.enableslideshow.click()
        if self.parser.get('program_defaults', 'printercontrol') == 'True':
            self.SettingsDialog.enableprintercontrol.click()
        if self.parser.get('projector_settings', 'projectorcontrol') == 'True':
            self.SettingsDialog.projectorcontrol.click()
        
        #self.getSettingsDialogValues()
        self.connect(self.SettingsDialog, QtCore.SIGNAL('ApplySettings()'), self.getSettingsDialogValues)
        self.SettingsDialog.exec_()
        
    def getSettingsDialogValues(self):
        print "got here"
        self.zScript = self.SettingsDialog.zscript.document().toPlainText()
        self.parser.set('scripting', 'sequence', '%s'%self.zScript)
        self.COM_Port = self.SettingsDialog.pickcom.currentText()
        self.parser.set('program_defaults', 'printerCOM', '%s'%self.COM_Port)

        self.exposeTime = float(self.SettingsDialog.exposure_time.text())
        self.parser.set('program_defaults', 'ExposeTime', '%s'%self.exposeTime)
        #AdvanceTime = float(self.ui.advance_time.text())
        self.numberOfStartLayers = float(self.SettingsDialog.starting_layers.text())
        self.parser.set('program_defaults', 'NumStartLayers', '%s'%self.numberOfStartLayers)
        self.startLayersExposureTime = float(self.SettingsDialog.starting_layer_exposure.text())
        self.parser.set('program_defaults', 'StartLayersExposeTime', '%s'%self.startLayersExposureTime)
        self.projector_baud = self.SettingsDialog.projector_baud.currentText()
        self.parser.set('program_defaults', 'projectorBAUD', '%s'%self.projector_baud)
        self.pitch = int(self.SettingsDialog.pitch.text())
        self.parser.set('printer_hardware', 'Leadscrew_pitch', '%s'%self.pitch)
        self.stepsPerRev = int(self.SettingsDialog.stepsPerRev.text())
        self.parser.set('printer_hardware', 'Steps_per_rev', '%s'%self.stepsPerRev)

        if self.SettingsDialog.projectorcontrol.isChecked():
            self.projectorControlEnabled = True
            self.parser.set('program_defaults', 'projectorcontrol', 'True')
        else:
            self.projectorControlEnabled = False
            self.parser.set('program_defaults', 'projectorcontrol', 'False')
            
        if self.SettingsDialog.enableprintercontrol.isChecked():
            self.printercontrolenabled = True  
            self.parser.set('program_defaults', 'printercontrol', 'True')
        else:
            self.printercontrolenabled = False
            self.parser.set('program_defaults', 'printercontrol', 'False')

        if self.SettingsDialog.enableslideshow.isChecked():
            self.slideshowEnabled = True
            self.parser.set('program_defaults', 'slideshowenabled', 'True')
        else:
            self.slideshowEnabled = False
            self.parser.set('program_defaults', 'slideshowenabled', 'False')
        if self.SettingsDialog.radio_pyMCU.isChecked():
            self.controller = "pymcu"
            self.parser.set('program_defaults', 'printercontroller', 'PYMCU')
        self.screenNumber = self.SettingsDialog.pickscreen.currentText() #get the screen number from picker
        if self.SettingsDialog.radio_arduinoUno.isChecked():
            self.controller = "arduinoUNO"
            self.parser.set('program_defaults', 'printercontroller', 'ARDUINO_UNO')
        if self.SettingsDialog.radio_arduinoMega.isChecked():
            self.controller = "arduinoMEGA"
            self.parser.set('program_defaults', 'printercontroller', 'ARDUINO_MEGA')
        if self.SettingsDialog.radio_ramps.isChecked():
            self.controller = "ramps"
            self.parser.set('program_defaults', 'printercontroller', 'RAMPS')
        #SAVE config settings
        ##to make sure it can find the config.ini file bundled with the .exe by Pyinstaller
#        filename = 'config.ini'
#        if hasattr(sys, '_MEIPASS'):
#            # PyInstaller >= 1.6
#            os.chdir(sys._MEIPASS)
#            filename = os.path.join(sys._MEIPASS, filename)
#        else:
#            os.chdir(os.path.dirname(sys.argv[0]))
#            filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
        ##
        
        filename = 'config.ini'
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
         
    def openhelp(self):
        webbrowser.open("http://www.chrismarion.net/3dlp/software/help")
        
    def openmanualcontrol(self):
        try: #check to see if printer object exists
            if self.printer:
                pass
        except:
            QtGui.QMessageBox.critical(self, 'Error opening manual control dialog',"You must first connect to a printer to control it!", QtGui.QMessageBox.Ok)
            return  
        ManualControl = StartManualControl(self)
        ManualControl.exec_()
        
    def ConnectToPrinter(self):
        self.printer = hardware.ramps("COM11")
        if self.printer.status == 1:
            print "unknown error encountered while trying to connect to printer."
            return
    
    def disablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(False)

    def enablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(True)        
        
    def openaboutdialog(self):
        dialog = OpenAbout(self)
        dialog.exec_()
        
    def printpressed(self):   
        try: #check to see if printer object exists
            if self.printer:
                pass
        except:
            QtGui.QMessageBox.critical(self, 'Error starting print job',"You must first connect to a printer to print to it!", QtGui.QMessageBox.Ok)
            return   
        self.printThread = printmodel.printmodel(self.zScript, self.COM_Port, self.printerBaud, self.exposeTime
                                                , self.numberOfStartLayers, self.startLayersExposureTime
                                                , self.projectorControlEnabled, self.controller, self.screenNumber, self.cwd, self)
        #connect to slideshow signal
        self.connect(self.printThread, QtCore.SIGNAL('updatePreview'), self.updatepreview)      
        self.connect(self.printThread, QtCore.SIGNAL('updatePreviewBlank'), self.updatepreviewblank)      
        self.connect(self.printThread, QtCore.SIGNAL('disable_stop_button'), self.disablestopbutton) 
        self.connect(self.printThread, QtCore.SIGNAL('enable_stop_button'), self.enablestopbutton)     
        self.printThread.start()

    def StopPrinting(self):
        print "Stopping print cycle.. finishing current layer"
        self.printThread.stop = True
################################################################################
def GetInHMS(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    #print "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d:%02d" % (h, m, s)

################################################################################        
def main():
    ################pyQt stuff
    app = QtGui.QApplication(sys.argv)
    
    splash_pix = QPixmap(':/splash/3dlp_splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    
    window=Main()
    window.show()
    splash.finish(window)


    
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    ###############
    
    
if __name__ == "__main__":
    main()
    
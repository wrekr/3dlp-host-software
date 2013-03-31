# -*- coding: utf-8 -*-
"""
Created on Thu Apr 05 22:20:39 2012

@author: Chris Marion Copyright 2012
www.chrismarion.net

Still to add/known issues:
    -fix ETA and advance time
    -projector control functionality is not finished.
    -I would like to support many different hardware types - poll community on hardware (drivers, feedback control, etc.)
    -Manual printer control dialog for manually jogging each printer axis
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
        print "Connecting to RAMPS board..."
        self.printer = hardware.ramps(parent.COM_Port)
        if self.printer.status == 1:
            return
        self.setupUi(self)
        self.mm_per_step = float(parent.pitch)/float(parent.steps_per_rev)
        self.Zpos = 0.0
        self.Xpos = 0.0

    def Z_up(self):
        if self.Z_001.isChecked(): #Z 0.01mm is checked
            self.Zpos = self.Zpos+.01
            self.DRO_Z.display(float(self.DRO_Z.value())+.01)
            self.printer.IncrementZ(.01/self.mm_per_step)
            #print "incrementing %r steps"%(.01/self.mm_per_step)
        elif self.Z_01.isChecked(): #Z 0.1mm is checked
            self.Zpos = self.Zpos+.1
            self.DRO_Z.display(float(self.DRO_Z.value())+.1)
            self.printer.IncrementZ(.1/self.mm_per_step)
            #print "incrementing %r steps"%(.1/self.mm_per_step)
        elif self.Z_1.isChecked(): #Z 1mm is checked
            self.Zpos = self.Zpos+1
            self.DRO_Z.display(float(self.DRO_Z.value())+1)
            self.printer.IncrementZ(1/self.mm_per_step)
            #print "incrementing %r steps"%(1/self.mm_per_step)
        elif self.Z_10.isChecked(): #Z 10mm is checked
            self.Zpos = self.Zpos+10
            self.DRO_Z.display(float(self.DRO_Z.value())+10)
            self.printer.IncrementZ(10/self.mm_per_step)
            #print "incrementing %r steps"%(10/self.mm_per_step)

    def Z_down(self):
        if self.Z_001.isChecked(): #Z 0.01mm is checked
            self.Zpos = self.Zpos-.01
            self.DRO_Z.display(float(self.DRO_Z.value())-.01)
            self.printer.IncrementZ(-.01/self.mm_per_step)
            #print "incrementing %r steps"%(-.01/self.mm_per_step)
        elif self.Z_01.isChecked(): #Z 0.1mm is checked
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
    
    def X_up(self):
        if self.X_001.isChecked(): #X 0.01mm is checked
            self.Xpos = self.Xpos+.01
            self.DRO_X.display(float(self.DRO_X.value())+.01)
            self.printer.IncrementX(.01/self.mm_per_step)
            #print "incrementing %r steps"%(.01/self.mm_per_step)
        elif self.X_01.isChecked(): #X 0.1mm is checked
            self.Xpos = self.Xpos+.1
            self.DRO_X.display(float(self.DRO_X.value())+.1)
            self.printer.IncrementX(.1/self.mm_per_step)
            #print "incrementing %r steps"%(.1/self.mm_per_step)
        elif self.X_1.isChecked(): #X 1mm is checked
            self.Xpos = self.Xpos+1
            self.DRO_X.display(float(self.DRO_X.value())+1)
            self.printer.IncrementX(1/self.mm_per_step)
            #print "incrementing %r steps"%(1/self.mm_per_step)
        elif self.X_10.isChecked(): #X 10mm is checked
            self.Xpos = self.Xpos+10
            self.DRO_X.display(float(self.DRO_X.value())+10)
            self.printer.IncrementX(10/self.mm_per_step)
            #print "incrementing %r steps"%(10/self.mm_per_step)
    
    def X_down(self):
        if self.X_001.isChecked(): #X 0.01mm is checked
            self.Xpos = self.Xpos-.01
            self.DRO_X.display(float(self.DRO_X.value())-.01)
            self.printer.IncrementX(-.01/self.mm_per_step)
            #print "incrementing %r steps"%(.01/self.mm_per_step)
        elif self.X_01.isChecked(): #X 0.1mm is checked
            self.Xpos = self.Xpos-.1
            self.DRO_X.display(float(self.DRO_X.value())-.1)
            self.printer.IncrementX(-.1/self.mm_per_step)
            #print "incrementing %r steps"%(.1/self.mm_per_step)
        elif self.X_1.isChecked(): #X 1mm is checked
            self.Xpos = self.Xpos-1
            self.DRO_X.display(float(self.DRO_X.value())-1)
            self.printer.IncrementX(-1/self.mm_per_step)
            #print "incrementing %r steps"%(1/self.mm_per_step)
        elif self.X_10.isChecked(): #X 10mm is checked
            self.Xpos = self.Xpos-10
            self.DRO_X.display(float(self.DRO_X.value())-10)
            self.printer.IncrementX(-10/self.mm_per_step)
            #print "incrementing %r steps"%(10/self.mm_per_step)
    
    def Zero_Z(self):
        self.Zpos = 0
        self.DRO_Z.display(0)
    
    def Zero_X(self):
        self.Xpos = 0
        self.DRO_X.display(0)

#######################GUI class and event handling#############################
class OpenAbout(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
    
#*****************************
#class OpenProgressBar(QtGui.QDialog, Ui_Progress):
#    def __init__(self,parent=None):
#        QtGui.QDialog.__init__(self,parent)
#        self.setupUi(self)
#        self.ctimer = QtCore.QTimer()
#        self.ctimer.start(10)
#        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.constantUpdate)
#    
#    def constantUpdate(self):
#        if progressBLAH:
#            self.progressbar.setValue(progressBLAH*100)
#            previousval = progressBLAH
#            if progressBLAH == 1:
#                sleep(.5)
#                self.close()
#**********************************************************************************************************************************

#**********************************************************************************************************************************
# Create a class for our main window
class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        pass
        #print Event.size().height() #mainwindow size 
        #print self.ui.ModelFrame.geometry().width(), self.ui.ModelFrame.geometry().height()
        ###self.ModelView.resize(self.ui.ModelFrame.geometry().width()-15,self.ui.ModelFrame.geometry().height()-39)
        

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Host", None, QtGui.QApplication.UnicodeUTF8))
        
        #add toolbar labels
        label = QtGui.QLabel(" Current Layer:")
        self.ui.toolBar_3.addWidget(label)
        label2 = QtGui.QLabel(" 0 of 0")
        self.ui.toolBar_3.addWidget(label2)
        
        self.cwd = os.getcwd() #get current execution (working) directory
        
        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #####################

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(.4,.4,.4)
        
        # create the modelview widget
        self.ModelView = QVTKRenderWindowInteractor(self.ui.splitter)
        self.ModelView.SetInteractorStyle(MyInteractorStyle())
        self.ModelView.Initialize()
        self.ModelView.Start()

        #self.ModelView.setGeometry(200,200,200,200)
        self.renWin=self.ModelView.GetRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.ModelView.show()

        #self.ModelView.SetFixedSize(500,500)
        #self.ModelView.setBaseSize(200,200)
        #self.ModelView.resize(self.ui.ModelFrame.geometry().width()-500,self.ui.ModelFrame.geometry().height()-500)
        #self.ModelView.resize(690-100,550-100)

        #####################
        # create the sliceview widget
        self.SliceView = QVTKRenderWindowInteractor(self.ui.splitter)
        self.SliceView.SetInteractorStyle(MyInteractorStyle())
        self.SliceView.blockSignals(True)
        #self.SliceView.setFixedSize(294,200)
        #self.SliceView.resize(self.ui.SliceFrame.geometry().width()+8,self.ui.SliceFrame.geometry().height()-39)
        self.SliceView.Initialize()

        self.sliceren = vtk.vtkRenderer()
        self.sliceren.InteractiveOff() #why doesnt this work?!
        
        self.sliceWin = self.SliceView.GetRenderWindow()
        self.sliceWin.AddRenderer(self.sliceren)
        self.SliceView.Start()
        #######################        
        print self.ui.splitter.sizes()
        self.screencount = QtGui.QDesktopWidget().numScreens()
        print "number of monitors: ", self.screencount

        #autodetect COM ports:  
        self.ports = comscan.comscan() #returns a list with each entry being a dict of useful information
        print self.ports
        self.numports = len(self.ports) #how many dicts did comscan return?
        
        #print "Found %d ports, %d available." %(length, numports)
        #*********************************
        #IF YOU'RE EVER GOING TO LOAD PREVIOUS SETTINGS, DO IT HERE. 
        self.parser = SafeConfigParser()
        self.parser.read('config.ini')
        self.LoadSettingsFromConfigFile()

        #*********************************
        #After settings are loaded (default or saved), load all the settings into variables for use.
        
        self.ZStepPin = int(self.parser.get('pin_mapping', 'zstep'))
        self.ZDirPin = int(self.parser.get('pin_mapping', 'zdir'))
        self.XStepPin = int(self.parser.get('pin_mapping', 'xstep'))
        self.XDirPin = int(self.parser.get('pin_mapping', 'xdir'))
        self.ZEnablePin = int(self.parser.get('pin_mapping', 'zenable'))
        self.XEnablePin = int(self.parser.get('pin_mapping', 'xenable'))
        
        self.zscript = self.parser.get('scripting', 'sequence')
        self.projector_poweroffcommand = self.parser.get('program_defaults', 'PowerOffCommand')
        #bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        self.printerbaud = self.parser.get('program_defaults', 'Printer_Baud')
        self.exposure_time = self.parser.get('program_defaults', 'ExposeTime')
        self.starting_layers = self.parser.get('program_defaults', 'NumStartLayers')
        self.starting_layer_exposure = self.parser.get('program_defaults', 'StartLayersExposeTime')
        
#        if self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO UNO':
#            self.ui.radio_arduinoUno.click()
#        elif self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO MEGA':
#            self.ui.radio_arduinoMega.click()
#        elif self.parser.get('program_defaults', 'printercontroller') == 'PYMCU':
#            self.ui.radio_pyMCU.click()
#        if self.parser.get('program_defaults', 'slideshowenabled') == 'True':
#            self.ui.enableslideshow.click()
#        if self.parser.get('program_defaults', 'printercontrol') == 'True':
#            self.ui.enableprintercontrol.click()
#        if self.parser.get('program_defaults', 'projectorcontrol') == 'True':
#            self.ui.projectorcontrol.click()
            
#        self.ProjectorControlToggled() #enable or disable projector stuff based on current status of projector enable checkbox
        
        #*********************************
#        if self.ui.radio_pyMCU.isChecked(): #if selected on startup: means projector comms are handled through it. disable printer com config stuff. 
#            self.ui.projector_pickcom.setEnabled(False)
#            self.ui.projector_baud.setEnabled(False)
#            self.ui.projector_parity.setEnabled(False)
#            self.ui.projector_databits.setEnabled(False)
#            self.ui.projector_stopbits.setEnabled(False)
#            self.ui.zscript.setEnabled(False)
        #*********************************
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__           
        
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.ui.consoletext.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.consoletext.setTextCursor(cursor)
        self.ui.consoletext.ensureCursorVisible()
            
#    def ProjectorControlToggled(self):
#        if self.ui.projectorcontrol.isChecked(): #only if projector control is enabled can you re-enable all the control settings.
#            self.ui.projector_pickcom.setEnabled(True)
#            self.ui.projector_baud.setEnabled(True)
#            self.ui.projector_parity.setEnabled(True)
#            self.ui.projector_databits.setEnabled(True)
#            self.ui.projector_stopbits.setEnabled(True)
#            self.ui.projector_poweroffcommand.setEnabled(True)
#            self.ui.projector_testpoweroffcommand.setEnabled(True)
#        else:
#            self.ui.projector_pickcom.setEnabled(False)
#            self.ui.projector_baud.setEnabled(False)
#            self.ui.projector_parity.setEnabled(False)
#            self.ui.projector_databits.setEnabled(False)
#            self.ui.projector_stopbits.setEnabled(False)
#            self.ui.projector_poweroffcommand.setEnabled(False)
#            self.ui.projector_testpoweroffcommand.setEnabled(False)

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
        #print cutStrips.GetOutput()
        
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
#        
#        self.sliceActor = vtk.vtkActor()
#        self.sliceActor.GetProperty().SetColor(1,1,1)
#        self.sliceActor.SetMapper(self.cutterMapper)
# 
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
        self.ren.AddActor(self.slicingplaneActor)
        self.ren.AddActor(self.slicingplaneoutlineActor)
        self.ren.AddActor(self.outlineActor)
        self.sliceren.AddActor(self.slicingplaneActor)
        self.sliceren.ResetCamera()
        self.sliceren.ResetCameraClippingRange(-100.0,100.0,-100.0,100.0,-100.0,100.0)
        self.sliceren.InteractiveOff() #why doesnt this work?!
        self.SliceView.Render()
        #self.SliceView.Disable()
        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.ren.ResetCamera()  
        self.ModelView.Render() #update model view
        print self.ui.splitter.sizes()
    
    def IncrementSlicingPlanePositive(self):
        self.previousPlaneZVal = self.slicingplane.GetOrigin()[2] #pull Z coordinate off plane origin 
        self.slicingplane.SetOrigin(0,0,self.previousPlaneZVal+1)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.ren.Render()
        self.sliceren.Render()
        self.ModelView.Render()
        self.SliceView.Render()
        
    def IncrementSlicingPlaneNegative(self):
        self.previousPlaneZVal = self.slicingplane.GetOrigin()[2] #pull Z coordinate off plane origin 
        self.slicingplane.SetOrigin(0,0,self.previousPlaneZVal-1)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.ren.Render()
        self.sliceren.Render()
        self.ModelView.Render()
        self.SliceView.Render()
        
    def GoToLayer(self):
        pass
        
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
            
    def LoadSettingsFromConfigFile(self):
        print "Loading printing settings from config.ini"
        bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        self.printerbaud = bauddict[self.parser.get('program_defaults', 'Printer_Baud')]
 
        self.zscript = self.parser.get('scripting', 'sequence')
        self.projector_poweroffcommand = self.parser.get('program_defaults', 'PowerOffCommand')

        self.ExposeTime = self.parser.get('program_defaults', 'ExposeTime')
        self.NumberOfStartLayers = self.parser.get('program_defaults', 'NumStartLayers')
        self.StartLayersExposureTime = self.parser.get('program_defaults', 'StartLayersExposeTime')
        
        if self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO UNO':
            self.controller = "arduinoUNO"
        elif self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO MEGA':
            self.controller = "arduinoMEGA"
        elif self.parser.get('program_defaults', 'printercontroller') == 'PYMCU':
            self.controller = "pymcu"
        elif self.parser.get('program_defaults', 'printercontroller') == 'RAMPS':
            self.controller = "ramps"
        if self.parser.get('program_defaults', 'slideshowenabled') == 'True':
            self.slideshowenabled = True
        else:
            self.slideshowenabled = False
        if self.parser.get('program_defaults', 'printercontrol') == 'True':
            self.enableprintercontrol = True
        else:
            self.enableprintercontrol = False
        if self.parser.get('program_defaults', 'projectorcontrol') == 'True':
            self.projectorcontrolenabled = True
        else:
            self.projectorcontrolenabled = False
            
        self.COM_Port = self.parser.get('program_defaults', 'printerCOM')
        self.Printer_Baud = self.parser.get('program_defaults', 'printerBAUD')
        self.screennumber = self.parser.get('program_defaults', 'screennumber')
        
        self.pitch = int(self.parser.get('printer_hardware', 'Leadscrew_pitch'))
        self.steps_per_rev = int(self.parser.get('printer_hardware', 'Steps_per_rev'))
            
    def OpenSettingsDialog(self):
        self.SettingsDialog = StartSettingsDialog(self)
        
        for x in range(self.numports):
            portentry = self.ports[x] #switch to dict x
            if portentry['available'] == True: #if it is currently available
                portname = portentry['name'] #find the name of the port
                #print portname 
                self.SettingsDialog.pickcom.addItem(portname)
                self.SettingsDialog.pickcom.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
                self.SettingsDialog.projector_pickcom.addItem(portname)
                self.SettingsDialog.projector_pickcom.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
        ####setup screen picker####
        for x in range(self.screencount):
            self.SettingsDialog.pickscreen.addItem("")
            self.SettingsDialog.pickscreen.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%d"%x, None, QtGui.QApplication.UnicodeUTF8))

        bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        self.SettingsDialog.printerbaud.setCurrentIndex(bauddict[self.printerbaud])
 
        #insert all other values from current namespace
        self.SettingsDialog.zscript.setPlainText(self.zscript)
        self.SettingsDialog.projector_poweroffcommand.setText(self.projector_poweroffcommand)

        self.SettingsDialog.exposure_time.setText(self.exposure_time)
        self.SettingsDialog.starting_layers.setText(self.starting_layers)
        self.SettingsDialog.starting_layer_exposure.setText(self.starting_layer_exposure)
        
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
        if self.parser.get('program_defaults', 'projectorcontrol') == 'True':
            self.SettingsDialog.projectorcontrol.click()
        
        #self.getSettingsDialogValues()
        self.connect(self.SettingsDialog, QtCore.SIGNAL('ApplySettings()'), self.getSettingsDialogValues)
        self.SettingsDialog.exec_()
        
    def getSettingsDialogValues(self):
        print "got here"
        self.zscript = self.SettingsDialog.zscript.document().toPlainText()
        self.COM_Port = self.SettingsDialog.pickcom.currentText()
        self.Printer_Baud = int(self.SettingsDialog.printerbaud.currentText())
        self.ExposeTime = float(self.SettingsDialog.exposure_time.text())
        #AdvanceTime = float(self.ui.advance_time.text())
        self.Port = self.SettingsDialog.remote_port.text()
        self.NumberOfStartLayers = float(self.SettingsDialog.starting_layers.text())
        self.StartLayersExposureTime = float(self.SettingsDialog.starting_layer_exposure.text())
        self.projector_com = self.SettingsDialog.projector_pickcom.currentText()
        self.projector_baud = self.SettingsDialog.projector_baud.currentText()

        if self.SettingsDialog.projectorcontrol.isChecked():
            self.projectorcontrolenabled = True
        else:
            self.projectorcontrolenabled = False
            
        if self.SettingsDialog.enableprintercontrol.isChecked():
            self.printercontrolenabled = True  
        else:
            self.printercontrolenabled = False

        if self.SettingsDialog.enableslideshow.isChecked():
            self.slideshowenabled = True
        if self.SettingsDialog.radio_pyMCU.isChecked():
            self.controller = "pymcu"
        self.screennumber = self.SettingsDialog.pickscreen.currentText() #get the screen number from picker
        if self.SettingsDialog.radio_arduinoUno.isChecked():
            self.controller = "arduinoUNO"
        if self.SettingsDialog.radio_arduinoMega.isChecked():
            self.controller = "arduinoMEGA"
        if self.SettingsDialog.radio_ramps.isChecked():
            self.controller = "ramps"
         
    def openhelp(self):
        webbrowser.open("http://www.chrismarion.net/3dlp/software/help")
        
    def openmanualcontrol(self):
        ManualControl = StartManualControl(self)
        ManualControl.exec_()
        
    def updatepreview(self):
        #print"updating picture"
        pass        
        #pmscaled = pm.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        #self.ui.imagepreview.setPixmap(pmscaled)
        
    def updatepreviewblank(self):
        pass
        #print"updating pictire to blank slide"    
        #blankpath = "%s\\10x10black.png" %(startingexecutionpath)
        #pm = QtGui.QPixmap(blankpath)
        #pmscaled = pm.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        #self.ui.imagepreview.setPixmap(pmscaled)#set black pixmap for blank slide
    
    def disablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(False)

    def enablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(True)        
        
    def openaboutdialog(self):
        dialog = OpenAbout(self)
        dialog.exec_()
        
    def printpressed(self):    
        self.printThread = printmodel.printmodel(self.zscript, self.COM_Port, self.Printer_Baud, self.ExposeTime
                                                , self.NumberOfStartLayers, self.StartLayersExposureTime
                                                , self.projectorcontrolenabled, self.controller, self.screennumber, self.cwd, self)
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
    
    splash_pix = QPixmap('3dlp_splash.png')
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
    
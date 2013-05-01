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
    -generate 3d preview from layer slice images, scrolls through in real-time with the print job
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
        self.printer = parent.printer
        self.setupUi(self)
        self.mm_per_step = float(parent.pitch)/float(parent.steps_per_rev)
        self.microstepping = 0.0625 #1/16th microstepping
        print self.microstepping
        self.mm_per_step = self.mm_per_step#/self.microstepping
        self.Zpos = 0.0
        self.Xpos = 0.0

    def Z_up(self):
        if self.Z_001.isChecked(): #Z 0.01mm is checked
            self.Zpos = self.Zpos+.01
            self.DRO_Z.display(float(self.DRO_Z.value())+.01)
            self.printer.IncrementZ((.01/self.mm_per_step))
            #print "incrementing %r steps"%(.01/self.mm_per_step)
        elif self.Z_01.isChecked(): #Z 0.1mm is checked
            self.Zpos = self.Zpos+.1
            self.DRO_Z.display(float(self.DRO_Z.value())+.1)
            self.printer.IncrementZ((.1/self.mm_per_step))
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

class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        self.ModelView.resize(self.ui.frame.geometry().width(),self.ui.frame.geometry().height())
        self.slicepreview.resize(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height())
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)  
        
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Host", None, QtGui.QApplication.UnicodeUTF8))
        
        #add toolbar labels
        label = QtGui.QLabel(" Current Layer: ")
        self.ui.toolBar_3.addWidget(label)
        self.layercount = QtGui.QLabel("0 of 0")
        self.ui.toolBar_3.addWidget(self.layercount)
        self.cwd = os.getcwd() #get current execution (working) directory
        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(.4,.4,.4)
        
        # create the modelview widget
        self.ModelView = QVTKRenderWindowInteractor(self.ui.frame)
        self.ModelView.SetInteractorStyle(MyInteractorStyle())
        self.ModelView.Initialize()
        self.ModelView.Start()

        self.renWin=self.ModelView.GetRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.ModelView.show()

        self.slicepreview = QtGui.QLabel(self.ui.frame_2)
        pm = QtGui.QPixmap(os.getcwd() + "\\10x10black.png")
        pmscaled = pm.scaled(400, 600)
        self.slicepreview.setPixmap(pmscaled) #set black pixmap for blank slide     

        self.screencount = QtGui.QDesktopWidget().numScreens()
        print "number of monitors: ", self.screencount

        self.ports = comscan.comscan() #returns a list with each entry being a dict of useful information
        print self.ports
        self.numports = len(self.ports) #how many dicts did comscan return?
        
        #print "Found %d ports, %d available." %(self.numports, numports)

        self.parser = SafeConfigParser()
        self.parser.read('config.ini')
        self.LoadSettingsFromConfigFile()
   
        self.zscript = self.parser.get('scripting', 'sequence')
        self.projector_poweroffcommand = self.parser.get('program_defaults', 'PowerOffCommand')
        #bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        self.printerbaud = self.parser.get('program_defaults', 'printerBAUD')
        self.exposure_time = self.parser.get('program_defaults', 'ExposeTime')
        self.starting_layers = self.parser.get('program_defaults', 'NumStartLayers')
        self.starting_layer_exposure = self.parser.get('program_defaults', 'StartLayersExposeTime')
        self.ModelView.resize(self.ui.frame.geometry().width(),self.ui.frame.geometry().height())
        
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
            
    def OpenPrintJob(self):
        self.printDirectory = str(QFileDialog.getExistingDirectory(self, "Select Directory of Desired Print Job"))
        if not os.path.isdir(self.printDirectory + "\\slices"):
            print "no slices directory found"
            return
        self.FileList = []
        for file in os.listdir(self.printDirectory + "\\slices"): #for every file in slices dir (changed dir above)
            if file.endswith(".png"): #if it's a supported image type
                imagepath = self.printDirectory + "\\slices\\" + file
                self.FileList.append(imagepath)
        if len(self.FileList)<1:
            print "no valid slice images were found"
            return
        if not os.path.isfile(self.printDirectory + "\\printconfiguration.ini"):
            print "no print configuration file was found"
            return
        try:
            self.printconfigparser = SafeConfigParser()
            self.printconfigparser.read(self.printDirectory + '\\printconfiguration.ini')
        except:
            print "unknown error encountered while trying to parse print configuration file"
            return
        self.OpenModel(self.printconfigparser.get('print_settings', 'STL_name'))
        self.currentlayer = 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm = QtGui.QPixmap(self.FileList[self.currentlayer-1]) #remember to compensate for 0-index
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)    
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        self.slicepreview.resize(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height())

    def OpenModel(self, filename):
        self.ModelView.resize(self.ui.frame.geometry().width(),self.ui.frame.geometry().height()) #just in case resizeEvent() hasn't been called yet

        self.filename = filename
        
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
        self.previousPlaneZVal = self.slicingplane.GetOrigin()[2] #pull Z coordinate off plane origin 
        self.slicingplane.SetOrigin(0,0,self.previousPlaneZVal+1)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.ren.Render()
        self.ModelView.Render()
        #####slice preview
        self.currentlayer = self.currentlayer + 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm = QtGui.QPixmap(self.FileList[self.currentlayer-1]) #remember to compensate for 0-index
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)    
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        
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
        self.ModelView.Render()
        #####slice preview
        self.currentlayer = self.currentlayer - 1
        self.layercount.setText(str(self.currentlayer) + " of " + str(len(self.FileList)))
        self.pm = QtGui.QPixmap(self.FileList[self.currentlayer-1]) #remember to compensate for 0-index
        self.pmscaled = self.pm.scaled(self.ui.frame_2.geometry().width(), self.ui.frame_2.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)    
        QApplication.processEvents() #make sure the toolbar gets updated with new text
        
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
        self.printerbaud = bauddict[self.parser.get('program_defaults', 'printerBAUD')]
 
        self.zscript = self.parser.get('scripting', 'sequence')
        self.projector_poweroffcommand = self.parser.get('program_defaults', 'PowerOffCommand')

        self.ExposeTime = self.parser.get('program_defaults', 'ExposeTime')
        self.NumberOfStartLayers = self.parser.get('program_defaults', 'NumStartLayers')
        self.StartLayersExposureTime = self.parser.get('program_defaults', 'StartLayersExposeTime')
        
        if self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO_UNO':
            self.controller = "arduinoUNO"
        elif self.parser.get('program_defaults', 'printercontroller') == 'ARDUINO_MEGA':
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

        ####setup screen picker####
        for x in range(self.screencount):
            self.SettingsDialog.pickscreen.addItem("")
            self.SettingsDialog.pickscreen.setItemText(x, QtGui.QApplication.translate("SettingsDialogBaseClass", "%d"%x, None, QtGui.QApplication.UnicodeUTF8))
 
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
        self.parser.set('scripting', 'sequence', '%s'%self.zscript)
        self.COM_Port = self.SettingsDialog.pickcom.currentText()
        self.parser.set('program_defaults', 'printerCOM', '%s'%self.COM_Port)

        self.ExposeTime = float(self.SettingsDialog.exposure_time.text())
        self.parser.set('program_defaults', 'ExposeTime', '%s'%self.ExposeTime)
        #AdvanceTime = float(self.ui.advance_time.text())
        self.NumberOfStartLayers = float(self.SettingsDialog.starting_layers.text())
        self.parser.set('program_defaults', 'NumStartLayers', '%s'%self.NumberOfStartLayers)
        self.StartLayersExposureTime = float(self.SettingsDialog.starting_layer_exposure.text())
        self.parser.set('program_defaults', 'StartLayersExposeTime', '%s'%self.StartLayersExposureTime)
        self.projector_baud = self.SettingsDialog.projector_baud.currentText()
        self.parser.set('program_defaults', 'projectorBAUD', '%s'%self.projector_baud)

        if self.SettingsDialog.projectorcontrol.isChecked():
            self.projectorcontrolenabled = True
            self.parser.set('program_defaults', 'projectorcontrol', 'True')
        else:
            self.projectorcontrolenabled = False
            self.parser.set('program_defaults', 'projectorcontrol', 'False')
            
        if self.SettingsDialog.enableprintercontrol.isChecked():
            self.printercontrolenabled = True  
            self.parser.set('program_defaults', 'printercontrol', 'True')
        else:
            self.printercontrolenabled = False
            self.parser.set('program_defaults', 'printercontrol', 'False')

        if self.SettingsDialog.enableslideshow.isChecked():
            self.slideshowenabled = True
            self.parser.set('program_defaults', 'slideshowenabled', 'True')
        else:
            self.slideshowenabled = False
            self.parser.set('program_defaults', 'slideshowenabled', 'False')
        if self.SettingsDialog.radio_pyMCU.isChecked():
            self.controller = "pymcu"
            self.parser.set('program_defaults', 'printercontroller', 'PYMCU')
        self.screennumber = self.SettingsDialog.pickscreen.currentText() #get the screen number from picker
        if self.SettingsDialog.radio_arduinoUno.isChecked():
            self.controller = "arduinoUNO"
            self.parser.set('program_defaults', 'printercontroller', 'ARDUINO_UNO')
        if self.SettingsDialog.radio_arduinoMega.isChecked():
            self.controller = "arduinoMEGA"
            self.parser.set('program_defaults', 'printercontroller', 'ARDUINO_MEGA')
        if self.SettingsDialog.radio_ramps.isChecked():
            self.controller = "ramps"
            self.parser.set('program_defaults', 'printercontroller', 'RAMPS')
        outputini = open('config.ini', 'w') #open a file pointer for the config file parser to write changes to
        self.parser.write(outputini)
        outputini.close() #done writing config file changes
         
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
        print "Connecting to printer.."
        self.printer = hardware.ramps(self.COM_Port)
        if self.printer.status == 1:
            print "unknown error encountered while trying to connect to printer."
            return
        
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
        try: #check to see if printer object exists
            if self.printer:
                pass
        except:
            QtGui.QMessageBox.critical(self, 'Error starting print job',"You must first connect to a printer to print to it!", QtGui.QMessageBox.Ok)
            return   
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
    
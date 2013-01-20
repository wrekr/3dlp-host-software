# -*- coding: utf-8 -*-
"""
Created on Thu Apr 05 22:20:39 2012

@author: Chris Marion Copyright 2012
www.chrismarion.net

Still to add/known issues:
    -clean exiting of threads, possibly using constant timers? ARGHHH
    -after the printmodel and slicemodel classes are perfected combine them into print&slice
    -fix ETA and advance time
    -projector control functionality is not finished.
    -I would like to support many different hardware types - poll community on hardware (drivers, feedback control, etc.)
    -Manual printer control dialog for manually jogging each printer axis
    -still looking for a good method of calibrating for X and Y (image size)
"""
from subprocess import Popen, PIPE
import sys
import shutil
import serial
import socket
import Queue
import threading
import comscan
import pyfirmata
import webbrowser
from ConfigParser import *
import re
from time import sleep
import ctypes
import printmodel
import vtk
from settingsdialog import Ui_SettingsDialogBaseClass
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#**********************************

import os
from qtgui import Ui_MainWindow #import generated class from ui file from designer 
from slideshowgui import SlideShowWindow
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
        
    def quit(self):
        print "quitting"

#######################GUI class and event handling#############################
class OpenAbout(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
    
#*******************************************************************************


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
        screencount = QtGui.QDesktopWidget().numScreens()
        print "number of monitors: ", screencount
         ####setup screen picker####
#        for x in range(screencount):
#            self.ui.pickscreen.addItem("")
#            self.ui.pickscreen.setItemText(x, QtGui.QApplication.translate("MainWindow", "%d"%x, None, QtGui.QApplication.UnicodeUTF8))
        #autodetect COM ports:  
        ports = comscan.comscan() #returns a list with each entry being a dict of useful information
        print ports
        length = len(ports) #how many dicts did comscan return?
        numports = 0
        for x in range(length):
            portentry = ports[x] #switch to dict x
            if portentry['available'] == True: #if it is currently available
                portname = portentry['name'] #find the name of the port
                #print portname 
                numports = numports + 1
#                self.ui.pickcom.addItem(portname)
#                self.ui.pickcom.setItemText(x, QtGui.QApplication.translate("MainWindow", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
#                self.ui.projector_pickcom.addItem(portname)
#                self.ui.projector_pickcom.setItemText(x, QtGui.QApplication.translate("MainWindow", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
        print "Found %d ports, %d available." %(length, numports)
        #*********************************
        #IF YOU'RE EVER GOING TO LOAD PREVIOUS SETTINGS, DO IT HERE. 
        parser = SafeConfigParser()
        parser.read('config.ini')

        #*********************************
        #After settings are loaded (default or saved), load all the settings into variables for use.
        global screennumber
        global ImageFilename
        global Filename
        global ZStepPin, ZDirPin, XStepPin, XDirPin, ZEnablePin, XEnablePin
        
        ZStepPin = int(parser.get('pin_mapping', 'zstep'))
        ZDirPin = int(parser.get('pin_mapping', 'zdir'))
        XStepPin = int(parser.get('pin_mapping', 'xstep'))
        XDirPin = int(parser.get('pin_mapping', 'xdir'))
        ZEnablePin = int(parser.get('pin_mapping', 'zenable'))
        XEnablePin = int(parser.get('pin_mapping', 'xenable'))
        
#        self.ui.zscript.setPlainText(parser.get('scripting', 'sequence'))
#        self.ui.projector_poweroffcommand.setText(parser.get('program_defaults', 'PowerOffCommand'))
#        bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
#        self.ui.printerbaud.setCurrentIndex(bauddict[parser.get('program_defaults', 'Printer_Baud')])
#        self.ui.exposure_time.setText(parser.get('program_defaults', 'ExposeTime'))
#        self.ui.starting_layers.setText(parser.get('program_defaults', 'NumStartLayers'))
#        self.ui.starting_layer_exposure.setText(parser.get('program_defaults', 'StartLayersExposeTime'))
#        self.ui.image_height.setText(parser.get('program_defaults', 'ImageHeight'))
#        self.ui.image_width.setText(parser.get('program_defaults', 'ImageWidth'))
#        self.ui.layer_thickness.setText(parser.get('program_defaults', 'LayerThickness'))
#        self.ui.z_options_start.setText(parser.get('program_defaults', 'z_options_start'))
#        self.ui.z_options_end.setText(parser.get('program_defaults', 'z_options_end'))
#        self.ui.z_options_increment.setText(parser.get('program_defaults', 'z_options_increment'))
#        planedict = {'XZ':0, 'XY':1, 'YZ':2}
#        self.ui.slicing_plane.setCurrentIndex(planedict[parser.get('program_defaults', 'plane')])
#        
#        if parser.get('program_defaults', 'printercontroller') == 'ARDUINO UNO':
#            self.ui.radio_arduinoUno.click()
#        elif parser.get('program_defaults', 'printercontroller') == 'ARDUINO MEGA':
#            self.ui.radio_arduinoMega.click()
#        elif parser.get('program_defaults', 'printercontroller') == 'PYMCU':
#            self.ui.radio_pyMCU.click()
#        if parser.get('program_defaults', 'slideshowenabled') == 'True':
#            self.ui.enableslideshow.click()
#        if parser.get('program_defaults', 'printercontrol') == 'True':
#            self.ui.enableprintercontrol.click()
#        if parser.get('program_defaults', 'projectorcontrol') == 'True':
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
                
    def SlideshowControlToggled(self):
        global slideshowenabled
        if self.ui.enableslideshow.isChecked():
            self.ui.pickscreen.setEnabled(True)
            slideshowenabled = True
        else:
            self.ui.pickscreen.setEnabled(False)
            slideshowenabled = False

    def EnablePrinterControlToggled(self):
        if self.ui.enableprintercontrol.isChecked():
            self.ui.pickcom.setEnabled(True)
            self.ui.printerbaud.setEnabled(True)
            self.ui.radio_pyMCU.setEnabled(True)
            self.ui.radio_arduinoUno.setEnabled(True)
            self.ui.radio_arduinoMega.setEnabled(True)
            self.printercontrolenabled = True
        else:
            self.ui.pickcom.setEnabled(False)
            self.ui.printerbaud.setEnabled(False)
            self.ui.radio_pyMCU.setEnabled(False)
            self.ui.radio_arduinoUno.setEnabled(False)
            self.ui.radio_arduinoMega.setEnabled(False)
            self.printercontrolenabled = False
            
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
        
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        self.slicingplane=vtk.vtkPlane()
        self.slicingplane.SetOrigin(0,0,20)
        self.slicingplane.SetNormal(0,0,1)
        
        #create cutter
        self.cutter=vtk.vtkCutter()
        self.cutter.SetCutFunction(self.slicingplane)
        self.cutter.SetInputConnection(self.reader.GetOutputPort())
        self.cutter.Update()

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
            
    def OpenSettingsDialog(self):
        SettingsDialog = StartSettingsDialog(self)
        SettingsDialog.exec_()
            
    def openhelp(self):
        webbrowser.open("http://www.chrismarion.net/3dlp/software/help")
        
    def openmanualcontrol(self):
        pass
        
    def updatepreview(self):
        #print"updating picture"        
        pmscaled = pm.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.ui.imagepreview.setPixmap(pmscaled)
        
    def updatepreviewblank(self):
        #print"updating pictire to blank slide"    
        blankpath = "%s\\10x10black.png" %(startingexecutionpath)
        pm = QtGui.QPixmap(blankpath)
        pmscaled = pm.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.ui.imagepreview.setPixmap(pmscaled)#set black pixmap for blank slide
    
    def disablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(False)

    def enablestopbutton(self):
        self.ui.button_stop_printing.setEnabled(True)        
        
    def openaboutdialog(self):
        dialog = OpenAbout(self)
        dialog.exec_()
        
    def printpressed(self):    
        self.zscriptdoc = self.ui.zscript.document()
        self.zscript = self.zscriptdoc.toPlainText()
        self.COM_Port = self.ui.pickcom.currentText()
        self.Printer_Baud = int(self.ui.printerbaud.currentText())
        self.ExposeTime = float(self.ui.exposure_time.text())
        #AdvanceTime = float(self.ui.advance_time.text())
        self.Port = self.ui.remote_port.text()
        self.NumberOfStartLayers = float(self.ui.starting_layers.text())
        self.StartLayersExposureTime = float(self.ui.starting_layer_exposure.text())
        self.projector_com = self.ui.projector_pickcom.currentText()
        self.projector_baud = self.ui.projector_baud.currentText()
        self.projector_parity = self.ui.projector_parity.currentText()
        self.projector_stopbits = self.ui.projector_stopbits.currentText()
        self.projector_databits = self.ui.projector_databits.currentText()

        if self.ui.projectorcontrol.isChecked():
            self.projectorcontrolenabled = True
        else:
            self.projectorcontrolenabled = False
            
        if self.ui.enableprintercontrol.isChecked():
            self.printercontrolenabled = True  
        else:
            self.printercontrolenabled = False

        if self.ui.enableslideshow.isChecked():
            self.slideshowenabled = True
        if self.ui.radio_pymcu.isChecked():
            self.controller = "pymcu"
        self.screennumber = self.ui.pickscreen.currentText() #get the screen number from picker
        if self.ui.radio_uno.isChecked():
            self.controller = "arduinoUno"
        if self.ui.radio_mega.isChecked():
            self.controller = "arduinoMega"
          
        self.printThread = printmodel.printmodel(self.zscript, self.COM_Port, self.Printer_Baud, self.ExposeTime,self.Port
                                                , self.NumberOfStartLayers, self.StartLayersExposureTime, self.projector_baud
                                                , self.projector_com, self.projector_databits, self.projector_parity, self.projector_stopbits
                                                , self.projectorcontrolenabled, self.controller)
        #connect to slideshow signal
        self.connect(self.printThread, QtCore.SIGNAL('updatePreview'), self.updatepreview)      
        self.connect(self.printThread, QtCore.SIGNAL('updatePreviewBlank'), self.updatepreviewblank)      
        self.connect(self.printThread, QtCore.SIGNAL('disable_stop_button'), self.disablestopbutton) 
        self.connect(self.printThread, QtCore.SIGNAL('enable_stop_button'), self.enablestopbutton)     

################################################################################
def GetInHMS(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    #print "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d:%02d" % (h, m, s)

################################################################################        
def main():
    #start thread with old 3dlp stuff

    ####

    ################pyQt stuff
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    ###############
    

if __name__ == "__main__":
    main()
    
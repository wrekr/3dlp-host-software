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

import slicer

from newHardware import Ui_dialogHardware
from newResin import Ui_dialogResin

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
    
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

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
    
class hardwareProfile():
    def __init__(self):
        self.name = ""
        self.COM = ""
        self.leadscrewPitchZ = 0
        self.stepsPerRevZ = 0
        self.steppingMode = ""
        self.layerThickness = ""
        self.projectorResolution = (0,0)
        self.buildAreaSize = (0,0)
        self.pixelSize = (0,0)
    
class _3dlpfile():
    def __init__(self):
        self.name = ""
        self.description = ""
        self.notes = ""
        self.hardwareProfile = None
        
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
        self.parent.renPre.AddActor(self.actor)
        self.parent.renPre.AddActor(self.outlineActor)
        
class NewHardwareProfileDialog(QtGui.QDialog):
    def __init__(self, parent, mainparent):
        super(NewHardwareProfileDialog, self).__init__(parent)
        self.setWindowTitle("Define New Hardware Profile")
        self.resize(558, 375)
        
        self.verticalLayout_6 = QtGui.QVBoxLayout(self)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setText(QtGui.QApplication.translate("dialogHardware", "Define New Hardware Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setTitle(QtGui.QApplication.translate("dialogHardware", "Controller Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.radio_ramps = QtGui.QRadioButton(self.groupBox)
        self.radio_ramps.setText(QtGui.QApplication.translate("dialogHardware", "RAMPS", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_ramps.setChecked(True)
        self.radio_ramps.setObjectName(_fromUtf8("radio_ramps"))
        self.horizontalLayout_7.addWidget(self.radio_ramps)
        self.radio_arduinoUno = QtGui.QRadioButton(self.groupBox)
        self.radio_arduinoUno.setEnabled(False)
        self.radio_arduinoUno.setText(QtGui.QApplication.translate("dialogHardware", "Arduino Uno", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_arduinoUno.setChecked(False)
        self.radio_arduinoUno.setObjectName(_fromUtf8("radio_arduinoUno"))
        self.horizontalLayout_7.addWidget(self.radio_arduinoUno)
        self.radio_arduinoMega = QtGui.QRadioButton(self.groupBox)
        self.radio_arduinoMega.setEnabled(False)
        self.radio_arduinoMega.setText(QtGui.QApplication.translate("dialogHardware", "Arduino Mega", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_arduinoMega.setObjectName(_fromUtf8("radio_arduinoMega"))
        self.horizontalLayout_7.addWidget(self.radio_arduinoMega)
        self.radio_pyMCU = QtGui.QRadioButton(self.groupBox)
        self.radio_pyMCU.setEnabled(False)
        self.radio_pyMCU.setText(QtGui.QApplication.translate("dialogHardware", "PyMCU", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_pyMCU.setObjectName(_fromUtf8("radio_pyMCU"))
        self.horizontalLayout_7.addWidget(self.radio_pyMCU)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_29 = QtGui.QLabel(self.groupBox)
        self.label_29.setText(QtGui.QApplication.translate("dialogHardware", "COM Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.horizontalLayout_8.addWidget(self.label_29)
        self.pickcom = QtGui.QComboBox(self.groupBox)
        self.pickcom.setObjectName(_fromUtf8("pickcom"))
        self.horizontalLayout_8.addWidget(self.pickcom)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addWidget(self.groupBox)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.groupBox_7 = QtGui.QGroupBox(self)
        self.groupBox_7.setTitle(QtGui.QApplication.translate("dialogHardware", "Hardware Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_22 = QtGui.QHBoxLayout()
        self.horizontalLayout_22.setObjectName(_fromUtf8("horizontalLayout_22"))
        self.label_6 = QtGui.QLabel(self.groupBox_7)
        self.label_6.setText(QtGui.QApplication.translate("dialogHardware", "Z Axis Leadscrew Pitch:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_22.addWidget(self.label_6)
        self.pitchZ = QtGui.QLineEdit(self.groupBox_7)
        self.pitchZ.setObjectName(_fromUtf8("pitchZ"))
        self.horizontalLayout_22.addWidget(self.pitchZ)
        self.label_7 = QtGui.QLabel(self.groupBox_7)
        self.label_7.setText(QtGui.QApplication.translate("dialogHardware", "mm/rev", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_22.addWidget(self.label_7)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_22.addItem(spacerItem4)
        self.verticalLayout_4.addLayout(self.horizontalLayout_22)
        self.horizontalLayout_23 = QtGui.QHBoxLayout()
        self.horizontalLayout_23.setObjectName(_fromUtf8("horizontalLayout_23"))
        self.label_8 = QtGui.QLabel(self.groupBox_7)
        self.label_8.setText(QtGui.QApplication.translate("dialogHardware", "Z Axis Steps/rev:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_23.addWidget(self.label_8)
        self.stepsPerRevZ = QtGui.QLineEdit(self.groupBox_7)
        self.stepsPerRevZ.setObjectName(_fromUtf8("stepsPerRevZ"))
        self.horizontalLayout_23.addWidget(self.stepsPerRevZ)
        self.label_9 = QtGui.QLabel(self.groupBox_7)
        self.label_9.setText(QtGui.QApplication.translate("dialogHardware", "steps", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_23.addWidget(self.label_9)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_23.addItem(spacerItem5)
        self.verticalLayout_4.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_10 = QtGui.QLabel(self.groupBox_7)
        self.label_10.setText(QtGui.QApplication.translate("dialogHardware", "Layer Thickness:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_9.addWidget(self.label_10)
        self.layerThickness = QtGui.QLineEdit(self.groupBox_7)
        self.layerThickness.setObjectName(_fromUtf8("layerThickness"))
        self.horizontalLayout_9.addWidget(self.layerThickness)
        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setText(QtGui.QApplication.translate("dialogHardware", "um", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_9.addWidget(self.label_13)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setText(QtGui.QApplication.translate("dialogHardware", "Projector Resolution (pixels):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_10.addWidget(self.label_11)
        self.projectorResolutionX = QtGui.QLineEdit(self.groupBox_7)
        self.projectorResolutionX.setObjectName(_fromUtf8("projectorResolutionX"))
        self.horizontalLayout_10.addWidget(self.projectorResolutionX)
        self.label_12 = QtGui.QLabel(self.groupBox_7)
        self.label_12.setText(QtGui.QApplication.translate("dialogHardware", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_10.addWidget(self.label_12)
        self.projectorResolutionY = QtGui.QLineEdit(self.groupBox_7)
        self.projectorResolutionY.setObjectName(_fromUtf8("projectorResolutionY"))
        self.horizontalLayout_10.addWidget(self.projectorResolutionY)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem7)
        self.verticalLayout_4.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_14 = QtGui.QLabel(self.groupBox_7)
        self.label_14.setText(QtGui.QApplication.translate("dialogHardware", "Build Area Size (mm):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.horizontalLayout_11.addWidget(self.label_14)
        self.buildAreaX = QtGui.QLineEdit(self.groupBox_7)
        self.buildAreaX.setObjectName(_fromUtf8("buildAreaX"))
        self.horizontalLayout_11.addWidget(self.buildAreaX)
        self.label_15 = QtGui.QLabel(self.groupBox_7)
        self.label_15.setText(QtGui.QApplication.translate("dialogHardware", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.horizontalLayout_11.addWidget(self.label_15)
        self.buildAreaY = QtGui.QLineEdit(self.groupBox_7)
        self.buildAreaY.setObjectName(_fromUtf8("buildAreaY"))
        self.horizontalLayout_11.addWidget(self.buildAreaY)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem8)
        self.verticalLayout_4.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.label_16 = QtGui.QLabel(self.groupBox_7)
        self.label_16.setText(QtGui.QApplication.translate("dialogHardware", "Pixel Size (um):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.horizontalLayout_12.addWidget(self.label_16)
        self.pixelSizeX = QtGui.QLabel(self.groupBox_7)
        self.pixelSizeX.setText(QtGui.QApplication.translate("dialogHardware", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.pixelSizeX.setObjectName(_fromUtf8("pixelSizeX"))
        self.horizontalLayout_12.addWidget(self.pixelSizeX)
        self.label_17 = QtGui.QLabel(self.groupBox_7)
        self.label_17.setText(QtGui.QApplication.translate("dialogHardware", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.horizontalLayout_12.addWidget(self.label_17)
        self.pixelSizeY = QtGui.QLabel(self.groupBox_7)
        self.pixelSizeY.setText(QtGui.QApplication.translate("dialogHardware", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.pixelSizeY.setObjectName(_fromUtf8("pixelSizeY"))
        self.horizontalLayout_12.addWidget(self.pixelSizeY)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem9)
        self.verticalLayout_4.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.groupBox_4 = QtGui.QGroupBox(self.groupBox_7)
        self.groupBox_4.setTitle(QtGui.QApplication.translate("dialogHardware", "Stepping Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.fullStep = QtGui.QRadioButton(self.groupBox_4)
        self.fullStep.setText(QtGui.QApplication.translate("dialogHardware", "Full Stepping", None, QtGui.QApplication.UnicodeUTF8))
        self.fullStep.setChecked(True)
        self.fullStep.setObjectName(_fromUtf8("fullStep"))
        self.verticalLayout_3.addWidget(self.fullStep)
        self.halfStep = QtGui.QRadioButton(self.groupBox_4)
        self.halfStep.setText(QtGui.QApplication.translate("dialogHardware", "1/2 Microstepping", None, QtGui.QApplication.UnicodeUTF8))
        self.halfStep.setObjectName(_fromUtf8("halfStep"))
        self.verticalLayout_3.addWidget(self.halfStep)
        self.quarterStep = QtGui.QRadioButton(self.groupBox_4)
        self.quarterStep.setText(QtGui.QApplication.translate("dialogHardware", "1/4 Microstepping", None, QtGui.QApplication.UnicodeUTF8))
        self.quarterStep.setObjectName(_fromUtf8("quarterStep"))
        self.verticalLayout_3.addWidget(self.quarterStep)
        self.eighthStep = QtGui.QRadioButton(self.groupBox_4)
        self.eighthStep.setText(QtGui.QApplication.translate("dialogHardware", "1/8 Microstepping", None, QtGui.QApplication.UnicodeUTF8))
        self.eighthStep.setObjectName(_fromUtf8("eighthStep"))
        self.verticalLayout_3.addWidget(self.eighthStep)
        self.sixteenthStep = QtGui.QRadioButton(self.groupBox_4)
        self.sixteenthStep.setText(QtGui.QApplication.translate("dialogHardware", "1/16 Microstepping", None, QtGui.QApplication.UnicodeUTF8))
        self.sixteenthStep.setObjectName(_fromUtf8("sixteenthStep"))
        self.verticalLayout_3.addWidget(self.sixteenthStep)
        self.horizontalLayout_13.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3.addWidget(self.groupBox_4)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_5.addWidget(self.groupBox_7)
        spacerItem10 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem10)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_5.addWidget(self.buttonBox)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QObject.connect(self.buildAreaX, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.CalculatePixelSize)
        QtCore.QObject.connect(self.buildAreaY, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.CalculatePixelSize)
        QtCore.QObject.connect(self.projectorResolutionX, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.CalculatePixelSize)
        QtCore.QObject.connect(self.projectorResolutionY, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.CalculatePixelSize)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.pixelSizeX.setText("")
        self.pixelSizeY.setText("")
        
    def CalculatePixelSize(self):
        self.pixelSizeX.setText(str((float(str(self.buildAreaX.text()))/float(str(self.projectorResolutionX.text())))*1000))
        self.pixelSizeY.setText(str((float(str(self.buildAreaY.text()))/float(str(self.projectorResolutionY.text())))*1000))

class wizardNewGeneral(QtGui.QWizardPage):
    def __init__(self, parent, mainparent):
        super(wizardNewGeneral, self).__init__(parent)
        self.parent = mainparent
        self.setTitle("General Print Job Settings")
        self.setSubTitle("test general settings page")    
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_8 = QtGui.QVBoxLayout()
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.groupBox_2 = QtGui.QGroupBox(self)
        self.groupBox_2.setTitle(QtGui.QApplication.translate("WizardPage", "General Information", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Job Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.jobName = QtGui.QLineEdit(self.groupBox_2)
        self.jobName.setObjectName(_fromUtf8("jobName"))
        self.horizontalLayout.addWidget(self.jobName)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.jobDescription = QtGui.QLineEdit(self.groupBox_2)
        self.jobDescription.setObjectName(_fromUtf8("jobDescription"))
        self.horizontalLayout_2.addWidget(self.jobDescription)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "Notes:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.jobNotes = QtGui.QTextEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jobNotes.sizePolicy().hasHeightForWidth())
        self.jobNotes.setSizePolicy(sizePolicy)
        self.jobNotes.setObjectName(_fromUtf8("jobNotes"))
        self.horizontalLayout_4.addWidget(self.jobNotes)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_6.addLayout(self.verticalLayout)
        self.verticalLayout_8.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout_8)
        
    def initializePage(self):
        pass
        
    def validatePage(self):
        self.parent.printJob.name = self.jobName.text()
        self.parent.printJob.description = self.jobDescription.text()
        self.parent.printJob.notes = self.jobNotes.toPlainText()
        return True
        
class wizardNewHardware(QtGui.QWizardPage):
    def __init__(self, parent, mainparent):
        super(wizardNewHardware, self).__init__(parent)
        self.setTitle("Print Job Hardware Settings")
        self.setSubTitle("test hardware settings page")    
        self.parent = mainparent
        self.profile = None
        
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_5 = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setText(QtGui.QApplication.translate("WizardPage", "Load an existing hardware profile:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_6.addWidget(self.label_5)
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.horizontalLayout_6.addWidget(self.comboBox)
        self.toolButton = QtGui.QToolButton(self)
        self.toolButton.setText(QtGui.QApplication.translate("WizardPage", "Create New Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout_6.addWidget(self.toolButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.line = QtGui.QFrame(self)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_3.addWidget(self.line)
        spacerItem = QtGui.QSpacerItem(681, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.groupBox_3 = QtGui.QGroupBox(self)
        self.groupBox_3.setTitle(QtGui.QApplication.translate("WizardPage", "Selected Hardware Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_17.setObjectName(_fromUtf8("verticalLayout_17"))
        self.verticalLayout_16 = QtGui.QVBoxLayout()
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        self.horizontalLayout_31 = QtGui.QHBoxLayout()
        self.horizontalLayout_31.setObjectName(_fromUtf8("horizontalLayout_31"))
        self.groupBox_10 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_10.setTitle(QtGui.QApplication.translate("WizardPage", "Controller Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_10.setObjectName(_fromUtf8("groupBox_10"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.groupBox_10)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_24 = QtGui.QHBoxLayout()
        self.horizontalLayout_24.setObjectName(_fromUtf8("horizontalLayout_24"))
        self.label_46 = QtGui.QLabel(self.groupBox_10)
        self.label_46.setText(QtGui.QApplication.translate("WizardPage", "Controller Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.horizontalLayout_24.addWidget(self.label_46)
        self.controller = QtGui.QLabel(self.groupBox_10)
        self.controller.setText(QtGui.QApplication.translate("WizardPage", "RAMPS", None, QtGui.QApplication.UnicodeUTF8))
        self.controller.setObjectName(_fromUtf8("controller"))
        self.horizontalLayout_24.addWidget(self.controller)
        self.verticalLayout_5.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_30 = QtGui.QHBoxLayout()
        self.horizontalLayout_30.setObjectName(_fromUtf8("horizontalLayout_30"))
        self.label_48 = QtGui.QLabel(self.groupBox_10)
        self.label_48.setText(QtGui.QApplication.translate("WizardPage", "COM Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_48.setObjectName(_fromUtf8("label_48"))
        self.horizontalLayout_30.addWidget(self.label_48)
        self.port = QtGui.QLabel(self.groupBox_10)
        self.port.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.port.setObjectName(_fromUtf8("port"))
        self.horizontalLayout_30.addWidget(self.port)
        self.verticalLayout_5.addLayout(self.horizontalLayout_30)
        self.verticalLayout_14.addLayout(self.verticalLayout_5)
        self.horizontalLayout_31.addWidget(self.groupBox_10)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_31.addItem(spacerItem1)
        self.verticalLayout_16.addLayout(self.horizontalLayout_31)
        self.groupBox_7 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_7.setTitle(QtGui.QApplication.translate("WizardPage", "Hardware Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_22 = QtGui.QHBoxLayout()
        self.horizontalLayout_22.setObjectName(_fromUtf8("horizontalLayout_22"))
        self.label_6 = QtGui.QLabel(self.groupBox_7)
        self.label_6.setText(QtGui.QApplication.translate("WizardPage", "Z Axis Leadscrew Pitch:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_22.addWidget(self.label_6)
        self.pitchZ = QtGui.QLabel(self.groupBox_7)
        self.pitchZ.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.pitchZ.setObjectName(_fromUtf8("pitch"))
        self.horizontalLayout_22.addWidget(self.pitchZ)
        self.label_7 = QtGui.QLabel(self.groupBox_7)
        self.label_7.setText(QtGui.QApplication.translate("WizardPage", "mm/rev", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_22.addWidget(self.label_7)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_22.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_22)
        self.horizontalLayout_23 = QtGui.QHBoxLayout()
        self.horizontalLayout_23.setObjectName(_fromUtf8("horizontalLayout_23"))
        self.label_8 = QtGui.QLabel(self.groupBox_7)
        self.label_8.setText(QtGui.QApplication.translate("WizardPage", "Z Axis Steps/rev:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_23.addWidget(self.label_8)
        self.stepsPerRevZ = QtGui.QLabel(self.groupBox_7)
        self.stepsPerRevZ.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.stepsPerRevZ.setObjectName(_fromUtf8("stepsPerRev"))
        self.horizontalLayout_23.addWidget(self.stepsPerRevZ)
        self.label_9 = QtGui.QLabel(self.groupBox_7)
        self.label_9.setText(QtGui.QApplication.translate("WizardPage", "steps", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_23.addWidget(self.label_9)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_23.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_34 = QtGui.QHBoxLayout()
        self.horizontalLayout_34.setObjectName(_fromUtf8("horizontalLayout_34"))
        self.label_53 = QtGui.QLabel(self.groupBox_7)
        self.label_53.setText(QtGui.QApplication.translate("WizardPage", "Stepping Mode:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_53.setObjectName(_fromUtf8("label_53"))
        self.horizontalLayout_34.addWidget(self.label_53)
        self.steppingMode = QtGui.QLabel(self.groupBox_7)
        self.steppingMode.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.steppingMode.setObjectName(_fromUtf8("steppingMode"))
        self.horizontalLayout_34.addWidget(self.steppingMode)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_34.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_34)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_10 = QtGui.QLabel(self.groupBox_7)
        self.label_10.setText(QtGui.QApplication.translate("WizardPage", "Layer Thickness:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_9.addWidget(self.label_10)
        self.layerThickness = QtGui.QLabel(self.groupBox_7)
        self.layerThickness.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.layerThickness.setObjectName(_fromUtf8("layerThickness"))
        self.horizontalLayout_9.addWidget(self.layerThickness)
        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setText(QtGui.QApplication.translate("WizardPage", "um", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_9.addWidget(self.label_13)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setText(QtGui.QApplication.translate("WizardPage", "Projector Resolution (pixels):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_10.addWidget(self.label_11)
        self.resolutionX = QtGui.QLabel(self.groupBox_7)
        self.resolutionX.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.resolutionX.setObjectName(_fromUtf8("resolutionX"))
        self.horizontalLayout_10.addWidget(self.resolutionX)
        self.label_12 = QtGui.QLabel(self.groupBox_7)
        self.label_12.setText(QtGui.QApplication.translate("WizardPage", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_10.addWidget(self.label_12)
        self.resolutionY = QtGui.QLabel(self.groupBox_7)
        self.resolutionY.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.resolutionY.setObjectName(_fromUtf8("resolutionY"))
        self.horizontalLayout_10.addWidget(self.resolutionY)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_14 = QtGui.QLabel(self.groupBox_7)
        self.label_14.setText(QtGui.QApplication.translate("WizardPage", "Build Area Size (mm):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.horizontalLayout_11.addWidget(self.label_14)
        self.buildAreaX = QtGui.QLabel(self.groupBox_7)
        self.buildAreaX.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.buildAreaX.setObjectName(_fromUtf8("buildAreaX"))
        self.horizontalLayout_11.addWidget(self.buildAreaX)
        self.label_15 = QtGui.QLabel(self.groupBox_7)
        self.label_15.setText(QtGui.QApplication.translate("WizardPage", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.horizontalLayout_11.addWidget(self.label_15)
        self.buildAreaY = QtGui.QLabel(self.groupBox_7)
        self.buildAreaY.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.buildAreaY.setObjectName(_fromUtf8("buildAreaY"))
        self.horizontalLayout_11.addWidget(self.buildAreaY)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.label_16 = QtGui.QLabel(self.groupBox_7)
        self.label_16.setText(QtGui.QApplication.translate("WizardPage", "Pixel Size (um):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.horizontalLayout_12.addWidget(self.label_16)
        self.pixelSizeX = QtGui.QLabel(self.groupBox_7)
        self.pixelSizeX.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.pixelSizeX.setObjectName(_fromUtf8("pixelSizeX"))
        self.horizontalLayout_12.addWidget(self.pixelSizeX)
        self.label_17 = QtGui.QLabel(self.groupBox_7)
        self.label_17.setText(QtGui.QApplication.translate("WizardPage", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.horizontalLayout_12.addWidget(self.label_17)
        self.pixelSizeY = QtGui.QLabel(self.groupBox_7)
        self.pixelSizeY.setText(QtGui.QApplication.translate("WizardPage", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.pixelSizeY.setObjectName(_fromUtf8("pixelSizeY"))
        self.horizontalLayout_12.addWidget(self.pixelSizeY)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem8)
        self.verticalLayout_2.addLayout(self.horizontalLayout_12)
        spacerItem9 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem9)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_16.addWidget(self.groupBox_7)
        self.verticalLayout_17.addLayout(self.verticalLayout_16)
        spacerItem10 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_17.addItem(spacerItem10)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        
        QtCore.QObject.connect(self.comboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ProfileChanged)
        QtCore.QObject.connect(self.toolButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.CreateNewProfile)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.controller.setText("")
        self.port.setText("")
        self.pitchZ.setText("")
        self.stepsPerRevZ.setText("")
        self.steppingMode.setText("")
        self.layerThickness.setText("")
        self.resolutionX.setText("")
        self.resolutionY.setText("")
        self.buildAreaX.setText("")
        self.buildAreaY.setText("")
        self.pixelSizeX.setText("")
        self.pixelSizeY.setText("")
    
    def CreateNewProfile(self):
        profile = hardwareProfile()
        dialog = NewHardwareProfileDialog(self, self)
        dialog.exec_()
    
    def ProfileChanged(self):
        pass

    def initializePage(self):
        pass
    
    def validatePage(self):
        self.parent.printJob.name = self.jobName.text()
        self.parent.printJob.description = self.jobDescription.text()
        self.parent.printJob.notes = self.jobNotes.toPlainText()
        return True
    
#######################GUI class and event handling#############################
class OpenAbout(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        if self.ui.workspacePre.isVisible():
            self.ModelViewPre.resize(self.ui.modelFramePre.geometry().width()-16,self.ui.modelFramePre.geometry().height()-30)
        elif self.ui.workspacePost.isVisible():
            self.ModelViewPost.resize(self.ui.modelFramePost.geometry().width()-16,self.ui.modelFramePost.geometry().height()-30)
            self.slicepreview.resize(self.ui.sliceFramePost.geometry().width(), self.ui.sliceFramePost.geometry().height())
            self.pmscaled = self.pm.scaled(self.ui.sliceFramePost.geometry().width(), self.ui.sliceFramePost.geometry().height(), QtCore.Qt.KeepAspectRatio)
            self.slicepreview.setPixmap(self.pmscaled)  

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
        self.step = ""
        self.hardwareProfileList = []
        
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
    
        ########
        self.ChangeWorkspacePreSlice()
        
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__     
        if hasattr(self, 'printer'):
            self.printer.close()      #close serial connection to printer if open
        self.renPre.GetRenderWindow().Finalize()
        self.renPost.GetRenderWindow().Finalize()
        
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.ui.consoletext.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.consoletext.setTextCursor(cursor)
        self.ui.consoletext.ensureCursorVisible()
        
    def ChangeWorkspacePreSlice(self):
        if self.ui.workspacePost.isVisible():
            response = QtGui.QMessageBox.information(self, 'Changing to Pre-slicing mode',"""By changing to pre-slicing mode you will have to re-slice later.
Would you like to continue and re-enter pre-slice mode?""", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                pass
            elif response  == QtGui.QMessageBox.No:
                self.ui.actionPreSlice.setChecked(False)
                return
        self.ui.preSliceBar.show()
        self.ui.sliceListBar.hide()
        self.ui.printJobInfoBar.hide()
        self.ui.workspacePost.hide()
        self.ui.workspacePre.show()
        
        self.ModelViewPre.show()
        self.ModelViewPre.resize(self.ui.modelFramePre.geometry().width(), self.ui.modelFramePre.geometry().height())
        
        self.ui.actionPreSlice.setChecked(True)
        self.ui.actionPostSlice.setChecked(False)
            
    def ChangeWorkspacePostSlice(self):
        if self.ui.workspacePre.isVisible():
            response = QtGui.QMessageBox.information(self, 'Changing to Post-slicing mode',"""You must first slice a model before you can view it in post-slice mode.
Would you like to slice what is currently in the pre-slice view now?""", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if response == QtGui.QMessageBox.Yes:
                self.SliceModel()
                self.EnterPostSliceMode("test")
            elif response  == QtGui.QMessageBox.No:
                self.ui.actionPostSlice.setChecked(False)
                return
            
        self.ui.preSliceBar.hide()
        self.ui.sliceListBar.show()
        self.ui.printJobInfoBar.show()
        self.ui.workspacePost.show()
        self.ui.workspacePre.hide()

        self.ModelViewPost.show()
        self.ModelViewPost.resize(self.ui.modelFramePost.geometry().width(), self.ui.modelFramePost.geometry().height())
        self.slicepreview.resize(self.ui.sliceFramePost.geometry().width(), self.ui.sliceFramePost.geometry().height())
        self.pmscaled = self.pm.scaled(self.ui.sliceFramePost.geometry().width(), self.ui.sliceFramePost.geometry().height(), QtCore.Qt.KeepAspectRatio)
        self.slicepreview.setPixmap(self.pmscaled)
          
        self.ui.actionPreSlice.setChecked(False)
        self.ui.actionPostSlice.setChecked(True)
        
    def NewPrintJob(self):
        self.printJob = _3dlpfile()
        
        wizard = QtGui.QWizard(self)
        wizard.addPage(wizardNewGeneral(wizard, self))
        wizard.addPage(wizardNewHardware(wizard, self))
        wizard.resize(640, 480)
        wizard.setWizardStyle(QtGui.QWizard.ModernStyle)
        wizard.WizardOption(QtGui.QWizard.IndependentPages)
        wizard.exec_()
    
    def SavePrintJobAs(self):
        self.outputFile = str(QFileDialog.getSaveFileName(self, "Save file", "", ".3dlp"))
        os.chdir(os.path.split(str(self.outputFile))[0]) #change to base dir of the selected filename
        self.zfile = zipfile.ZipFile(os.path.split(str(self.outputFile))[1], 'w')
        if self.step == "":
            self.SaveConfig()
        elif self.step == "pre":
            self.SaveConfig()
            self.SavePreSliceLayout()
        elif self.step == "post":
            self.SaveConfig()
            self.SavePreSliceLayout()
            self.SavePostSlice()
            
    def SavePreSliceLayout(self):
        objectTransformMatricies = []
        for object in self.modelList:
            objectTransformMatricies.append((object.transform.GetMatrix(), object.transform.GetOrientation(), object.transform.GetPosition(), object.transform.GetScale()))
            self.zfile.write(str(object.filename), arcname = os.path.split(str(object.filename))[1])
        stringio = StringIO.StringIO()
        pickle.dump(objectTransformMatricies, stringio)
        self.zfile.writestr("matricies.p", stringio.getvalue())
            
    def SavePostSlice(self):
        pass
            
    def SaveConfig(self):
        Config = ConfigParser()
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

    def SavePrintJob(self):
        pass
    
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
        self.step = "pre"
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

    def EnterPostSliceMode(self, filename):
        self.ModelViewPost.resize(self.ui.modelFramePost.geometry().width()-16,self.ui.modelFramePost.geometry().height()-30) #just in case resizeEvent() hasn't been called yet
        
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

    def OpenModel(self, filename):
        self.ModelViewPost.resize(self.ui.modelFramePost.geometry().width()-16,self.ui.modelFramePost.geometry().height()-30) #just in case resizeEvent() hasn't been called yet

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
        self.renPost.AddActor(self.modelActor)
        self.renPost.AddActor(self.slicingplaneActor)
        self.renPost.AddActor(self.slicingplaneoutlineActor)
        self.renPost.AddActor(self.outlineActor)

        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelViewPost)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        
        self.renPost.ResetCamera()  
        self.ModelViewPost.Render() #update model view
    
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
            self.renPost.Render()
            self.ModelViewPost.Render()
        
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
            self.renPost.Render()
            self.ModelViewPost.Render()
        
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
            self.renPost.Render()
            self.ModelViewPost.Render()
        
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
            self.renPost.Render()
            self.ModelViewPost.Render()
        
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
            self.renPost.Render()
            self.ModelViewPost.Render()
        
    def UpdateModelLayer(self, z):
        self.slicingplane.SetOrigin(0,0,z)
        self.cutter.Update()
        self.cutStrips.Update()
        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
        self.cutPoly.Update()
        self.cutTriangles.Update()
        self.renPost.Render()
        self.ModelViewPost.Render()
                
    def UpdateModelOpacityPre(self):
        if len(self.modelList)>0: #check to see if a model is loaded, if not it will throw an exception
            modelObject = self.modelList[self.ui.modelList.currentRow()]
            opacity, ok = QtGui.QInputDialog.getText(self, 'Set Model Opacity', 'Enter the desired opacity for %s (0-100):' %(os.path.basename(str(modelObject.filename))))
            if not ok: #the user hit the "cancel" button
                return
            modelObject.actor.GetProperty().SetOpacity(float(opacity)/100)
            self.renPre.Render()
            self.ModelViewPre.Render()
        else:
            QtGui.QMessageBox.critical(self, 'Error setting opacity',"You must load a model to change the opacity!", QtGui.QMessageBox.Ok)      
            
    def UpdateModelOpacityPost(self):
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
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
        self.renPre.Render()
        self.ModelViewPre.Render()
    
    def UpdateScale(self, scale):
        modelObject = self.modelList[self.ui.modelList.currentRow()]
        orientation = modelObject.transform.GetOrientation()
        position = modelObject.transform.GetPosition()
        
        modelObject.transform = vtk.vtkTransform()
        modelObject.transform.RotateX(orientation[0])
        modelObject.transform.RotateY(orientation[1])
        modelObject.transform.RotateZ(orientation[2])
        modelObject.transform.Translate(position[0], position[1], position[2])
        
        #now scale it to the new value and update the window
        modelObject.transform.Scale(float(scale)/100,float(scale)/100,float(scale)/100)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(modelObject.transform)
        transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
        transformFilter.Update()
        modelObject.mapper.SetInputConnection(transformFilter.GetOutputPort())
        modelObject.mapper.Update()
        modelObject.outlineMapper.Update()
        
        self.renPre.Render()
        self.ModelViewPre.Render()
        
    def ConcatenateSTLs(self):
        filename = str(QFileDialog.getSaveFileName(self, "Save STL file", "", ".stl"))
        if filename == "":
            return
        ap = vtk.vtkAppendPolyData()
        for modelObject in self.modelList:
            matrix = modelObject.transform.GetMatrix()
            
            transform  = vtk.vtkTransform()
            transform.SetMatrix(matrix)
    
            transformFilter = vtk.vtkTransformPolyDataFilter()
            transformFilter.SetTransform(transform)
            transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
            transformFilter.Update()
            ap.AddInput(transformFilter.GetOutput())
        
        writer = vtk.vtkSTLWriter()
        writer.SetInput(ap.GetOutput())
        writer.SetFileName(str(filename))
        writer.Write()
        
    def SliceModel(self):
        if len(self.modelList)>0: #check to see if a model is loaded, if not it will throw an exception
            pass
        else: #self.modelActor doesn't exist (hasn't been instantiated with a model yet)
            QtGui.QMessageBox.critical(self, 'Error slicing model',"You must first load a model to slice it!", QtGui.QMessageBox.Ok)   
            return
        outputFile = str(QFileDialog.getSaveFileName(self, "Save 3DLP project file", "", ".3dlp"))
        #concatenate all models into a single polydata dataset
        ap = vtk.vtkAppendPolyData()
        for modelObject in self.modelList:
            matrix = modelObject.transform.GetMatrix()
            transform  = vtk.vtkTransform()
            transform.SetMatrix(matrix)
            transformFilter = vtk.vtkTransformPolyDataFilter()
            transformFilter.SetTransform(transform)
            transformFilter.SetInputConnection(modelObject.reader.GetOutputPort())
            transformFilter.Update()
            ap.AddInput(transformFilter.GetOutput())
        
        writer = vtk.vtkSTLWriter()
        writer.SetInput(ap.GetOutput())
        writer.SetFileName("concat.stl")
        writer.Write()

        os.chdir(os.path.split(str(outputFile))[0])
        zfile = zipfile.ZipFile(os.path.split(str(outputFile))[1], 'w')
        #zfile.

        self.slicer = slicer.slicer(self)
        self.slicer.imageheight = 500
        self.slicer.imagewidth = 500
        # check to see if starting depth is less than ending depth!! this assumption is crucial
        self.slicer.startingdepth = 0
        self.slicer.endingdepth = 20
        self.slicer.layerincrement = 1
        self.slicer.OpenModel("wfu_cbi_skull_cleaned.stl")
        self.slicer.slice()
            
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
    
    window.resizeEvent("")
    
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    ###############
    
    
if __name__ == "__main__":
    main()
    
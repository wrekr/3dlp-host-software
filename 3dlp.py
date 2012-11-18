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
from slice import *
from time import sleep
import ctypes
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#**********************************

import os
from qtgui import Ui_MainWindow #import generated class from ui file from designer 
from slideshowgui import SlideShowWindow
from aboutdialoggui import Ui_Dialog
from progressbargui import Ui_Progress
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
#######################GUI class and event handling#############################
class OpenAbout(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
    
#*******************************************************************************
class sliceandprintmodel(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.alive = 1
        self.running = 0
    def run(self):
        self.sliceandprint(Z_options, plane, LayerThickness, ImageHeight, ImageWidth, Filename, ExposeTime, NumberOfStartLayers, StartLayersExposureTime, screennumber)   

    def sliceandprint(self, Z_options, plane, LayerThickness, ImageHeight, ImageWidth, Filename, ExposeTime, NumberOfStartLayers, StartLayersExposureTime, screennumber):
        pass
#**********************************************************************************************************************************
class slicemodel(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.alive = 1
        self.running = 0       
        
    def run(self):
        self.slice(plane, LayerThickness, ImageHeight, ImageWidth, Filename)   
           
    def slice(self, plane, LayerThickness, ImageHeight, ImageWidth, Filename):
        global progressBLAH   
        Z_options = "%s,%s,%s"%(Z_options_start, Z_options_end, Z_options_increment)
        executionpath = os.getcwd() #get current execution (working) directory
        shutil.rmtree('slices', ignore_errors = True)#clear any previous slices by removing the "slices" directory. This is re-built when freesteel slices new layers.
        print "\nslicing images..."
        
        #begin freesteel code
        options = None
        args = None
        cmdparser = None
        infile = None
        zlevels = Z_options
        outfile = "slices\layer.png"
        offset = -1.0
        radius = 1.0
        multiple = True
        tooltype = "disk"
        wres = -1.0
        wdiff = 0.0
        shell = ""
        verbose = ""
        noprogress = ""
        background = "black"
        cavity = "black"
        core = "white"
        ##
        if zlevels:
            # parse into floats
            zlist = zlevels.split(",")
            try:
                zlevels = [float(z) for z in zlist]
            except:
                print "Could not parse z levels: ", options.z
                cmdparser.print_version()
                cmdparser.print_help()
                sys.exit(0)

            if len(zlevels) == 3:
                # try to interpret as "lo, hi, step", allowing for a negative step
                lo, hi, step = zlevels[0], zlevels[1], zlevels[2]
                if ((lo < hi) == (step > 0)) and ((hi - lo) > step) and ((lo + step) > lo):
                    zlevels = [lo]
                    while (step > 0 and (zlevels[-1] + step <= hi)) or (step < 0 and (zlevels[-1] + step >= hi)):
                        zlevels.append(zlevels[-1] + step)

        scale = 1.0
        workplane = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,scale]]
        if plane == "yz":
            workplane = [[0,1,0,0],[0,0,-1,0],[-1,0,0,0],[0,0,0,scale]]
        elif plane == "xz":
            workplane = [[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,scale]]
#        if options.offset == "-radius":
#            options.offset = -options.radius
#        else:
#            options.offset = float(options.offset)

        sr = getSliceWriter(outfile, None, ImageWidth, ImageHeight, radius, offset, multiple)
        st = SlicerThread(Filename, zlevels, tooltype, radius, offset, 
                          wres, wdiff, LayerThickness, verbose, workplane=workplane, solid = not shell)
        if noprogress:
            st.printprogress = False
        else:
            st.printprogress = (outfile != "") and not sr.writestostdout
        st.start()

        while True:
            item = st.queue.get()
            if type(item) == type((0,)) and item[0] == "bbox":
                bounding_box = item[1]
                break
        units = 0.01 # used for CLI output
        sr = getSliceWriter(outfile, bounding_box, ImageWidth, ImageHeight, radius, offset, multiple)
        sr.WriteHeader(units)
        while True:
            item = st.queue.get()
            progressBLAH = st.pr
            
            if item == "end":
                break
            if item != "start":
                f, z, allpoints = item
                style="fill:%s; fill-opacity:%.1f; stroke:blue; stroke-width:1; stroke-opacity:%.1f;"
                sr.WriteLayer(units, z, allpoints, (background, cavity, core), style="")
        sr.WriteFooter()
        ###end of freesteel code
        print "\nslicing complete."

class OpenProgressBar(QtGui.QDialog, Ui_Progress):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(10)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.constantUpdate)
    
    def constantUpdate(self):
        if progressBLAH:
            self.progressbar.setValue(progressBLAH*100)
            previousval = progressBLAH
            if progressBLAH == 1:
                sleep(.5)
                self.close()
#**********************************************************************************************************************************
class printmodel(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.alive = 1
        self.running = 0
        self.timer = QtCore.QTimer()
        self.timer.start(10)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.checkIfClose)

    def run(self):
        self.printmodel(ExposeTime, NumberOfStartLayers, StartLayersExposureTime, screennumber, Printer_Baud, COM_Port)   
     
    def printmodel(self, ExposeTime, NumberOfStartLayers, StartLayersExposureTime, screennumber, Printer_Baud, COM_Port):
        self.emit(QtCore.SIGNAL('enable_stop_button')) #emit signal to enable stop button
        global pm        
        #************Start custom z scripting*******
        """
        syntax for custom z scripting; 
        
        [] - signifies a command block
        Z_xxx - move Z axis xxx number of steps
        X_xxx - move X axis xxx number of steps
        Z_UP - change direction of z axis to move up
        Z_DOWN - change direction of z axis to move down
        X_UP - change direction of x axis to move up
        X_DOWN - change direction of x axis to move down
        
        """
        #print "Custom Scripting:\n"
        commands = []
        for match in re.findall("\[(.*?)\]", zscript):
            #print match
            commands.append(match)      
        #*******************************************
        parity = {'None':'N', 'Even':'E', 'Odd':'O', 'Mark':'M', 'Space':'S'}
        stopbits = {'1':1, '1.5':1.5, '2':2}       
        databits = {'5':'5', '6':'6', '7':'7', '8':'8'}
        projector_parity_lookup = parity['%s'%projector_parity]
        projector_stopbits_lookup = stopbits['%s'%projector_stopbits]
        projector_databits_lookup = databits['%s'%projector_databits]
        projector_databits_lookup = int(projector_databits_lookup)
   
        if projectorcontrolenabled==True:
            #try connecting to projector com port
            print "Attempting to connect to projector for RS232 control..."
            try:
                projector = serial.Serial("%s"%projector_com, projector_baud, parity="%s"%projector_parity_lookup, stopbits=projector_stopbits_lookup, bytesize=projector_databits_lookup)
                print "connected to projector on %s! Engaged communications at %sbps." %(projector_com, projector_baud)
            except:
                print "FAILED."        
    
        executionpath = os.getcwd() #get current execution (working) directory
        global startingexecutionpath
        startingexecutionpath = executionpath
        #**********************************************
        if printercontrolenabled==True and arduinocontrolled==True:
            print "Connecting to printer firmware..."
            global board
            if IsArduinoUno == True:
                try:
                    board = pyfirmata.Arduino("%s"%COM_Port)
                    print "no issues opening serial connection to firmata..."
                except:
                    print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %COM_Port
                    self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
                    return
            if IsArduinoMega == True:
                try:
                    board = pyfirmata.ArduinoMega("%s"%COM_Port)
                    print "no issues opening serial connection to firmata..."
                except:
                    print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %COM_Port
                    self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
                    return

        #******************************************
        imgnum = 0 #initialize variable at 0, it is appended +1 for each file found
        #slideshow starts around here so if it's disabled kill the thread now 
        if slideshowenabled==False:
            return         #kill it now  
        concatenater = "\\"
        seq = (executionpath, "slices") #concatenate this list of strings with "str" as a separator
        slicesdir = concatenater.join(seq) #build slices path relative to working directory, separated by concatenator string
        try:
            os.chdir(slicesdir)#change to slices dir
        except:
            print "No images found in the given directory. Folder does not exist."
            print"waiting for thread to close."
            self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
            return
            #**************
        print"building file list..."    
        FileList = []
        for file in os.listdir("."): #for every file in slices dir (changed dir above)
            if file.endswith(".png"): #if it's the specified image type
                imgnum = imgnum + 1
                stringg = "\\"
                seq = (executionpath, "slices", "%s" %(file)) #concatenate this list of strings with "str" as a separator
                imagepath = stringg.join(seq) #build image path relative to working directory
                FileList.append(imagepath)
                #**************
        NumberOfImages = imgnum #number of slice images
        layers = imgnum

        print "\nNumber of Layers: ", NumberOfImages
        if slideshowenabled==True:
             #open slideshow window
             self.SlideShow = SlideShowWindow() #create instance of OtherWindow class
             self.SlideShow.show() #show slideshow window
             self.SlideShow.setupUi(self)
             screennumber = int(screennumber) #convert to integer
             screen = QtGui.QDesktopWidget().availableGeometry(screen = screennumber) #get available geometry of the screen chosen
             self.SlideShow.move(screen.left(), screen.top()) #move window to the top-left of the chosen screen
             self.SlideShow.resize(screen.width(), screen.height()) #resize the window to fit the chosen screen
             self.SlideShow.showMaximized()
             self.SlideShow.showFullScreen()
             #size = self.SlideShow.frameGeometry()
             #print size 
             #start slideshow
        if printercontrolenabled == True and arduinocontrolled == True:
            print "Enabling Stepper Motor Drivers..."
            board.digital[ZEnablePin].write(1)
            board.digital[XEnablePin].write(1)
            print "..ok."
            
        print "Printing..." 
 
        #eta = (NumberOfImages*ExposeTime) + (NumberOfImages*AdvanceTime)
        eta = 0
        percentagechunk = (100.0/float(NumberOfImages))
        ProgPercentage = 0.0
        for layer in range(NumberOfImages):
            TimeRemaining = GetInHMS(eta)
            if layer >= NumberOfStartLayers:
                ExposureTime = ExposeTime
            else:
                ExposureTime = StartLayersExposureTime
            if slideshowenabled:
                blankpath = "%s\\10x10black.png" %(startingexecutionpath)
                pm = QtGui.QPixmap(blankpath)
                pmscaled = pm.scaled(screen.width(), screen.height(), QtCore.Qt.KeepAspectRatio)
                self.SlideShow.label.setPixmap(pmscaled) #set black pixmap for blank slide     
                QCoreApplication.processEvents() #have to call this so the GUI updates before the sleep function
            self.emit(QtCore.SIGNAL('updatePreviewBlank')) #emit signal to update preview image
            #**send command to stage
            
            if printercontrolenabled==True and arduinocontrolled==True: #custom scripted sequence::
                print "sending custom scripted command sequence..."
                for command in commands:
                    if command == "Z_UP":
                        board.digital[ZDirPin].write(1)
                    elif command == "Z_DOWN":
                        board.digital[ZDirPin].write(0)
                    elif command == "X_UP":
                        board.digital[XDirPin].write(1)
                    elif command == "X_DOWN":
                        board.digital[XDirPin].write(0)
                    #make sure the next two cases are last to avoid false positives
                    elif command.startsWith("Z"):
                        amount = command[2:command.size()]
                        numsteps = int(amount)
                        for step in range(numsteps):                       
                            board.digital[ZStepPin].write(1)
                            sleep(.001)
                            board.digital[ZStepPin].write(0)
                    elif command.startsWith("X"):
                        amount = command[2:command.size()]
                        numsteps = int(amount)
                        for step in range(numsteps):
                            board.digital[XStepPin].write(1)
                            sleep(.001)
                            board.digital[XStepPin].write(0)
                    
            #sleep(AdvanceTime)
            #eta = eta - AdvanceTime
            print "Now printing layer %d out of %d. Progress: %r%% Time Remaining: %s" %(layer+1, layers, ProgPercentage, TimeRemaining)
            layer = layer - 0
            pm = QtGui.QPixmap(FileList[layer])
            if slideshowenabled:
                pmscaled = pm.scaled(screen.width(), screen.height(), QtCore.Qt.KeepAspectRatio)
                self.SlideShow.label.setPixmap(pmscaled)
                QCoreApplication.processEvents()
            
            self.emit(QtCore.SIGNAL('updatePreview')) #emit signal to update preview image
            sleep(ExposureTime)
            eta = eta - ExposureTime
            ProgPercentage = ProgPercentage + percentagechunk         

        print "\nPrint job completed successfully. %d layers were built." %layers
        if printercontrolenabled==True and arduinocontrolled==True:
            board.exit() #close firmata connection 
        if projectorcontrolenabled:
            print "Sending power off command to projector."
#**********************************************************************************************************************************
# Create a class for our main window
class Main(QtGui.QMainWindow):
    def resizeEvent(self,Event):
        print "window has been resized:", Event
        print Event.size().height()
        #self.ModelView.setFixedSize(651,501)
        print self.ui.ModelFrame.frameGeometry()
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)  
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "3DLP Host", None, QtGui.QApplication.UnicodeUTF8))
        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #####################
        self.filename = "testpart.stl"
    
        
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(str(self.filename))
         
        self.polyDataOutput = self.reader.GetOutput()       
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
         
        #create model actor
        self.modelActor = vtk.vtkActor()
        self.modelActor.GetProperty().SetColor(1,1,1)
        self.modelActor.GetProperty().SetOpacity(0.4)
        self.modelActor.SetMapper(self.mapper)
        
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        self.slicingplane=vtk.vtkPlane()
        self.slicingplane.SetOrigin(0,0,37)
        self.slicingplane.SetNormal(0,0,1)
        
        #create cutter
        self.cutter=vtk.vtkCutter()
        self.cutter.SetCutFunction(self.slicingplane)
        self.cutter.SetInputConnection(self.reader.GetOutputPort())
        self.cutter.Update()
        self.cutterMapper=vtk.vtkPolyDataMapper()
        self.cutterMapper.SetInputConnection(self.cutter.GetOutputPort())
        
        #create plane actor
        self.slicingplaneActor=vtk.vtkActor()
        self.slicingplaneActor.GetProperty().SetColor(1.0,0,0)
        self.slicingplaneActor.GetProperty().SetLineWidth(4)
        self.slicingplaneActor.SetMapper(self.cutterMapper)
 
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

        self.ren = vtk.vtkRenderer()
        self.ren.AddActor(self.modelActor)
        self.ren.AddActor(self.slicingplaneActor)
        self.ren.AddActor(self.outlineActor)
        self.ren.SetBackground(0,0,0)
        
        # create the modelview widget
        self.ModelView = QVTKRenderWindowInteractor(self.ui.ModelFrame)
        self.ModelView.SetInteractorStyle(MyInteractorStyle())
        self.ModelView.setFixedSize(651,501)
        self.ModelView.Initialize()
        
        self.renWin=self.ModelView.GetRenderWindow()
        self.renWin.AddRenderer(self.ren)

        #create orientation markers
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.ModelView)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        self.ren.ResetCamera()        

        self.ModelView.Start()  

        #####################
#        # create the sliceview widget
        self.ModelView = QVTKRenderWindowInteractor(self.ui.SliceFrame)
        self.ModelView.SetInteractorStyle(MyInteractorStyle())
        self.ModelView.setFixedSize(271,171)
        self.ModelView.Initialize()
        self.ModelView.Start()
#        
#        self.filename = "ball.stl"     
#        self.reader = vtk.vtkSTLReader()
#        self.reader.SetFileName(self.filename)
#         
#        self.polyDataOutput = self.reader.GetOutput()       
#        
#        self.mapper = vtk.vtkPolyDataMapper()
#        self.mapper.SetInputConnection(self.reader.GetOutputPort())
#         
#        self.actor = vtk.vtkActor()
#        self.actor.SetMapper(self.mapper)
#        
#        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
#        self.plane = vtk.vtkPlane()
#        self.plane.SetOrigin(20, 0, 0)
#        self.plane.SetNormal(0, 0, 1)
#
#        #create cutter
#        self.cutter = vtk.vtkCutter()
#        self.cutter.SetCutFunction(self.plane)
#        self.cutter.SetInputConnection(self.reader.GetOutputPort())
#        self.cutter.Update()
#
#        FeatureEdges = vtk.vtkFeatureEdges()
#        FeatureEdges.SetInputConnection(self.cutter.GetOutputPort())
#        FeatureEdges.BoundaryEdgesOn()
#        FeatureEdges.FeatureEdgesOff()
#        FeatureEdges.NonManifoldEdgesOff()
#        FeatureEdges.ManifoldEdgesOff()
#        FeatureEdges.Update()
#         
#        self.cutStrips = vtk.vtkStripper() ; #Forms loops (closed polylines) from cutter
#        self.cutStrips.SetInputConnection(self.cutter.GetOutputPort())
#        self.cutStrips.Update()
#        self.cutPoly = vtk.vtkPolyData() ; #This trick defines polygons as polyline loop
#        self.cutPoly.SetPoints((self.cutStrips.GetOutput()).GetPoints())
#        self.cutPoly.SetPolys((self.cutStrips.GetOutput()).GetLines())
#         
#        self.cutMapper = vtk.vtkPolyDataMapper()
#        #self.cutMapper.SetInput(FeatureEdges.GetOutput())
#        if vtk.VTK_MAJOR_VERSION <= 5:
#            self.cutMapper.SetInput(self.cutPoly)
#        else:
#            self.cutMapper.SetInputData(self.cutPoly)
#         
#        self.cutActor = vtk.vtkActor()
#        self.cutActor.GetProperty().SetColor(1, 1, 0)
#        self.cutActor.GetProperty().SetEdgeColor(0, 1, 0)
#         
#        self.cutActor.GetProperty().SetLineWidth(2)
#        self.cutActor.GetProperty().EdgeVisibilityOn()
#        ##self.cutActor.GetProperty().SetOpacity(0.7)
#        self.cutActor.SetMapper(self.cutMapper)
#
#        self.ren = vtk.vtkRenderer()
#        self.ren.SetBackground(0,0,0)
#        self.ren.AddActor(self.cutActor)
#        self.renWin=self.ModelView.GetRenderWindow()
#        self.renWin.AddRenderer(self.ren)
        #######################        
        
        
        screencount = QtGui.QDesktopWidget().numScreens()
        print "number of monitors: ", screencount
         ####setup screen picker####
        for x in range(screencount):
            self.ui.pickscreen.addItem("")
            self.ui.pickscreen.setItemText(x, QtGui.QApplication.translate("MainWindow", "%d"%x, None, QtGui.QApplication.UnicodeUTF8))
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
                self.ui.pickcom.addItem(portname)
                self.ui.pickcom.setItemText(x, QtGui.QApplication.translate("MainWindow", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
                self.ui.projector_pickcom.addItem(portname)
                self.ui.projector_pickcom.setItemText(x, QtGui.QApplication.translate("MainWindow", "%s"%portname, None, QtGui.QApplication.UnicodeUTF8))
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
        
        self.ui.zscript.setPlainText(parser.get('scripting', 'sequence'))
        self.ui.projector_poweroffcommand.setText(parser.get('program_defaults', 'PowerOffCommand'))
        bauddict = {'115200':0, '57600':1, '38400':2, '19200':3, '9600':4, '4800':5, '2400':6}
        self.ui.printerbaud.setCurrentIndex(bauddict[parser.get('program_defaults', 'Printer_Baud')])
        self.ui.exposure_time.setText(parser.get('program_defaults', 'ExposeTime'))
        self.ui.starting_layers.setText(parser.get('program_defaults', 'NumStartLayers'))
        self.ui.starting_layer_exposure.setText(parser.get('program_defaults', 'StartLayersExposeTime'))
        self.ui.image_height.setText(parser.get('program_defaults', 'ImageHeight'))
        self.ui.image_width.setText(parser.get('program_defaults', 'ImageWidth'))
        self.ui.layer_thickness.setText(parser.get('program_defaults', 'LayerThickness'))
        self.ui.z_options_start.setText(parser.get('program_defaults', 'z_options_start'))
        self.ui.z_options_end.setText(parser.get('program_defaults', 'z_options_end'))
        self.ui.z_options_increment.setText(parser.get('program_defaults', 'z_options_increment'))
        planedict = {'XZ':0, 'XY':1, 'YZ':2}
        self.ui.slicing_plane.setCurrentIndex(planedict[parser.get('program_defaults', 'plane')])
        
        if parser.get('program_defaults', 'printercontroller') == 'ARDUINO':
            self.ui.radio_arduino.click()
        elif parser.get('program_defaults', 'printercontroller') == 'PYMCU':
            self.ui.radio_pymcu.click()
        if parser.get('program_defaults', 'arduinotype') == 'UNO':
            self.ui.radio_uno.click()
        elif parser.get('program_defaults', 'arduinotype') == 'MEGA':
            self.ui.radio_mega.click()
        if parser.get('program_defaults', 'slideshowenabled') == 'True':
            self.ui.enableslideshow.click()
        if parser.get('program_defaults', 'printercontrol') == 'True':
            self.ui.enableprintercontrol.click()
        if parser.get('program_defaults', 'projectorcontrol') == 'True':
            self.ui.projectorcontrol.click()
        
        #*********************************
        if self.ui.radio_pymcu.isChecked(): #if pymcu is selected on startup that means projector comms are handled through it. disable printer com config stuff. 
            self.ui.projector_pickcom.setEnabled(False)
            self.ui.projector_baud.setEnabled(False)
            self.ui.projector_parity.setEnabled(False)
            self.ui.projector_databits.setEnabled(False)
            self.ui.projector_stopbits.setEnabled(False)
            self.ui.zscript.setEnabled(False)
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
            
    def applyprintingsettings(self):
        print "applying printing settings"
        COM_Port = self.ui.pickcom.currentText()
        Printer_Baud = int(self.ui.printerbaud.currentText())
        ExposeTime = float(self.ui.exposure_time.text())
        #AdvanceTime = float(self.ui.advance_time.text())
        Port = self.ui.remote_port.text()
        NumberOfStartLayers = float(self.ui.starting_layers.text())
        StartLayersExposureTime = float(self.ui.starting_layer_exposure.text())
    
    def applyslicingsettings(self):
        print "applying slicing settings"
        
        LayerThickness = self.ui.layer_thickness.text()
        Z_options = self.ui.z_options.text()
        ImageWidth = self.ui.image_width.text()
        ImageHeight = self.ui.image_height.text()
        plane= self.ui.slicing_plane.currentText()
        
    def projectorcontroltoggle(self):
        if self.ui.projectorcontrol.isChecked():
            self.ui.projector_pickcom.setEnabled(True)
            self.ui.projector_baud.setEnabled(True)
            self.ui.projector_parity.setEnabled(True)
            self.ui.projector_databits.setEnabled(True)
            self.ui.projector_stopbits.setEnabled(True)
            self.ui.projector_poweroffcommand.setEnabled(True)
            self.ui.projector_testpoweroffcommand.setEnabled(True)
            self.ui.projector_applysettings.setEnabled(True)
            if self.ui.radio_pymcu.isChecked(): #whoa there, if pymcu is selected you can't enable the control settings...
                self.ui.projector_pickcom.setEnabled(False)
                self.ui.projector_baud.setEnabled(False)
                self.ui.projector_parity.setEnabled(False)
                self.ui.projector_databits.setEnabled(False)
                self.ui.projector_stopbits.setEnabled(False)   
               
        else:
            self.ui.projector_pickcom.setEnabled(False)
            self.ui.projector_baud.setEnabled(False)
            self.ui.projector_parity.setEnabled(False)
            self.ui.projector_databits.setEnabled(False)
            self.ui.projector_stopbits.setEnabled(False)
            self.ui.projector_poweroffcommand.setEnabled(False)
            self.ui.projector_testpoweroffcommand.setEnabled(False)
            self.ui.projector_applysettings.setEnabled(False)
            
    def printercontroltoggle(self):
        if self.ui.radio_pymcu.isChecked():
            self.ui.projector_pickcom.setEnabled(False)
            #self.ui.projector_baud.setEnabled(False)
            self.ui.projector_parity.setEnabled(False)
            self.ui.projector_databits.setEnabled(False)
            self.ui.projector_stopbits.setEnabled(False)
            self.ui.zscript.setEnabled(False)
        else:
            if self.ui.projectorcontrol.isChecked(): #only if projector control is enabled can you re-enable all the control settings.
                self.ui.projector_pickcom.setEnabled(True)
                self.ui.projector_baud.setEnabled(True)
                self.ui.projector_parity.setEnabled(True)
                self.ui.projector_databits.setEnabled(True)
                self.ui.projector_stopbits.setEnabled(True)
                self.ui.zscript.setEnabled(True)
                
    def slideshowcontroltoggled(self):
        global slideshowenabled
        if self.ui.enableslideshow.isChecked():
            self.ui.pickscreen.setEnabled(True)
            slideshowenabled = True
        else:
            self.ui.pickscreen.setEnabled(False)
            slideshowenabled = False

    def enableprintercontroltoggled(self):
        if self.ui.enableprintercontrol.isChecked():
            self.ui.pickcom.setEnabled(True)
            self.ui.printerbaud.setEnabled(True)
            self.ui.radio_pymcu.setEnabled(True)
            self.ui.radio_arduino.setEnabled(True)
            self.ui.projectorcontrol.setChecked(True)
            printercontrolenabled = True
        else:
            self.ui.pickcom.setEnabled(False)
            self.ui.printerbaud.setEnabled(False)
            self.ui.radio_pymcu.setEnabled(False)
            self.ui.radio_arduino.setEnabled(False)
            self.ui.projectorcontrol.setChecked(False)
            printercontrolenabled = False
    
    def stopthread(self):
        global IsStopped
        IsStopped = True
 
    def selectfile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()
        self.ui.displayfilenamelabel.setText(self.filename)


        
    def loadimage(self):

        ImageFilename = QtGui.QFileDialog.getOpenFileName()
        pm = QtGui.QPixmap(ImageFilename)
        pmscaled = pm.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.ui.imagepreview.setPixmap(pmscaled)
    
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
        
    def sliceandprintpressed(self):
        #combine slice and print classes here
        pass

    def slicepressed(self):
        print "applying slicing settings"
        global Z_options_start, Z_options_end, Z_options_increment
        global plane
        global LayerThickness
        global ImageHeight
        global ImageWidth
        global Filename
        Filename = self.ui.displayfilenamelabel.text()
        LayerThickness = float(self.ui.layer_thickness.text())
        Z_options_start = self.ui.z_options_start.text()
        Z_options_end = self.ui.z_options_end.text()
        Z_options_increment = self.ui.z_options_increment.text()
        ImageWidth = float(self.ui.image_width.text())
        ImageHeight = float(self.ui.image_height.text())
        plane= self.ui.slicing_plane.currentText()
        self.thread = slicemodel()
        self.thread.start()
        sleep(1)
        progress = OpenProgressBar(self)
        progress.exec_()
               
    def printpressed(self):
        print "applying printing settings"
        global ExposeTime
        global AdvanceTime
        global NumberOfStartLayers
        global StartLayersExposureTime
        global COM_Port
        global Printer_Baud
        global screennumber
        global printercontrol
        global poweroffcommand
        global projectorcontrolenabled
        global printercontrolenabled
        global pymcucontrolled
        global arduinocontrolled
        global slideshowenabled
        global zscript
        global projector_com, projector_parity, projector_baud, projector_databits, projector_stopbits
        global IsStopped
        global IsArduinoUno
        global IsArduinoMega
        IsStopped = False
        COM_Port = self.ui.pickcom.currentText()
        Printer_Baud = int(self.ui.printerbaud.currentText())
        ExposeTime = float(self.ui.exposure_time.text())
        #AdvanceTime = float(self.ui.advance_time.text())
        Port = self.ui.remote_port.text()
        NumberOfStartLayers = float(self.ui.starting_layers.text())
        StartLayersExposureTime = float(self.ui.starting_layer_exposure.text())
        projector_com = self.ui.projector_pickcom.currentText()
        projector_baud = self.ui.projector_baud.currentText()
        projector_parity = self.ui.projector_parity.currentText()
        projector_stopbits = self.ui.projector_stopbits.currentText()
        projector_databits = self.ui.projector_databits.currentText()
        zscriptdoc = self.ui.zscript.document()
        zscript = zscriptdoc.toPlainText()
        if self.ui.projectorcontrol.isChecked():
            projectorcontrolenabled = True
        else:
            projectorcontrolenabled = False
        if self.ui.enableprintercontrol.isChecked():
            printercontrolenabled = True
           
        else:
            printercontrolenabled = False
            print "printercontrolenabled set to false"
        if self.ui.enableslideshow.isChecked():
            slideshowenabled = True
        if self.ui.radio_pymcu.isChecked():
            pymcucontrolled = True
            arduinocontrolled = False
        if self.ui.radio_arduino.isChecked():
            arduinocontrolled = True
            pymcucontrolled = False
        screennumber = self.ui.pickscreen.currentText() #get the screen number from picker
        if self.ui.radio_uno.isChecked():
            IsArduinoUno = True
            IsArduinoMega = False
        if self.ui.radio_mega.isChecked():
            IsArduinoMega = True
            IsArduinoUno = False
       
        self.thread = printmodel()
        #connect to slideshow signal
        self.connect(self.thread
                     ,QtCore.SIGNAL('updatePreview')
                     ,self.updatepreview)      
        self.connect(self.thread
                     ,QtCore.SIGNAL('updatePreviewBlank')
                     ,self.updatepreviewblank)      
        self.connect(self.thread
                     ,QtCore.SIGNAL('disable_stop_button')
                     ,self.disablestopbutton) 
        self.connect(self.thread
                     ,QtCore.SIGNAL('enable_stop_button')
                     ,self.enablestopbutton)     
        self.thread.start()

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
    
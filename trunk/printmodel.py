# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 17:06:39 2012

@author: Chris
"""

from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
import re, os, hardware

class printmodel(QtCore.QThread):
    def __init__(self, zscript, COM_Port, Printer_Baud, ExposeTime, NumberOfStartLayers, StartLayersExposureTime
                , projectorcontrolenabled, controller, slideshowenabled):
        print "HEY"
        self.zscript = zscript
        self.COM_Port = COM_Port
        self.Printer_Baud = Printer_Baud
        self.ExposeTime = ExposeTime
        self.NumberOfStartLayers = NumberOfStartLayers
        self.StartLayersExposureTime = StartLayersExposureTime
        self.projectorcontrolenabled = projectorcontrolenabled
        self.slideshowenabled = slideshowenabled
        self.controller = controller
        QtCore.QThread.__init__(self, parent = None)
        self.printmodel() #start the printmodel method below
     
    def printmodel(self):
        print "RUNNING"
        self.emit(QtCore.SIGNAL('enable_stop_button')) #emit signal to enable stop button
    
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
        commands = []
        for match in re.findall("\[(.*?)\]", self.zscript):
            print match
            commands.append(match)      
        #*******************************************

        if self.projectorcontrolenabled==True:
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
        if self.controller=="ramps":
            print "Connecting to RAMPS board..."
            self.printer = hardware.ramps(self.COM_Port)
            
        if self.controller=="arduinoUNO":
            print "Connecting to printer firmware..."
            try:
                self.board = pyfirmata.Arduino("%s"%self.COM_Port)
                print "no issues opening serial connection to firmata..."
            except:
                print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %self.COM_Port
                self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
                return
                
        if self.controller=="arduinoMEGA":
            try:
                self.board = pyfirmata.ArduinoMega("%s"%self.COM_Port)
                print "no issues opening serial connection to firmata..."
            except:
                print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %self.COM_Port
                self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
                return

        #******************************************
        imgnum = 0 #initialize variable at 0, it is appended +1 for each file found
        #slideshow starts around here so if it's disabled kill the thread now 
        if self.slideshowenabled==False:
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
        if self.slideshowenabled==True:
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
                self.pm = QtGui.QPixmap(blankpath)
                pmscaled = self.pm.scaled(screen.width(), screen.height(), QtCore.Qt.KeepAspectRatio)
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
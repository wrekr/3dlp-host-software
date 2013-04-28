# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 17:06:39 2012

@author: Chris
"""

from PyQt4 import QtCore,QtGui
from PyQt4.Qt import *
import re, os, hardware
from slideshowgui import SlideShowWindow
from time import sleep


class printmodel(QtCore.QThread):
    def __init__(self, zscript, COM_Port, Printer_Baud, ExposeTime, NumberOfStartLayers, StartLayersExposureTime
                , projectorcontrolenabled, controller, screennumber, cwd, parent):
        self.zscript = zscript
        self.COM_Port = COM_Port
        self.Printer_Baud = Printer_Baud
        self.ExposeTime = float(ExposeTime)
        self.screennumber = screennumber
        self.NumberOfStartLayers = NumberOfStartLayers
        self.StartLayersExposureTime = StartLayersExposureTime
        self.projectorcontrolenabled = projectorcontrolenabled
        self.controller = controller
        self.stop = False
        self.cwd = cwd
        self.printer = parent.printer
        super(printmodel, self).__init__(parent)
        #QtCore.QThread.__init__(self, parent = None)
        #self.printmodel() #start the printmodel method below
     
    def run(self):
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
        PAUSE_xxxx - pause xxxx number of milliseconds in scripting sequence
        Z_ENABLE
        Z_DISABLE
        X_ENABLE
        X_DISABLE
        
        """
        self.commands = []
        for match in re.findall("\[(.*?)\]", self.zscript):
            print match
            self.commands.append(match)      
        #*******************************************
    
        self.startingexecutionpath = self.cwd
        #**********************************************

#        if self.controller=="ramps":
#            print "Connecting to RAMPS board..."
#            self.printer = hardware.ramps(self.COM_Port)
            
#        if self.controller=="arduinoUNO":
#            print "Connecting to printer firmware..."
#            try:
#                self.board = hardware.arduinoUno(self.COM_Port)
#                print "no issues opening serial connection to firmata..."
#            except:
#                print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %self.COM_Port
#                self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
#                return
#                
#        if self.controller=="arduinoMEGA":
#            try:
#                self.board = hardware.arduinoMega(self.COM_Port)
#                print "no issues opening serial connection to firmata..."
#            except:
#                print"Failed to connect to firmata on %s. Check connections and settings, restart the program, and try again." %self.COM_Port
#                self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
#                return

        #******************************************
        imgnum = 0 #initialize variable at 0, it is appended +1 for each file found

        concatenater = "\\"
        seq = (self.cwd, "slices") #concatenate this list of strings with "str" as a separator
        slicesdir = concatenater.join(seq) #build slices path relative to working directory, separated by concatenator string
        try:
            os.chdir(slicesdir)#change to slices dir
            print slicesdir
        except:
            print "Slices folder does not exist."
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
                seq = (self.cwd, "slices", "%s" %(file)) #concatenate this list of strings with "str" as a separator
                imagepath = stringg.join(seq) #build image path relative to working directory
                FileList.append(imagepath)
                #**************
        NumberOfImages = imgnum #number of slice images
        layers = imgnum

        print "\nNumber of Layers: ", NumberOfImages

        #open slideshow window
        self.SlideShow = SlideShowWindow() #create instance of OtherWindow class
        self.SlideShow.show() #show slideshow window
        self.SlideShow.setupUi(self)
        screen = QtGui.QDesktopWidget().availableGeometry(screen = int(self.screennumber)) #get available geometry of the screen chosen
        self.SlideShow.move(screen.left(), screen.top()) #move window to the top-left of the chosen screen
        self.SlideShow.resize(screen.width(), screen.height()) #resize the window to fit the chosen screen
        self.SlideShow.showMaximized()
        self.SlideShow.showFullScreen()
        #size = self.SlideShow.frameGeometry()
        #print size 
        #start slideshow

        #print "Enabling Stepper Motor Drivers..."
        #self.printer.EnableZ()
        #self.printer.EnableX()
        #print "..ok."
            
        print "Printing..." 
 
        #eta = (NumberOfImages*ExposeTime) + (NumberOfImages*AdvanceTime) + custom commands!!!!
        eta = 0
        percentagechunk = 100.0/float(NumberOfImages)
        ProgPercentage = 0.0
        for layer in range(NumberOfImages):
            if self.stop == True:
                print "Exiting print cycle now."
                self.emit(QtCore.SIGNAL('disable_stop_button')) #emit signal to disable stop button
                #self.printer.close() #close connection with printer
                return
            TimeRemaining = GetInHMS(eta)
            if layer >= self.NumberOfStartLayers:
                ExposureTime = float(self.ExposeTime)
            else:
                ExposureTime = self.StartLayersExposureTime

            blankpath = "%s\\10x10black.png" %(self.startingexecutionpath)
            self.pm = QtGui.QPixmap(blankpath)
            #insert code to move printer to starting point
            ###
            pmscaled = self.pm.scaled(screen.width(), screen.height(), QtCore.Qt.KeepAspectRatio)
            self.SlideShow.label.setPixmap(pmscaled) #set black pixmap for blank slide     
            QCoreApplication.processEvents() #have to call this so the GUI updates before the sleep function
            self.emit(QtCore.SIGNAL('updatePreviewBlank')) #emit signal to update preview image
            #**send command to stage
             
            print "sending custom scripted command sequence..."
            for command in self.commands:
                if command == "Z_UP":
                    #board.digital[ZDirPin].write(1)
                    self.printer.Z_Up()
                elif command == "Z_DOWN":
                    #board.digital[ZDirPin].write(0)
                    self.printer.Z_Down()
                elif command == "X_UP":
                    #board.digital[XDirPin].write(1)
                    self.printer.Z_Up()
                elif command == "X_DOWN":
                    #board.digital[XDirPin].write(0)
                    self.printer.X_Down()
                #make sure the next two cases are last to avoid false positives
                elif command.startswith("Z"):
                    numsteps = int(command[2:command.__len__()])
                    print "Incrementing Z axis %d steps" %numsteps
                    self.printer.IncrementZ(numsteps)

                elif command.startswith("X"):
                    numsteps = int(command[2:command.__len__()])
                    print "Incrementing X axis %d steps"%numsteps
                    self.printer.IncrementX(numsteps)
                    
                elif command.startswith("PAUSE"):
                    delayval = int(command[6:command.__len__()])
                    print "Pausing %d milliseconds"%delayval
                    sleep(float(delayval)/1000.00)
                    
            #sleep(AdvanceTime)
            #eta = eta - AdvanceTime
            #print "Now printing layer %d out of %d. Progress: %r%% Time Remaining: %s" %(layer+1, layers, ProgPercentage, TimeRemaining)
            layer = layer - 0
            pm = QtGui.QPixmap(FileList[layer])

            pmscaled = pm.scaled(screen.width(), screen.height(), QtCore.Qt.KeepAspectRatio)
            self.SlideShow.label.setPixmap(pmscaled)
            QCoreApplication.processEvents()
            
            self.emit(QtCore.SIGNAL('updatePreview')) #emit signal to update preview image
            sleep(float(ExposureTime))
            eta = eta - float(ExposureTime)
            ProgPercentage = ProgPercentage + percentagechunk         

        print "\nPrint job completed successfully. %d layers were built." %layers
        #if printercontrolenabled==True and arduinocontrolled==True:
        #   board.exit() #close firmata connection 

            
def GetInHMS(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    #print "%d:%02d:%02d" % (h, m, s)
    return "%d:%02d:%02d" % (h, m, s)
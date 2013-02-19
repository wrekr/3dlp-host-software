# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 21:01:39 2012

@author: Chris
"""
import serial

class arduino_uno():
    def __init__(self):
        print "initialized"
    
class arduino_mega():
    def __init__(self):
        print "initialized"  

class ramps():
    def __init__(self, port):
        try:
            self.board = serial.Serial("%s"%port, 115200)
            print "initialized connection successfully"
            print self.board.readline()
        except:
            print "Could not connect to RAMPS board."
    
    def EnableZ(self):
        print "Z Enabled."
        
    def Z_Up(self):
        print "set Z to UP"
    
    def Z_Down(self):
        print "Set Z to DOWN"
        
    def X_Up(self):
        print "Set X to UP"
        
    def X_Down(self):
        print "set X to DOWN"
        
    def IncrementZ(self, steps):
        #check to make sure the step value is a whole number
        if steps % 1 == 0:
            pass
        else:
            print "ERROR! Steps value must be an integer!"
            return
        #check if it's negative and take appropriate action
        if steps < 0:
            self.Z_Down()
        elif steps > 0:
            self.Z_Up()
        #send command
        print "sending G%d" %steps
        self.board.write('G%d'%steps)
        #look for response
        if self.board.readline() == "OK":
            print "success"
        else:
            print "FAILED"
    
    def IncrementX(self, steps):
        pass
    
    def HomeZ(self):
        pass
    
    def HomeX(self):
        pass
    
class pymcu():
    def __init__(self):
        print "initialized"
    
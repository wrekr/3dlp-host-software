# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 21:01:39 2012

@author: Chris
"""
import serial
import math

class arduinoUno():
    def __init__(self):
        print "initialized"
    
class arduinoMega():
    def __init__(self):
        print "initialized"  

class ramps():
    def __init__(self, port):
        try:
            self.board = serial.Serial("%s"%port, 115200)
            print "initialized connection successfully"
            self.status = 0
            print self.board.readline()
        except:
            print "Could not connect to RAMPS board."
            self.status = 1
    
    def EnableZ(self):
        print "Z Enabled."
        
    def HomePrinter(self):
        pass
        
    def Z_Up(self):
        self.board.write("Z_UP\n")
        print "set Z to UP"
    
    def Z_Down(self):
        self.board.write("Z_DOWN\n")
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
        print steps
        if steps < 0:
            self.Z_Down()
        elif steps > 0:
            self.Z_Up()
        #send command
        print "sending ZMOVE_%d" %math.fabs(steps)
        self.board.write('ZMOVE_%d\n'%math.fabs(steps))
        print self.board.readline()
        #look for response
        #print ".", self.board.readline(), "."
#        if self.board.readline() == "OK\n":
#            print "success"
#        else:
#            print "FAILED"

    def IncrementX(self, steps):
        pass
    
    def HomeZ(self):
        pass
    
    def HomeX(self):
        pass
    
    def close(self):
        self.board.close()
    
class pymcu():
    def __init__(self):
        print "initialized"
    
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 21:01:39 2012

@author: Chris Marion
"""
import serial
import math
import time
from threading import Thread

class Heartbeat(Thread):
    def __init__(self, parent):
        self.stopped = False
        self.parent = parent
        Thread.__init__(self)
        
    def run(self):
        while not self.stopped:
            time.sleep(1.0)
            self.ping()
            
    def ping(self):
        self.parent.board.write("?\n")
        response = str(self.parent.board.readline())
        if response.strip() == ".":
            print "OK"
        else:
            pass

class arduinoUno():
    def __init__(self):
        print "initialized"
    
class arduinoMega():
    def __init__(self):
        print "initialized"  

class ramps():
    def __init__(self, port):
        try:
            self.heartbeat = Heartbeat(self)
            #print "trying board"
            self.board = serial.Serial("%s"%port, 115200, timeout = 5)
            print "Initialized serial connection successfully"
            self.status = 0
            self.board.readline()
            self.identify()
            #time.sleep(5)
            #self.heartbeat.start()
        except:
            print "Could not connect to RAMPS board."
            self.status = 1
            
    def identify(self):
        self.board.write("IDN\n")
        print str(self.board.readline()).strip()

    def EnableZ(self):
        self.board.write("Z_ENABLE\n")
        if str(self.board.readline()).strip() == "OK":
            print "done"
        
    def HomePrinter(self):
        pass
        
    def Z_Up(self):
        self.board.write("Z_UP\n")
        print str(self.board.readline()).strip()
    
    def Z_Down(self):
        self.board.write("Z_DOWN\n")
        print str(self.board.readline()).strip()
        
    def IncrementZ(self, steps):
        #check to make sure the step value is a whole number
#        if steps % 1 == 0:
#            pass
#        else:
#            print "ERROR! Steps value must be an integer!"
#            return
        #check if it's negative and take appropriate action
        if steps < 0:
            self.Z_Down()
        elif steps > 0:
            self.Z_Up()
        #send command
        print "sending ZMOVE_%d" %math.fabs(steps)
        self.board.write('ZMOVE_%d\n'%math.fabs(steps))
        if str(self.board.readline()).strip() == "OK":
            print "success"

    def HomeZ(self):
        pass
    
    def HomeX(self):
        pass
    
    def close(self):
        self.board.close()
        self.heartbeat.join()
    
class pymcu():
    def __init__(self):
        print "initialized"
    
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 21:01:39 2012

@author: Chris
"""
import serial

class arduino_uno():
    def __init__(self):
        print "initialized"
    
    def connect(self):
        pass
    
    def send(self):
        pass
    
class arduino_mega():
    def __init__(self):
        print "initialized"
    
    def connect(self):
        pass
    
    def send(self):
        pass
    
class ramps():
    def __init__(self, port):
        try:
            self.board = serial.Serial("%s"%port, 115200)
            print "initialized connection successfully"
            print self.board.readline()
        except:
            print "Could not connect to RAMPS board."
    
    def send(self):
        pass
    
class pymcu():
    def __init__(self):
        print "initialized"
    
    def connect(self):
        pass
        
    def send(self):
        pass
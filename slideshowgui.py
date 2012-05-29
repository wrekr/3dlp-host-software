# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 13:35:14 2012

@author: Chris Marion - www.chrismarion.net
"""
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
#class for slideshow window
class SlideShowWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
    
    def setupUi(self, QMainWindow):        
        layout = QHBoxLayout()
        self.label = QLabel()
        self.label.setText("Image Preview")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        self.setWindowTitle("Slideshow")
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        self.setPalette(palette)
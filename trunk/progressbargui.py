# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progressbar.ui'
#
# Created: Tue May 01 19:10:56 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Progress(object):
    def setupUi(self, Progress):
        Progress.setObjectName(_fromUtf8("Progress"))
        Progress.resize(490, 39)
        Progress.setWindowTitle(QtGui.QApplication.translate("Progress", "Slicing...", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(Progress)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressbar = QtGui.QProgressBar(Progress)
        self.progressbar.setProperty("value", 0)
        self.progressbar.setObjectName(_fromUtf8("progressbar"))
        self.gridLayout.addWidget(self.progressbar, 0, 0, 1, 1)

        self.retranslateUi(Progress)
        QtCore.QMetaObject.connectSlotsByName(Progress)

    def retranslateUi(self, Progress):
        pass


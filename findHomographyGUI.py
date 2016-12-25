# -*- coding: utf-8 -*-

""" 
  findHomographyGUI.py
    detect keypoints and their matches and homography transform in Qt GUI
    based on getparseGUI.py
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import cv2

from module_core.Image import *
from module_core.Matcher import *
from module_core.Concatenate import *
from module_core.Measure import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle('findHomographyGUI window')

        # Window Object
        self.widget = QWidget(self)

        # Widget Object
        self.inputWidget = ImageInputWidget(self)
        self.canvasWidget = CanvasWidget(self)
        self.matchingWidget = MatchingControlWidget(self)

        # Layout Object (Left Side)
        self.layout_left = QVBoxLayout(self)
        self.layout_left.setAlignment(Qt.AlignTop)
        self.layout_left.addWidget(self.inputWidget)
        self.layout_left.addWidget(self.canvasWidget)

        # Layout Object (Right Side)
        self.layout_right = QVBoxLayout(self)
        self.layout_right.addWidget(self.matchingWidget)
        self.matchingWidget.setMaximumWidth(420)
        self.matchingWidget.setMinimumWidth(300)

        # Layout Object (Parent Frame)
        self.layout_frame = QHBoxLayout(self)
        self.layout_frame.addLayout(self.layout_left)
        self.layout_frame.addLayout(self.layout_right)

        self.widget.setLayout(self.layout_frame)
        self.setCentralWidget(self.widget)

        # Matching processor
        self.controller = MainController()
        self.controller.setParent(self)


class MainController(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)

            cls.__instance.__parentWindow = None

            cls.__instance.__myImageObjects = [None, None]
            cls.__instance.__concatenatedImageObject = None
            cls.__instance.__measuredImageObject = None

            cls.__instance.__matchingProcessor = MatchingProcessor()
            cls.__instance.__concatenator = None
            cls.__instance.__concatenateWindow = None
            cls.__instance.__measurer = None
            cls.__instance.__measureWindow = None
            cls.__instance.__inputWidget = None
            cls.__instance.__canvasWidget = None
            cls.__instance.__canvasView = None
            cls.__instance.__canvasScene = None
            cls.__instance.__controlWidget = None
        return cls.__instance

    def __init__(self):
        pass

    def setParent(self, widget):
        self.__parentWindow = widget

    def setConcatenator(self, con):
        self.__concatenator = con

    def concatenator(self):
        return self.__concatenator

    def setConcatenateWindow(self, widget):
        self.__concatenateWindow = widget

    def concatenateWindow(self):
        return self.__concatenateWindow

    def setMeasurer(self, mes):
        self.__measurer = mes

    def measurer(self):
        return self.__measurer

    def setMeasureWindow(self, widget):
        self.__measureWindow = widget

    def measureWindow(self):
        return self.__measureWindow

    def setInputWidget(self, widget):
        self.__inputWidget = widget

    def inputWidget(self):
        return self.__inputWidget

    def setCanvasWidget(self, widget):
        self.__canvasWidget = widget

    def canvasWidget(self):
        return self.__canvasWidget

    def setCanvasView(self, widget):
        self.__canvasView = widget

    def canvasView(self):
        return self.__canvasView

    def setCanvasScene(self, widget):
        self.__canvasScene = widget

    def canvasScene(self):
        return self.__canvasScene

    def setControlWidget(self, widget):
        self.__controlWidget = widget

    def controlWidget(self):
        return self.__controlWidget

    def imageRegist(self, pos, filepath):
        self.__myImageObjects[pos] = MyImage(filepath)

        # Regist image to MatchingProcessor
        self.__matchingProcessor.setImage(pos, self.__myImageObjects[pos])

        # Regist image to CanvasView Widget
        imageItem = self.__canvasView.imageAdd(pos, self.__myImageObjects[pos])
        self.__myImageObjects[pos].setPixmapItem(imageItem)

    def imageUnregist(self, item):
        for (i, obj) in enumerate(self.__myImageObjects):
            if obj is item:
                self.__myImageObjects[i] = None
                self.__matchingProcessor.deleteAllMatches()

    def getMyImageObject(self, side):
        if side == 0 or side == 1:
            return self.__myImageObjects[side]
        else:
            return None

    def getConcatenatedImageObject(self):
        return self.__concatenatedImageObject

    def getSide(self, imageObject):
        for (i, obj) in enumerate(self.__myImageObjects):
            if obj is imageObject:
                return i

    def execMatch(self):
        if self.__matchingProcessor.im1 is None or self.__matchingProcessor.im2 is None:
            print "Warning: some of images are not registered."
            return

        self.__matchingProcessor.clean()

        self.__matchingProcessor.detect()
        self.__matchingProcessor.compute()

        if self.__controlWidget.nndrChecked():
            self.__matchingProcessor.knnMatch()
            self.__matchingProcessor.nndr(self.__controlWidget.nndrSliderValue())
        else:
            self.__matchingProcessor.match()

        self.__matchingProcessor.extractMatches()

        if self.__controlWidget.distanceChecked():
            self.__matchingProcessor.distanceCutOff(self.__controlWidget.distanceSliderValue())
        if self.__controlWidget.limitChecked():
            self.__matchingProcessor.YCutOff(self.__controlWidget.limitSliderValue())

        self.__matchingProcessor.calculateHomography()

        self.__matchingProcessor.drawMatch()

    def isAcceptedMatch(self, idx):
        return self.__matchingProcessor.matchPairs[idx].isAccepted()

    def dumpMatch(self, idx=None):
        self.__matchingProcessor.dumpMatch(idx)

    def setEnableMatch(self, idx):
        self.__matchingProcessor.matchPairs[idx].enable()
        matchingLine = self.__myImageObjects[0].pixmapItem.getMatchingPoint(idx).getMatchingLine()
        matchingLine.setColor(self.__matchingProcessor.matchPairs[idx].distanceToHSV())
        matchingLine.status = True

    def setDisableMatch(self, idx):
        self.__matchingProcessor.matchPairs[idx].disable()
        matchingLine = self.__myImageObjects[0].pixmapItem.getMatchingPoint(idx).getMatchingLine()
        matchingLine.setColor(self.__matchingProcessor.matchPairs[idx].distanceToHSV())
        matchingLine.status = False

    def setPoint(self, side, idx, x=None, y=None):
        self.__matchingProcessor.matchPairs[idx].setPoint(side, x, y)

    def setPointByOffset(self, side, idx, x=None, y=None):
        self.__matchingProcessor.matchPairs[idx].setPoint(side, x, y)

    def execConcatenate(self):
        self.__matchingProcessor.rehashHomography()
        self.__concatenator = Concatenator( \
            self.__matchingProcessor.im1, self.__matchingProcessor.im2, \
            self.__matchingProcessor.H, self.__matchingProcessor.matchPairs)
        if self.__concatenateWindow is None:
            self.__concatenateWindow = ConcatenateWindow(self.__parentWindow)
            self.__concatenateWindow.show()
        else:
            self.__concatenateWindow.show()
            self.__concatenateWindow.activateWindow()

        img = self.__concatenator.concatenate()
        self.setConcatenatedImage(img)
        self.__concatenateWindow.drawImage(img.getInQPixmap())

    def setConcatenatedImage(self, img):
        self.__concatenatedImageObject = img

    def getConcatenatedImage(self):
        return self.__concatenatedImageObject

    def setMeasuredImage(self, img):
        self.__measuredImageObject = img

    def getMeasuredImage(self, img):
        return self.__measuredImageObject

    def deleteAllMatches(self):
        self.__matchingProcessor.deleteAllMatches()

    def execMeasure(self):
        if self.__measureWindow is None:
            self.__measurer = Measure()
            self.__measureWindow = MeasureWindow(self.__parentWindow)
            self.__measureWindow.show()
        else:
            self.__measureWindow.show()
            self.__measureWindow.activateWindow()


class ImageInputWidget(QWidget):
    input_path = ""
    input_status = 0

    def __init__(self, parent=None):
        super(ImageInputWidget, self).__init__(parent)

        # Regist self to MainContorller
        MainController().setInputWidget(self)

        # Widget Parts
        self.labelFile = QLabel("Input File:")
        self.inputBox = QLineEdit()
        self.fileDialogButton = QPushButton("...", self)
        self.fileAddButton = QPushButton(" + ", self)
        self.labelTo = QLabel("To:")
        self.comboBox = QComboBox(self)

        # ComboBox Setting (specify side of image)
        self.comboBox.addItem("Left")
        self.comboBox.addItem("Right")

        # Layout Object
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.labelFile)
        self.layout.addWidget(self.inputBox)
        self.layout.addWidget(self.fileDialogButton)
        self.layout.addWidget(self.fileAddButton)
        self.layout.addWidget(self.labelTo)
        self.layout.addWidget(self.comboBox)

        # Widget Object
        self.setLayout(self.layout)

        # Connect buttons to signals
        self.connect(self.fileDialogButton, SIGNAL('clicked()'), self.filedialog_open)
        self.connect(self.fileAddButton, SIGNAL('clicked()'), self.imageFileAdd)

    # called if fileDialogButton pressed
    def filedialog_open(self):
        # QFileDialog Object
        self.input_path = QFileDialog.getOpenFileName( \
                self, "Select Image File:", ".", "Image Files (*.jpg *.png)")
        if (self.input_path != ""):
            self.inputBox.setText(self.input_path)

    # called if fileAddButton pressed
    def imageFileAdd(self):
        MainController().imageRegist(self.comboBox.currentIndex(), self.input_path)


class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)

        # Widget Parts
        self.canvas = CanvasView(self)

        # Regist self to MainContorller
        MainController().setCanvasWidget(self)

        # Widget for Control View
        self.controlGroup = QGroupBox("View Control")
        self.controlLayout = QHBoxLayout(self)

        self.zoomButtonPlus = QPushButton('+', self)
        self.zoomButtonMinus = QPushButton('-', self)
        self.zoomStatusLabel = QLabel('Current Zoom Factor: %d' \
                % self.canvas.getZoomState(), self)

        self.controlLayout.addWidget(self.zoomButtonPlus)
        self.controlLayout.addWidget(self.zoomButtonMinus)
        self.controlLayout.addWidget(self.zoomStatusLabel)
        self.controlGroup.setLayout(self.controlLayout)

        # Layout Object
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.controlGroup)
        self.setLayout(self.layout)

        # Connect buttons to signals
        self.connect(self.zoomButtonPlus, SIGNAL('clicked()'), self.zoomPlus)
        self.connect(self.zoomButtonMinus, SIGNAL('clicked()'), self.zoomMinus)

    def zoomPlus(self):
        if self.canvas.getZoomState() < 9:
            self.canvas.scale(1.25, 1.25)
            self.canvas.setZoomState(self.canvas.getZoomState() + 1)
            self.zoomStatusLabel.setText('Current Zoom Factor: %d' \
                    % self.canvas.getZoomState())

    def zoomMinus(self):
        if self.canvas.getZoomState() > -8:
            self.canvas.scale(0.8, 0.8)
            self.canvas.setZoomState(self.canvas.getZoomState() - 1)
            self.zoomStatusLabel.setText('Current Zoom Factor: %d' \
                    % self.canvas.getZoomState())


class MatchingControlWidget(QWidget):
    def __init__(self, parent=None):
        super(MatchingControlWidget, self).__init__(parent)

        # Regist self to MainController
        MainController().setControlWidget(self)

        # Layouts and Widgets Initialize
        self.frameLayout = QVBoxLayout(self)

        #-------------------------------------------------------
        # Matching Parameter Section
        # GroupBox
        #-------------------------------------------------------
        self.paramGroupBox = QGroupBox("Matching Option")
        self.paramGroupBox_grid = QGridLayout(self.paramGroupBox)
        self.paramGroupBox.setLayout(self.paramGroupBox_grid)
        self.frameLayout.addWidget(self.paramGroupBox)

        # Threshold control
        self.paramCheckBox1 = QCheckBox(self)
        self.paramGroupBox_label1 = QLabel("Distance Threshold:")
        self.paramSlider1 = QSlider(Qt.Horizontal, self)
        self.paramSlider1.setMaximum(1000)
        self.paramSlider1.setMinimum(   0)
        self.svalue1 = QLabel(" 0.0")
        self.paramSlider1.setTracking(True)
        self.paramGroupBox_grid.addWidget(self.paramCheckBox1, 0, 0)
        self.paramGroupBox_grid.addWidget(self.paramGroupBox_label1, 0, 1)
        self.paramGroupBox_grid.addWidget(self.paramSlider1, 0, 2)
        self.paramGroupBox_grid.addWidget(self.svalue1, 0, 3)
        self.connect(self.paramCheckBox1, SIGNAL('stateChanged(int)'), self.distanceSliderSwitch)
        self.connect(self.paramSlider1, SIGNAL('valueChanged(int)'), self.distanceSliderChanged)

        self.paramCheckBox1.setChecked(True)
        self.paramSlider1.setValue(400)

        # NNDR Threshold control
        self.paramCheckBox2 = QCheckBox(self)
        self.paramGroupBox_label2 = QLabel("NNDR Threshold:")
        self.paramSlider2 = QSlider(Qt.Horizontal, self)
        self.paramSlider2.setMaximum(100)
        self.paramSlider2.setMinimum(  0)
        self.svalue2 = QLabel("0.00")
        self.paramSlider2.setTracking(True)
        self.paramGroupBox_grid.addWidget(self.paramCheckBox2, 1, 0)
        self.paramGroupBox_grid.addWidget(self.paramGroupBox_label2, 1, 1)
        self.paramGroupBox_grid.addWidget(self.paramSlider2, 1, 2)
        self.paramGroupBox_grid.addWidget(self.svalue2, 1, 3)
        self.connect(self.paramCheckBox2, SIGNAL('stateChanged(int)'), self.nndrSliderSwitch)
        self.connect(self.paramSlider2, SIGNAL('valueChanged(int)'), self.nndrSliderChanged)

        self.paramCheckBox2.setChecked(False)
        self.paramSlider2.setValue(60)
        self.paramSlider2.setDisabled(True)

        # Y limitation control
        self.paramCheckBox3 = QCheckBox(self)
        self.paramGroupBox_label3 = QLabel("Y limitation:")
        self.paramSlider3 = QSlider(Qt.Horizontal, self)
        self.paramSlider3.setMaximum(100)
        self.paramSlider3.setMinimum(  0)
        self.svalue3 = QLabel("0.00")
        self.paramSlider3.setTracking(True)
        self.paramGroupBox_grid.addWidget(self.paramCheckBox3, 2, 0)
        self.paramGroupBox_grid.addWidget(self.paramGroupBox_label3, 2, 1)
        self.paramGroupBox_grid.addWidget(self.paramSlider3, 2, 2)
        self.paramGroupBox_grid.addWidget(self.svalue3, 2, 3)
        self.connect(self.paramCheckBox3, SIGNAL('stateChanged(int)'), self.limitSliderSwitch)
        self.connect(self.paramSlider3, SIGNAL('valueChanged(int)'), self.limitSliderChanged)

        self.paramCheckBox3.setChecked(False)
        self.paramSlider3.setValue(60)
        self.paramSlider3.setDisabled(True)

        #-------------------------------------------------------
        # Matching Execution Section
        # Buttons
        #-------------------------------------------------------
        self.MatchingExecutionLayout = QGridLayout(self)
        self.frameLayout.addLayout(self.MatchingExecutionLayout)

        # Matching Execution Button
        self.execButton1 = QPushButton("Match", self)
        self.MatchingExecutionLayout.addWidget(self.execButton1, 0, 0)

        # Concatenate Execution Button
        self.execButton2 = QPushButton("Concatenate", self)
        self.MatchingExecutionLayout.addWidget(self.execButton2, 0, 1)

        # Delete All matching point Button
        self.execButton3 = QPushButton("Delete All Matches", self)
        self.MatchingExecutionLayout.addWidget(self.execButton3, 0, 2)

        # Match & Concatenate Execution Button
        self.execButton4 = QPushButton("Measure", self)
        self.MatchingExecutionLayout.addWidget(self.execButton4, 1, 0, 1, 3)

        # Connect Buttons
        self.connect(self.execButton1, SIGNAL('clicked()'), MainController().execMatch)
        self.connect(self.execButton2, SIGNAL('clicked()'), MainController().execConcatenate)
        self.connect(self.execButton3, SIGNAL('clicked()'), MainController().deleteAllMatches)
        self.connect(self.execButton4, SIGNAL('clicked()'), MainController().execMeasure)

        #-------------------------------------------------------
        # Matched Point List Section
        # ListItem
        #-------------------------------------------------------
        self.matchList = QListWidget(self)
        self.frameLayout.addWidget(self.matchList)

    def distanceSliderSwitch(self):
        if self.paramCheckBox1.isChecked() == True:
            self.paramSlider1.setEnabled(True)
        else:
            self.paramSlider1.setDisabled(True)

    def nndrSliderSwitch(self):
        if self.paramCheckBox2.isChecked() == True:
            self.paramSlider2.setEnabled(True)
        else:
            self.paramSlider2.setDisabled(True)

    def limitSliderSwitch(self):
        if self.paramCheckBox3.isChecked() == True:
            self.paramSlider3.setEnabled(True)
        else:
            self.paramSlider3.setDisabled(True)

    def distanceSliderChanged(self):
        self.svalue1.setText("%5.1f" % (self.paramSlider1.value() / 10.0))

    def nndrSliderChanged(self):
        self.svalue2.setText("%4.2f" % (self.paramSlider2.value() / 100.0))

    def limitSliderChanged(self):
        self.svalue3.setText("%4.2f" % (self.paramSlider3.value() / 100.0))

    def distanceChecked(self):
        if self.paramCheckBox1.isChecked() == True:
            return True
        else:
            return False

    def nndrChecked(self):
        if self.paramCheckBox2.isChecked() == True:
            return True
        else:
            return False

    def limitChecked(self):
        if self.paramCheckBox3.isChecked() == True:
            return True
        else:
            return False

    def distanceSliderValue(self):
        return self.paramSlider1.value() / 10.0

    def nndrSliderValue(self):
        return self.paramSlider2.value() / 100.0

    def limitSliderValue(self):
        return self.paramSlider3.value() / 100.0



class CanvasView(QGraphicsView):
    isPressed = False
    isHandleDragged = False
    isPolygonMode = False

    cachedPolygon = None
    cachedPolygon_HandleItems = []
    cachedPolygon_LineItems = []
    pointerH, pointerV = None, None

    imageItems = []
    edgeItems = []

    capturedItems = []
    capturedItem  = None

    contextMenuItems = []

    currentPos   = None
    x0, y0       = None, None

    zoomState = 0

    def __init__(self, parent=None):
        super(CanvasView, self).__init__(parent)

        # Regist self to MainController()
        MainController().setCanvasView(self)

        self.scene = CanvasScene(self)
        self.setScene(self.scene)

        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.contextMenu = QMenu();
        #self.contextMenuAction1 = self.contextMenu.addAction("Delete item")

        #self.connect(self.contextMenuAction1, SIGNAL('triggered()'), self.imageDelete)

    # called if FileAddButton pressed
    def imageAdd(self, pos, myImageItem):
        imageItem = ImageWithMatchingPoint(myImageItem)
        self.scene.addItem(imageItem)

        x, y = imageItem.parentImage.shape()
        if pos == 0:
            imageItem.setPos(QPointF(self.frameRect().width() * -0.05 - x, y / -2.0))
        elif pos == 1:
            imageItem.setPos(QPointF(self.frameRect().width() * 0.05, y / -2.0))
        self.imageItems.append(imageItem)

        return imageItem

    # called if contextMenuAction1 "Delete item" pressed
    def imageDelete(self):
        for (i, imageItem) in enumerate(self.imageItems):
            if imageItem is self.capturedItem:
                self.scene.removeItem(self.capturedItem)
                del(self.imageItems[i])
                MainController().imageUnregist(imageItem.parentImage)

    def getZoomState(self):
        return self.zoomState

    def setZoomState(self, z):
        self.zoomState = z

    def addPolygonInit(self):
        self.isPolygonMode = True
        self.cachedPolygon = QPolygonF()

    def addPolygonAbort(self):
        self.isPolygonMode = False
        self.cachedPolygon = None
        self.removeLinePointer()

    def deletePolygon(self):
        pass

    def refreshCurrentLine(self, pos):
        if self.cachedPolygon_LineItems != []:
            currentLineItem = self.cachedPolygon_LineItems[-1]
            line = currentLineItem.line()
            line.setP2(pos)
            currentLineItem.setLine(line)

    def removeAllCachedPolygon(self):
        for item in self.cachedPolygon_HandleItems:
            self.scene.removeItem(item)
        for item in self.cachedPolygon_LineItems:
            self.scene.removeItem(item)
        self.cachedPolygon_HandleItems = []
        self.cachedPolygon_LineItems = []

    def drawLinePointer(self, pos):
        self.removeLinePointer()

        left, top = self.sceneRect().x(), self.sceneRect().y()
        w, h = self.sceneRect().width(), self.sceneRect().height()
        x, y = pos.x(), pos.y()

        self.pointerH = self.scene.addLine(left, y, left+w, y)
        self.pointerV = self.scene.addLine(x, top, x, top+h)

    def removeLinePointer(self):
        if self.pointerH is not None:
            self.scene.removeItem(self.pointerH)
        if self.pointerV is not None:
            self.scene.removeItem(self.pointerV)
        self.scene.update()

    def mousePressEvent(self, event):
        self.isPressed = True
        self.xdiff, self.ydiff = 0, 0
        
        self.currentPos = self.mapToScene(event.pos())
        self.x0, self.y0 = self.currentPos.x(), self.currentPos.y()

        print "current pos in view: ", self.mapFromScene(self.currentPos)
        print "current pos in scene: ", self.currentPos

        self.capturedItems =  self.items(event.pos())
        capturedItemTypes = map(type, self.capturedItems)
        for capturedItem in self.capturedItems:
            if type(capturedItem) == MatchingPointHandle:
                self.capturedItem = capturedItem
                MainController().dumpMatch(capturedItem.pointID)
                return
            if type(capturedItem) == ImageWithMatchingPoint:
                self.capturedItem = capturedItem
                currentPos_inImage = capturedItem.mapFromScene(self.currentPos)
                print "current pos in imageItem: ", currentPos_inImage
                if self.isPolygonMode:
                    if not (PolygonHandle in capturedItemTypes):
                        self.cachedPolygon.append(currentPos_inImage)

                        handle = PolygonHandle(0, \
                          0 if self.cachedPolygon_HandleItems == [] else len(self.cachedPolygon_HandleItems))
                        handle.setPos(self.currentPos)
                        self.scene.addItem(handle)
                        self.cachedPolygon_HandleItems.append(handle)

                        self.refreshCurrentLine(self.currentPos)
                        edge = QGraphicsLineItem(QLineF(self.currentPos, self.currentPos))
                        self.scene.addItem(edge)
                        self.cachedPolygon_LineItems.append(edge)
                    else:
                        self.cachedPolygon.append(self.cachedPolygon.at(0))
                        self.capturedItem.setPolygon(self.cachedPolygon)

                        self.removeAllCachedPolygon()
                        self.removeLinePointer()
                        self.isPolygonMode = False
                return

        # Default Action
        super(CanvasView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isPressed == True and type(self.capturedItem) is MatchingPointHandle:
            self.isHandleDragged = True
            handle = self.capturedItem

            self.currentPos = self.mapToScene(event.pos())
            x, y = self.currentPos.x(), self.currentPos.y()
            xdiff, ydiff = x - self.x0, y - self.y0
            handle.moveOffset(xdiff, ydiff)
            self.x0, self.y0 = x, y
            return

        if self.isPolygonMode:
            self.currentPos = self.mapToScene(event.pos())
            self.drawLinePointer(self.currentPos)
            self.refreshCurrentLine(self.currentPos)


        super(CanvasView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isHandleDragged == True:
            handle = self.capturedItem
            MainController().setPoint(handle.side, handle.pointID, handle.pos().x(), handle.pos().y())

        self.isPressed = False
        self.isHandleDragged = False
        self.capturedItem = None

        # Default Action
        super(CanvasView, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        cnt = 0
        self.capturedItems = self.scene.items(self.mapToScene(event.pos()))
        if self.capturedItems != []:
            # ContextMenu for ImageWithMatchingPoint
            for item in [i for i in self.capturedItems if type(i) is ImageWithMatchingPoint]:
                self.capturedItem = item
                self.contextMenuItems.append( \
                        self.contextMenu.addAction("Delete this image"))
                self.contextMenuItems.append( \
                        self.contextMenu.addAction("Add Polygon..."))
                self.contextMenuItems.append( \
                        self.contextMenu.addAction("Delete Polygon"))
                self.contextMenuItems[cnt].triggered.connect(self.imageDelete)
                cnt += 1
                self.contextMenuItems[cnt].triggered.connect(self.addPolygonInit)
                cnt += 1
                self.contextMenuItems[cnt].triggered.connect(item.deletePolygon)
                cnt += 1

            # ContextMenu for MatchingPoint
            for item in [i for i in self.capturedItems if type(i) is MatchingPointHandle]:
                idx = item.pointID
                if item.getMatchingLine().status is True:
                    self.contextMenuItems.append( \
                            self.contextMenu.addAction("[#%2d]Disable this Match" % idx))
                    self.contextMenuItems[cnt].triggered.connect( \
                            lambda: MainController().setDisableMatch(idx))
                elif item.getMatchingLine().status is False:
                    self.contextMenuItems.append( \
                            self.contextMenu.addAction("[#%2d]Enable this Match" % idx))
                    self.contextMenuItems[cnt].triggered.connect( \
                            lambda: MainController().setEnableMatch(idx))
                cnt += 1

        self.contextMenu.exec_(self.mapToGlobal(event.pos()))
        self.contextMenu.clear()
        self.contextMenuItems = []

        MainController().dumpMatch()

        self.capturedItems = []
        self.capturedItem = None


class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CanvasScene, self).__init__(parent)

        # Regist self to MainController()
        MainController().setCanvasScene(self)

        self.matchingLines = []
        self.setBackgroundBrush(QColor(200, 200, 200))

    # Add Matching Line
    def addMatchingLine(self, i, p1, p2, color=None, parent=None):
        if type(p1) is not MatchingPointHandle or type(p2) is not MatchingPointHandle:
            return
        else:
            matchingLine = MatchingLine(i, p1, p2, color)
            self.addItem(matchingLine)
            self.matchingLines.append(matchingLine)
            p1.setMatchingLine(matchingLine)
            p2.setMatchingLine(matchingLine)

    def deleteAllMatchingLine(self):
        for matchingLine in self.matchingLines:
            self.removeItem(matchingLine)
        self.matchingLines = []


"""
  class ImageWithMatchingPoint
    Group Object of Pixmap(Image), MatchingPoint(Rect)
    Inherited from QGraphicsItemGroup
"""
class ImageWithMatchingPoint(QGraphicsItemGroup):
    def __init__(self, myImage, parent=None):
        super(ImageWithMatchingPoint, self).__init__(parent)

        # linked MyImage item
        self.parentImage = myImage
        self.side = MainController().getSide(myImage)

        # Matching point storing array
        self.matchingPoints = []

        # Matching area specification
        self.matchingPolygon = None

        # Create an image(base)
        self.pixmapItem = self.parentImage.getInQPixmap()
        self.imageItem = QGraphicsPixmapItem(self.pixmapItem, self)

        # Create an boundary polygon
        self.imageShape = self.imageItem.shape()
        self.imagePolygon = self.imageShape.toFillPolygon()
        self.boundaryItem = QGraphicsPolygonItem(self.imagePolygon, self)

        # Store slice polygon
        self.slicePolygonItem = None

        # Add any child items to group
        self.addToGroup(self.imageItem)
        self.addToGroup(self.boundaryItem)

    def addMatchingPoint(self, idx, x, y):
        point = MatchingPointHandle(self.side, idx, self)
        point.setPos(x, y)
        self.addToGroup(point)
        self.matchingPoints.append(point)

        return point

    def getMatchingPoint(self, idx):
        return self.matchingPoints[idx]

    def deleteMatchingPoint(self, idx):
        pass

    def deleteAllMatchingPoint(self):
        if self.matchingPoints != []:
            for match in self.matchingPoints:
                self.removeFromGroup(match)
                self.scene().removeItem(match)
            self.update()
            self.matchingPoints = []

    def setPolygon(self, polygon):
        self.slicePolygonItem = QGraphicsPolygonItem(polygon, self)
        self.slicePolygonItem.setPen(QColor(200,80,0))
        self.addToGroup(self.slicePolygonItem)
        self.parentImage.setSlice(polygon)
        self.parentImage.getSlicedInQImage().save("debug.png")

    def deletePolygon(self):
        self.removeFromGroup(self.slicePolygonItem)
        self.scene().removeItem(self.slicePolygonItem)
        self.slicePolygonItem = None
        self.parentImage.unsetSlice()

    def mouseMoveEvent(self, event):
        super(ImageWithMatchingPoint, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        super(ImageWithMatchingPoint, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(ImageWithMatchingPoint, self).mouseReleaseEvent(event)


"""
  class SlicePolygonItem
    Group Object of QGraphicsRectItem, QGraphicsLineItem
"""
#class SlicePolygonItem(QGraphicsItemGroup):
#    def __init__(self, side, polygon, parent=None):
#        super(SlicePolygonItem, self).__init__(parent)
#        self.anchorItems = []
#        self.edgeItems = []
#
#        if type(polygon) in (QPolygonF, QPolygon):
#            for i in range(0, polygon.count() - 1):
#                anchor = PolygonHandle(side, i)
#                anchor.setPos(polygon.at(i))
#                self.anchorItems.append(anchor)
#                self.addToGroup(anchor)
#            for i in range(0, polygon.count() - 1):
#                if i <= polygon.count() - 3:
#                    line = PolygonEdgeLine(i, self.anchorItems[i], self.anchorItems[i+1])
#                else:
#                    line = PolygonEdgeLine(i, self.anchorItems[i], self.anchorItems[0])
#                self.edgeItems.append(line)
#                self.addToGroup(line)


    Group Object of QGraphicsRectItem, QGraphicsLineItem
    Inherited from QGraphicsItemGroup
"""
class MatchingPointHandle(QGraphicsItemGroup):
    def __init__(self, side, idx, parent=None):
        super(MatchingPointHandle, self).__init__(parent)

        self.side = side
        self.pointID = idx
        self.items = []

        # Pointer to corresponding MatchingLine
        self.line = None

        self.frame = QGraphicsRectItem(QRectF(-5,-5,10,10), self)
        self.frame.setPen(QColor(0,0,0))
        self.frame.setBrush(QColor(180,180,180,60))
        self.vline = QGraphicsLineItem(QLineF( 0,-5, 0, 5), self)
        self.vline.setPen(QColor(0,0,0))
        self.hline = QGraphicsLineItem(QLineF(-5, 0, 5, 0), self)
        self.hline.setPen(QColor(0,0,0))

        self.items.append(self.frame)
        self.items.append(self.vline)
        self.items.append(self.hline)

        self.addToGroup(self.frame)
        self.addToGroup(self.vline)
        self.addToGroup(self.hline)

    def moveOffset(self, xdiff, ydiff):
        x, y = self.pos().x(), self.pos().y()
        self.setPos(x + xdiff, y + ydiff)
        self.line.movePos(self.side, xdiff, ydiff)

    def setMatchingLine(self, lineObject):
        self.line = lineObject

    def getMatchingLine(self):
        return self.line


"""
  class PolygonHandle
    Group Object of QGraphicsRectItem, QGraphicsLineItem
    Inherited from DraggableHandle
"""
class PolygonHandle(DraggableHandle):
    def __init__(self, side, idx, parent=None):
        super(PolygonHandle, self).__init__(side, parent)

        self.pointID = idx
        self.lineFrom = None
        self.lineTo = None

    def moveOffset(self, xdiff, ydiff):
        super(MatchingPointHandle, self).moveOffset(xdiff, ydiff)


"""
  class DependentLineItem
    Line Object contains both side of nodes
    Inherited from QGraphicsLineItem
"""
class DependentLineItem(QGraphicsLineItem):
    def __init__(self, p1=None, p2=None, parent=None):
        super(DependentLineItem, self).__init__(parent)
        # set two MatchingPointHandle instances
        self.point1 = p1 # origin
        self.point2 = p2 # terminal

        if self.point1 is not None:
            self.point1_pos = self.point1.mapToScene(0, 0) #QPointF
        if self.point2 is not None:
            self.point2_pos = self.point2.mapToScene(0, 0) #QPointF

        self.lineF = QLineF(self.point1_pos, self.point2_pos)
        self.setLine(self.lineF)

    def movePos(self, side, xdiff, ydiff):
        if side == 0:
            self.point1_pos = QPointF(self.point1_pos.x() + xdiff, self.point1_pos.y() + ydiff)
            self.lineF.setP1(self.point1_pos)
        elif side == 1:
            self.point2_pos = QPointF(self.point2_pos.x() + xdiff, self.point2_pos.y() + ydiff)
            self.lineF.setP2(self.point2_pos)
        self.setLine(self.lineF)


    def setColor(self, color):
        self.setPen(QColor.fromHsv(color[0], color[1], color[2]))


"""
  class PolygonEdgeLine
    Line Object contains previous/next nodes
    Inherited fro DependentLineItem
"""
class PolygonEdgeLine(DependentLineItem):
    def __init__(self, idx=None, p1=None, p2=None, color=None, parent=None):
        super(PolygonEdgeLine, self).__init__(p1, p2, parent)

        # PolygonEdgeLine number
        self.lineID = idx

        self.setPen(QColor(160,80,0))

class ConcatenateWindow(QWidget):
    def __init__(self, parent=None):
        super(ConcatenateWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.resize(800,600)

        self.imageItem = QLabel("image here")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.imageItem)
        self.setLayout(self.layout)

    def drawImage(self, pixmap):
        self.imageItem.setPixmap(pixmap)

    def closeEvent(self, event):
        event.ignore()
        self.hide()



def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = MyWindow()
    window.resize(1280,800)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()


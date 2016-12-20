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
            cls.__instance.__matchingProcessor = MatchingProcessor()
            cls.__instance.__concatenator = None
            cls.__instance.__concatenateWindow = None
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

    def setConcatenatorWindow(self, widget):
        self.__concatenatorWindow = widget

    def setInputWidget(self, widget):
        self.__inputWidget = widget

    def setCanvasWidget(self, widget):
        self.__canvasWidget = widget

    def setCanvasView(self, widget):
        self.__canvasView = widget

    def setCanvasScene(self, widget):
        self.__canvasScene = widget

    def setControlWidget(self, widget):
        self.__controlWidget = widget

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

    def execConcatenate(self):
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
        self.__concatenateWindow.drawImage(img.getInQPixmap())

    def deleteAllMatches(self):
        self.__matchingProcessor.deleteAllMatches()


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
        self.execButton4 = QPushButton("Match -> Concatenate", self)
        self.MatchingExecutionLayout.addWidget(self.execButton4, 1, 0, 1, 3)

        # Connect Buttons
        self.connect(self.execButton1, SIGNAL('clicked()'), MainController().execMatch)
        self.connect(self.execButton2, SIGNAL('clicked()'), MainController().execConcatenate)
        self.connect(self.execButton3, SIGNAL('clicked()'), MainController().deleteAllMatches)

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
    isDragged = False

    imageItems = []
    edgeItems = []

    capturedItems = []
    capturedItem  = None

    currentPos   = None
    x0, y0       = None, None
    xdiff, ydiff = None, None

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
        self.contextMenuAction1 = self.contextMenu.addAction("Delete item")

        self.connect(self.contextMenuAction1, SIGNAL('triggered()'), self.imageDelete)

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

    def mouseMoveEvent(self, event):
        if self.isPressed == True:
            self.isDragged = True
            self.currentPos = event.pos()
            x, y = self.currentPos.x(), self.currentPos.y()

        if type(self.capturedItem) is QGraphicsRectItem and \
           type(self.capturedItem.group()) is TransformableImage:
            self.xdiff, self.ydiff = x - self.x0, y - self.y0
            self.capturedItem.group().moveAnchor(self.capturedItem, self.xdiff, self.ydiff)
            self.x0, self.y0 = x, y
            return

        super(CanvasView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.isPressed = True
        self.xdiff, self.ydiff = 0, 0
        
        self.currentPos = event.pos()
        self.x0, self.y0 = self.currentPos.x(), self.currentPos.y()

        print "current pos in view: ", self.currentPos
        print "current pos in scene: ", self.mapToScene(self.currentPos)

        self.capturedItems =  self.items(event.pos())
        for capturedItem in self.capturedItems:
            if type(capturedItem) == ImageWithMatchingPoint:
                self.capturedItem = capturedItem
                return

        # Default Action
        super(CanvasView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        isPressed = False
        isDragged = False
        self.capturedItem = None
        self.xdiff, self.ydiff = None, None

        # Default Action
        super(CanvasView, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        self.capturedItems = self.scene.items(self.mapToScene(event.pos()))
        if self.capturedItems != []:
            if MatchingPointHandle in map(type, self.capturedItems):
                pass

                #self.capturedItem = self.capturedItems[0].group()

        self.contextMenu.exec_(self.mapToGlobal(event.pos()))

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
            p1.group().setMatchingLine(matchingLine)
            p2.group().setMatchingLine(matchingLine)

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

        # Matching point storing array
        self.matchingPoints = []

        # Matching line storing array
        self.matchingLines = []

        # Create an image(base)
        self.pixmapItem = self.parentImage.getInQPixmap()
        self.imageItem = QGraphicsPixmapItem(self.pixmapItem, self)

        # Create an boundary polygon
        self.imageShape = self.imageItem.shape()
        self.imagePolygon = self.imageShape.toFillPolygon()
        self.boundaryItem = QGraphicsPolygonItem(self.imagePolygon, self)

        # Add any child items to group
        self.addToGroup(self.imageItem)
        self.addToGroup(self.boundaryItem)

    def addMatchingPoint(self, idx, x, y):
        point = MatchingPointHandle(idx, self)
        point.setPos(x, y)
        self.addToGroup(point)
        self.matchingPoints.append(point)

        return point

    def deleteMatchingPoint(self, idx):
        pass

    def setMatchingLine(self, line):
        self.matchingLines.append(line)

    def deleteAllMatchingPoint(self):
        if self.matchingPoints != []:
            for (matchingPoint, matchingLine) in zip(self.matchingPoints, self.matchingLines):
                self.removeFromGroup(matchingPoint)
                self.removeFromGroup(matchingLine)
            self.update()
            self.matchingPoints = []
            self.matchingLines = []


    def mouseMoveEvent(self, event):
        super(ImageWithMatchingPoint, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        super(ImageWithMatchingPoint, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(ImageWithMatchingPoint, self).mouseReleaseEvent(event)


"""
  class MatchingPointHandle
    Group Object of QGraphicsRectItem, QGraphicsLineItem
    Inherited from QGraphicsItemGroup
"""
class MatchingPointHandle(QGraphicsItemGroup):
    def __init__(self, idx=None, parent=None):
        super(MatchingPointHandle, self).__init__(parent)

        self.items = []

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


"""
  class MatchingLine
    Line Object contains both side of nodes
    Inherited from QGraphicsLineItem
"""
class MatchingLine(QGraphicsLineItem):
    def __init__(self, idx=None, p1=None, p2=None, color=None, parent=None):
        super(MatchingLine, self).__init__(parent)
        # set two MatchingPointHandle instances
        self.point1 = p1 # origin
        self.point2 = p2 # terminal

        self.point1_pos = self.point1.mapToScene(0, 0) #QPointF
        self.point2_pos = self.point2.mapToScene(0, 0) #QPointF
        self.setLine(QLineF(self.point1_pos, self.point2_pos))

        if color is None:
            self.setPen(QColor(0,0,0))
        else:
            self.setPen(QColor.fromHsv(color[0], color[1], color[2]))


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


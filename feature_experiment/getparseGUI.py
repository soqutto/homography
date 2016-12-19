# -*- coding: utf-8 -*-

# getparseGUI.py
# homography transform in Qt GUI

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import cv2

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle('getparseGUI window')

        # Window Object
        self.widget = QWidget(self)

        # Widget Object
        self.inputWidget = ImageInputWidget(self)
        self.attributionWidget = ImageAttributionWidget(self)
        self.canvasWidget = CanvasWidget(self)

        # Layout Object
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.inputWidget)
        self.layout.addWidget(self.attributionWidget)
        self.layout.addWidget(self.canvasWidget)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)


class ImageInputWidget(QWidget):
    input_path = ""
    input_status = 0

    def __init__(self, parent=None):
        super(ImageInputWidget, self).__init__(parent)

        # Widget Parts
        self.Label = QLabel("Input File:")
        self.InputBox = QLineEdit()
        self.FileDialogButton = QPushButton("...", self)
        self.FileAddButton = QPushButton(" + ", self)


        # Layout Object
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.InputBox)
        self.layout.addWidget(self.FileDialogButton)
        self.layout.addWidget(self.FileAddButton)

        # Widget Object
        self.setLayout(self.layout)

        # Connect buttons to signals
        self.connect(self.FileDialogButton, SIGNAL('clicked()'), self.filedialog_open)
        self.connect(self.FileAddButton, SIGNAL('clicked()'), self.imageFileAdd)


    # called if FileDialogButton pressed
    def filedialog_open(self):
        # QFileDialog Object
        self.input_path = QFileDialog.getOpenFileName( \
                self, "Select Image File:", ".", "Image Files (*.jpg *.png)")
        if (self.input_path != ""):
            self.InputBox.setText(self.input_path)

    def imageFileAdd(self):
        self.parent().findChild(CanvasView).imageFileAdd(self.input_path)

class ImageAttributionWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageAttributionWidget, self).__init__(parent)

        # Widget Parts
        self.Label = QLabel("Opacity:")
        self.Slider = QSlider(Qt.Horizontal, self)

        # Configure Slider
        self.Slider.setMaximum(100)
        self.Slider.setMinimum(  0)

        # Layout Object
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.Slider)

        # Connect Slider to signal
        self.connect(self.Slider, SIGNAL('sliderMoved(int)'), self.OpacitySliderChanged)

    def OpacitySliderChanged(self):
        pass

    def setOpacitySlider(self, opacityFloat):
        self.Slider.setValue(opacityFloat * 100)


class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)

        # Widget Parts
        self.canvas = CanvasView(self)

        # Layout Object
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        #self.setCentralWidget(self.canvas)


class CanvasView(QGraphicsView):
    isPressed = False
    isDragged = False

    imageItems = []

    capturedItems = []
    capturedItem  = None

    currentPos   = None
    x0, y0       = None, None
    xdiff, ydiff = None, None

    def __init__(self, parent=None):
        super(CanvasView, self).__init__(parent)
        self.scene = CanvasScene(self)
        self.setScene(self.scene)

        self.setMouseTracking(True)
        self.contextMenu = QMenu();
        self.contextMenuAction1 = self.contextMenu.addAction("Delete item")

        self.connect(self.contextMenuAction1, SIGNAL('triggered()'), self.imageDelete)

    # called if FileAddButton pressed
    def imageFileAdd(self, filepath):
        transformableImageItem = TransformableImage(filepath)
        transformableImageItem.setFlags( \
                QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(transformableImageItem)
        self.imageItems.append(transformableImageItem)

    # called if contextMenuAction1 "Delete item" pressed
    def imageDelete(self):
        for (i, imageItem) in enumerate(self.imageItems):
            if imageItem is self.capturingItem:
                self.scene.removeItem(self.capturingItem)
                del(self.imageItems[i])


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

        self.capturedItems =  self.items(event.pos())
        for capturedItem in self.capturedItems:
            if type(capturedItem) == QGraphicsRectItem:
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
        self.capturingItems = self.scene.items(self.mapToScene(event.pos()))
        self.capturingItem = self.capturingItems[0].group()

        self.contextMenu.exec_(self.mapToGlobal(event.pos()))

        self.capturingItems = []
        self.capturingItem = None

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CanvasScene, self).__init__(parent)

    def addImage(self, filepath):
        pass

"""
  class TransformableImage
    Group Object of Pixmap(Image), Matrix(Transform), Boundary(Polygon), Anchor(Rect)
    Inherited from QGraphicsItemGroup
    ピクスマップ、変換行列、境界線、アンカーポイントを含んだ
    QGraphicsItemGroupベースのグループクラス
"""
class TransformableImage(QGraphicsItemGroup):
    isPressed = False
    isDragged = False
    capturingItems = []
    capturingItem = None

    def __init__(self, filepath, parent=None):
        super(TransformableImage, self).__init__(parent)

        self.setAcceptHoverEvents(True)

        # Create an image(base)
        self.pixmapItem = QPixmap(filepath)
        self.imageItem = QGraphicsPixmapItem(self.pixmapItem, self)

        self.transformMatrix = QTransformWithNumpy()
        self.transformedPixmapItem = self.pixmapItem.transformed(self.transformMatrix)
        self.imageItem.setPixmap(self.transformedPixmapItem)

        # Create an boundary polygon
        self.imageShape = self.imageItem.shape()
        self.imagePolygon = self.imageShape.toFillPolygon()
        self.boundaryItem  = QGraphicsPolygonItem(self.imagePolygon, self)

        self.corners = [self.imagePolygon.at(i) for i in range(0, self.imagePolygon.count())]
        # Create copy of self.corners(used in calculating homography matrix)
        self.cornersInit = self.corners[:]
        # Initialize empty list of each anchors
        self.anchorItems = [None for i in range(0,4)]

        # Create four corner anchors(draggable) and add to self.anchors
        for i in range(0, 4):
            self.anchorItems[i] = \
                    QGraphicsRectItem(self.corners[i].x()-5, self.corners[i].y()-5, 10, 10, self)

        # Style anchors
        for anchorItem in self.anchorItems:
            anchorItem.setPen( QColor(0, 0, 0) )
            anchorItem.setBrush( QColor(255, 255, 255) )
        # Style boundary
        self.boundaryItem.setPen( QColor(255, 0, 0) )

        # Add any child items to group
        self.addToGroup(self.imageItem)
        #self.addToGroup(self.transformedPixmapItem)
        self.addToGroup(self.boundaryItem)
        for anchorItem in self.anchorItems:
            self.addToGroup(anchorItem)

    def mouseMoveEvent(self, event):
        super(TransformableImage, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        super(TransformableImage, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(TransformableImage, self).mouseReleaseEvent(event)

    # Move one anchor point to offset(xdiff, ydiff) value
    def moveAnchor(self, passedAnchorItem, xdiff, ydiff):
        # Find Index of passedAnchorItem in self.anchorItems
        for (i, anchorItem) in enumerate(self.anchorItems):
            if anchorItem is passedAnchorItem:
                capturedAnchor = anchorItem
                capturedAnchorIdx = i
                print "capturedAnchor.pos(): ", capturedAnchor.pos()
                print "TransformableImage.corners[capturedAnchorIdx]: ", self.corners[capturedAnchorIdx]

        # Move Anchor(QGraphicsRectItem)
        currentAnchorPos = (capturedAnchor.pos().x(), capturedAnchor.pos().y())
        capturedAnchor.setPos(currentAnchorPos[0] + xdiff, currentAnchorPos[1] + ydiff)

        # Change Shape of ImagePolygon(QGraphicsPolygonItem)
        currentCornerPos = (self.corners[capturedAnchorIdx].x(), self.corners[capturedAnchorIdx].y() )
        newCornerPos = QPointF(currentCornerPos[0] + xdiff, currentCornerPos[1] + ydiff)
        self.imagePolygon.replace(capturedAnchorIdx, newCornerPos)
        self.corners[capturedAnchorIdx] = self.imagePolygon.at(capturedAnchorIdx)

        # If anchor was origin point(#0), also apply to terminal point(#4)
        if capturedAnchorIdx == 0:
            self.imagePolygon.replace(4, newCornerPos)
            self.corners[4] = self.imagePolygon.at(capturedAnchorIdx)

        # Reapply Polygon to self.boundaryItem(QGraphicsPolygonItem)
        self.boundaryItem.setPolygon(self.imagePolygon)

        # kari---
        self.cornersInitNumpy = np.float32([[corner.x(), corner.y()] for corner in self.cornersInit])
        print "TransformaleImage.cornersInitNumpy:\n", self.cornersInitNumpy
        self.cornersAfterNumpy = np.float32([[corner.x(), corner.y()] for corner in self.corners])
        print "TransformableImage.cornersAfterNumpy:\n", self.cornersAfterNumpy

        self.H, self.inliers = cv2.findHomography(self.cornersInitNumpy, self.cornersAfterNumpy)
        print "TransformableImage.H:\n", self.H
        self.transformMatrix.setMatrixInNumpy(self.H)
        self.transformedPixmapItem = self.pixmapItem.transformed(self.transformMatrix)
        self.imageItem.setPixmap(self.transformedPixmapItem)
        print "TransformedPixmap: x=%4d, y=%4d" % \
                (self.transformedPixmapItem.width(), self.transformedPixmapItem.height())

        # Determine offsets to minimal x/y value in the item
        offset_x = np.min(self.cornersAfterNumpy[:,0])
        offset_y = np.min(self.cornersAfterNumpy[:,1])
        self.imageItem.setOffset(offset_x, offset_y)
        print "TransformableImage.pixmapItem.offset: ", self.imageItem.offset()

        
        

#    def hoverEnterEvent(self, event):
#        super(hoverEnterEvent, self).hoverEnterEvent(event)
#        self.imagePolygon.setPen( QColor(255, 0, 0) )
#
#    def hoverLeaveEvent(self, event):
#        super(hoverLeaveEvent, self).hoverLeaveEvent(event)
#        self.imagePolygon.setPen( QColor(0, 0, 0) )

""" 
  class QTransformWithNumpy:
    QTransform Class with utilities for using in Numpy representation
    QTransformクラスにNumpy形式で使うためのユーティリティを実装したクラス
"""
class QTransformWithNumpy(QTransform):
    def __init__(self):
        super(QTransformWithNumpy, self).__init__()
        self.matrix_NumpyFloat32 = np.zeros([3,3], dtype=np.float32)
        self.matrix_NumpyFloat32 = self.inNumpyFloat32()


    def reset(self):
        self.setMatrix(1.0, 0.0, 0.0, \
                       0.0, 1.0, 0.0, \
                       0.0, 0.0, 1.0)

    # function inNumpy(): returns QTransform in numpy.float32 representation
    def inNumpyFloat32(self):
        self.matrix_NumpyFloat32 = np.float32([[self.m11(), self.m12(), self.m13()], \
                                               [self.m21(), self.m22(), self.m23()], \
                                               [self.m31(), self.m32(), self.m33()]] )
        return self.matrix_NumpyFloat32

    # function
    def setMatrixInNumpy(self, matrix):
        if matrix.shape == (3,3):
            self.setMatrix( matrix[0,0], matrix[1,0], matrix[2,0], \
                            matrix[0,1], matrix[1,1], matrix[2,1], \
                            matrix[0,2], matrix[1,2], matrix[2,2]  )


def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = MyWindow()
    window.resize(800,600)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()


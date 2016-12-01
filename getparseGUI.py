# -*- coding: utf-8 -*-

# getparseGUI.py
# homography transform in Qt GUI

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle('getparseGUI window')

        # Window Object
        self.widget = QWidget(self)

        # Widget Object
        self.inputwidget = ImageInputWidget(self)
        self.canvaswidget = CanvasWidget(self)

        # Layout Object
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.inputwidget)
        self.layout.addWidget(self.canvaswidget)

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

    pointedItems   = []
    capturingItems = []
    capturingItem  = None

    x_origin, y_origin = None, None

    def __init__(self, parent=None):
        super(CanvasView, self).__init__(parent)
        self.scene = CanvasScene(self)
        self.setScene(self.scene)

        self.setMouseTracking(True)

    # called if FileAddButton pressed
    def imageFileAdd(self, filepath):
        transformableImageItem = TransformableImage(filepath)
        transformableImageItem.setFlags( \
                QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(transformableImageItem)
        self.imageItems.append(transformableImageItem)

    def mouseMoveEvent(self, event):
        #if self.isPressed == True:
        #    self.isDragged = True

        #if self.capturingItem is not None:
        #    print self.capturingItem.parentItem()
        #    return

        super(CanvasView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        #self.isPressed = True

        #self.pointedItems =  self.items(event.pos())
        #for pointedItem in self.pointedItems:
        #    if type(pointedItem) == QGraphicsRectItem:
        #        self.capturingItem = pointedItem
        #        return

        super(CanvasView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        #isPressed = False
        #isDragged = False
        #self.capturingItem = None
        super(CanvasView, self).mouseReleaseEvent(event)

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CanvasScene, self).__init__(parent)

    def addImage(self, filepath):
        pass

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

        # Create an boundary polygon
        self.imageShape = self.imageItem.shape()
        self.imagePolygon = self.imageShape.toFillPolygon()
        self.boundary  = QGraphicsPolygonItem(self.imagePolygon, self)

        self.corners = [self.imagePolygon.at(i) for i in range(0, self.imagePolygon.count())]
        self.anchors = [None for i in range(0,4)]

        # Create four corner anchors(draggable) and add to self.anchors
        self.anchors[0] = QGraphicsRectItem( \
                self.corners[0].x()-5, self.corners[0].y()-5, 10, 10, self)
        self.anchors[1] = QGraphicsRectItem( \
                self.corners[1].x()-5, self.corners[1].y()-5, 10, 10, self)
        self.anchors[2] = QGraphicsRectItem( \
                self.corners[2].x()-5, self.corners[2].y()-5, 10, 10, self)
        self.anchors[3] = QGraphicsRectItem( \
                self.corners[3].x()-5, self.corners[3].y()-5, 10, 10, self)

        # Style anchors
        for anchor in self.anchors:
            anchor.setPen( QColor(0, 0, 0) )
            anchor.setBrush( QColor(255, 255, 255) )

    def mouseMoveEvent(self, event):
        super(TransformableImage, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.isPressed = True
        self.capturingItems = []
        super(TransformableImage, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(TransformableImage, self).mouseReleaseEvent(event)

    # Move one anchor point to offset value
    def moveAnchor(anchorItem, point):
        pass

#    def hoverEnterEvent(self, event):
#        super(hoverEnterEvent, self).hoverEnterEvent(event)
#        self.imagePolygon.setPen( QColor(255, 0, 0) )
#
#    def hoverLeaveEvent(self, event):
#        super(hoverLeaveEvent, self).hoverLeaveEvent(event)
#        self.imagePolygon.setPen( QColor(0, 0, 0) )


def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = MyWindow()
    window.resize(800,600)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()


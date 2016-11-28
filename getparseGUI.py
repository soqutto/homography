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

    imageitems = []

    def __init__(self, parent=None):
        super(CanvasView, self).__init__(parent)
        self.scene = CanvasScene(self)
        self.setScene(self.scene)

        self.setMouseTracking(True)

    # called if FileAddButton pressed
    def imageFileAdd(self, filepath):
        pixmap = QPixmap(filepath)
        item = self.scene.addPixmap(pixmap)
        self.imageitems.append(item)

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CanvasScene, self).__init__(parent)

    def addImage(self, filepath):
        pass

#class TransformableImage(QPixmap):

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = MyWindow()
    window.resize(800,600)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()


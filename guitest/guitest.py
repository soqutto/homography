# -*- coding: utf-8 -*-

# guitest.py
# Qt with Python GUI testing program

# reference: http://myenigma.hatenablog.com/entry/2016/01/24/113413

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle('QtSampleCrossPointer')
        #self.installEventFilter(self)

    #def eventFilter(self, object, event):
    #    if event.type() == QEvent.HoverMove:
    #        mousePosition = event.pos()
    #        print mousePosition
    #        return True
    #    else:
    #        return False

class MyCanvas(QGraphicsView):
    isPressed = False
    isDragged = False

    def __init__(self, parent=None):
        super(MyCanvas, self).__init__(parent)
        self.parent = parent
        self.pos = None
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.lineItems = []
        self.rectItems = []
        self.capturingItems = None
        self.capturingItem = None

        self.pen = QPen(QColor(0xFF,0x00,0x00))

    def mouseMoveEvent(self, event):
        x, y = event.x(), event.y()

        if self.isPressed == True:
            self.isDragged = True

        if self.isDragged == True:
            if self.capturingItem is not None:
                for (i,rect) in enumerate(self.rectItems):
                    if rect is self.capturingItem:
                        self.scene.removeItem(rect)
                        del(self.rectItems[i])
                rect = self.scene.addRect(x-10, y-10, 20, 20)
                self.rectItems.append(rect)
                self.capturingItem = rect
        else: #self.isDragged == False:
            pass



        # 十字マウスポインタ
        for line in self.lineItems:
            self.scene.removeItem(line)
        self.lineItems = []

        h, w = self.parent.height(), self.parent.width()
        lineH = self.scene.addLine(0, y, w, y)
        lineV = self.scene.addLine(x, 0, x, h)

        self.lineItems.append(lineH)
        self.lineItems.append(lineV)

    def mousePressEvent(self, event):
        self.isPressed = True
        self.capturingItem = None
        self.capturingItems = self.scene.items(event.pos())
        for element in self.capturingItems:
            if type(element) == QGraphicsRectItem:
                self.capturingItem = element
        print self.capturingItems
        print self.capturingItem

    def mouseReleaseEvent(self, event):
        x, y = event.x(), event.y()
        if self.isDragged == True:
            self.isPressed = False
            self.isDragged = False
        else: #self.isDragged == False: 
            rect = self.scene.addRect(x-10, y-10, 20, 20)
            self.rectItems.append(rect)
            self.isPressed = False

class MyRect(QRect):
    def __init__(self):
        super(MyRect, self).__init__()

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    #app.setOverrideCursor(QCursor(Qt.CrossCursor))
    window = MyWindow()
    window.resize(640,480)
    canvas = MyCanvas(window)
    canvas.setMouseTracking(True)
    window.setCentralWidget(canvas)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

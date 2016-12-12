# -*- coding: utf-8 -*-

# findHomographyImage.py
# Definition of Image Set Class

import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gc

class MyImage:
    def __init__(self, filepath=None):
        # MyImage.bitmap: numpy.ndarray(BGR, uint8)
        self.bitmap = None
        self.bitmap_gray = None
        # Image in QImage representation
        self.bitmap_qImg = None
        # Image in QPixmap representation
        self.bitmap_qPix = None

        # Image Slicing Polygon(/Rectangle)
        self.imagePolygon = None
        self.slicePolygon = None #QPolygonF
        self.maskPolygon = None

        # sliced image data for each representation
        self.bitmap_sliced = None
        self.bitmap_sliced_gray = None
        self.bitmap_qImg_sliced = None
        self.bitmap_qPix_sliced = None

        # Specify PixmapItem in GUI
        self.pixmapItem = None

        if filepath is not None:
            self.readFile(filepath)

    def readFile(self, filepath):
        self.bitmap = cv2.imread(filepath)
        self.setImagePolygon()

    def reset(self):
        del(self.bitmap)
        del(self.bitmap_gray)
        del(self.bitmap_qImg)
        del(self.bitmap_qPix)
        del(self.imagePolygon)
        del(self.slicePolygon)
        del(self.maskPolygon)
        del(self.bitmap_sliced)
        del(self.bitmap_sliced_gray)
        del(self.bitmap_qImg_sliced)
        del(self.bitmap_qPix_sliced)
        gc.collect()

        self.__init__()

    # Setting polygon for slicing image
    def setSlice(self, polygon, offset=QPointF(0.0, 0.0)):
        if type(polygon) is QPolygonF and polygon.isClosed():
            self.slicePolygon = polygon
        elif type(polygon) is QRectF:
            self.slicePolygon = QPolygonF(polygon)
        else:
            return

        if type(offset) is QPointF:
            for i in range(0, self.slicePolygon.count()):
                self.slicePolygon.replace(i, self.slicePolygon.at(i) + offset)

    # Connect to PixmapItem on GUI
    def setPixmapItem(self, item):
        self.pixmapItem = item

    # Return image's shape: (x, y)
    def shape(self):
        if type(self.bitmap) is np.ndarray:
            return (self.bitmap.shape[1], self.bitmap.shape[0])
        else:
            return (None, None)

    # Setting up ImagePolygon by Image's shape rectangle
    # Using in subtract mask area
    def setImagePolygon(self):
        x, y = self.shape()
        if (x is not None) and (y is not None):
            self.imagePolygon = QPolygonF( QRectF(0, 0, x, y) )

    # Get raw image data in numpy.ndarray representation
    def getInNumpy(self, gray=False):
        if gray is True:
            self.bitmap_gray = cv2.cvtColor(self.bitmap, cv2.COLOR_BGR2GRAY)
            return self.bitmap_gray
        else:
            return self.bitmap

    def getInQImage(self):
        tempImage = cv2.cvtColor(self.bitmap, cv2.COLOR_BGR2RGB)
        x, y = self.shape()
        self.bitmap_qImg = QImage(tempImage, x, y, QImage.Format_RGB888)

        return self.bitmap_qImg

    def getInQPixmap(self):
        tempPixmap = QPixmap()
        tempPixmap.convertFromImage(self.getInQImage())
        self.bitmap_qPix = tempPixmap

        return self.bitmap_qPix

    # Get sliced image data in numpy.ndarray representation
    def getSlicedInNumpy(self, gray=False):
        self.getSlicedInQImage()
        temp_bitmap = self.bitmap_qImg_sliced.convertToFormat(QImage.Format_RGB888)
        ptr = temp_bitmap.bits()
        ptr.setsize(temp_bitmap.byteCount())
        x, y = self.shape()
        self.bitmap_sliced = np.array(ptr).reshape(y, x, 3)
        self.bitmap_sliced = cv2.cvtColor(self.bitmap_sliced, cv2.COLOR_RGB2BGR)

        if gray is True:
            self.bitmap_sliced_gray = cv2.cvtColor(self.bitmap_sliced, cv2.COLOR_BGR2GRAY)
            return self.bitmap_sliced_gray
        else:
            return self.bitmap_sliced

    # Get sliced image data in QImage representation
    def getSlicedInQImage(self):
        self.maskPolygon = self.imagePolygon.subtracted(self.slicePolygon)
        self.bitmap_qImg_sliced = self.getInQImage().copy()

        painter = QPainter(self.bitmap_qImg_sliced)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0,0,0)))
        painter.drawPolygon(self.maskPolygon)

        return self.bitmap_qImg_sliced

    # Get sliced image data in QPixmap representation
    def getSlicedInQPixmap(self):
        self.getSlicedInQImage()
        tempPixmap = QPixmap()
        tempPixmap.convertFromImage(self.bitmap_qImg_sliced)
        self.bitmap_qPix_sliced = tempPixmap

        return self.bitmap_qPix_sliced


# モジュールとして読み込まれるため単独動作はしない
if __name__ == '__main__':
    pass


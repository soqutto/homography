# -*- coding: utf-8 -*-

# findHomographyImage.py
# Definition of Image Set Class

import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gc

SIZE_MAX_X = 800
SIZE_MAX_Y = 800

class MyImage:
    def __init__(self, data):
        # MyImage.bitmap: numpy.ndarray(BGR, uint8)
        self.bitmap = None
        self.bitmap_gray = None
        # Image in QImage representation
        self.bitmap_qImg = None
        # Image in QPixmap representation
        self.bitmap_qPix = None

        # Image Slicing Polygon(/Rectangle)
        self.imagePolygon = None
        self.slicePolygon = None
        self.maskPolygon = None

        # sliced image data for each representation
        self.bitmap_sliced = None
        self.bitmap_sliced_gray = None
        self.bitmap_qImg_sliced = None
        self.bitmap_qPix_sliced = None

        # Specify PixmapItem in GUI
        self.pixmapItem = None

        if type(data) is str or type(data) is unicode:
            self.readFile(data)
        elif type(data) is np.ndarray:
            self.readFromNdarray(data)
            

    def readFile(self, filepath):
        self.bitmap = cv2.imread(unicode(filepath))
        self.resize()
        self.setImagePolygon()

    def readFromNdarray(self, data):
        self.bitmap = data.copy()
        self.resize()
        self.setImagePolygon()

    def resize(self):
        y, x = self.bitmap.shape[:2]
        if x > SIZE_MAX_X:
            y = y * (SIZE_MAX_X / float(x))
            x = SIZE_MAX_X
        if y > SIZE_MAX_Y:
            x = x * (SIZE_MAX_Y / float(y))
            y = SIZE_MAX_Y

        x, y = int(x), int(y)
        self.bitmap = cv2.resize(self.bitmap, (x, y))


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
        self.bitmap_qImg = QImage(tempImage, x, y, x*tempImage.shape[2], QImage.Format_RGB888)

        return self.bitmap_qImg

    def getInQPixmap(self):
        tempPixmap = QPixmap()
        tempPixmap.convertFromImage(self.getInQImage())
        self.bitmap_qPix = tempPixmap

        return self.bitmap_qPix

    # Get sliced image data in numpy.ndarray representation
    def getSlicedInNumpy(self, gray=False):
        self.getSlicedInQImage()
        temp_bitmap = self.bitmap_qImg_sliced.convertToFormat(QImage.Format_ARGB32)
        ptr = temp_bitmap.constBits()
        ptr.setsize(temp_bitmap.byteCount())
        x, y = self.shape()
        self.bitmap_sliced = np.array(ptr).reshape(y, x, 4)
        self.bitmap_sliced = cv2.cvtColor(self.bitmap_sliced, cv2.COLOR_RGBA2BGR)

        if gray is True:
            self.bitmap_sliced_gray = cv2.cvtColor(self.bitmap_sliced, cv2.COLOR_BGR2GRAY)
            return self.bitmap_sliced_gray
        else:
            return self.bitmap_sliced

    # Get sliced image data in QImage representation
    def getSlicedInQImage(self):
        self.bitmap_qImg_sliced = self.getInQImage().copy()
        if self.slicePolygon is None:
            return self.bitmap_qImg_sliced

        self.maskPolygon = self.imagePolygon.subtracted(self.slicePolygon)
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


# モジュールとして読み込まれるため単独動作はしない
if __name__ == '__main__':
    pass


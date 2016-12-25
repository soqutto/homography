# -*- coding: utf-8 -*-

"""
  Measure.py
    measures line on image
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import cv2
import math

from Image import *
from Matcher import *
from Concatenate import *

class Measure:
    def __init__(self):
        self.originalImage = None
        self.transform = None

        self.Xmmperpx = 0
        self.Ymmperpx = 0

        self.temp = 0

    def setImage(self, myImageObject):
        self.originalImage = myImageObject

    def setPlane(self, polygon):
        nodes = []
        for i in range(0, polygon.count()-1):
            p = polygon.at(i)
            nodes.append([p.x(), p.y()])
        N1 = np.float32(nodes)
        N2 = np.float32([[0,0],[1000,0],[1000,1000],[0,1000]])
        H = cv2.getPerspectiveTransform(N1, N2)
        self.transform = H

    def setKeyMeasureX(self, mm):
        self.Xmmperpx = mm / 1000.0
        print self.Xmmperpx

    def setKeyMeasureY(self, mm):
        self.Ymmperpx = mm / 1000.0
        print self.Ymmperpx

    def isMeasureable(self):
        flag = True
        if self.Xmmperpx == 0:
            flag = False
        if self.Ymmperpx == 0:
            flag = False
        if self.transform is None:
            flag = False

        return flag

    def warpPerspective(self, point):
        if type(point) is QPointF:
            x, y = point.x(), point.y()
            P = cv2.perspectiveTransform(np.float32([[[x, y]]]), self.transform)

            if type(P) is np.ndarray and P.shape == (1, 1, 2):
                return P[0][0]
            else:
                return None

    def measureDistance(self, point1, point2):
        if self.isMeasureable():
            # x, y in real length
            x = abs(point1[0] - point2[0]) * self.Xmmperpx
            y = abs(point1[1] - point2[1]) * self.Ymmperpx
            d = math.sqrt(x ** 2 + y ** 2)
            return d # in (mm) scale
        else:
            return None


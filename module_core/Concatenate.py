# -*- coding: utf-8 -*-

"""
  Concatenate.py
    shape images using homography matrix and composite
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import cv2

from Image import *
from Matcher import *

class Concatenator:
    def __init__(self, im1=None, im2=None, H=None, matchPairs=[]):
        self.image1 = im1 #MyImage Instance
        self.image2 = im2 #MyImage Instance

        self.transform = H
        self.matches = matchPairs

        self.dst = None

    def setImage(self, pos=None, img=None):
        if pos is None or img is None:
            print "Concatenator::setImage() parameter missing"
            return
        else:
            if pos == 0:
                self.image1 = img
            elif pos == 1:
                self.image2 = img
            else:
                print "Concatenator::setImage() parameter missing"
                return

    def setTransform(self, H):
        self.transform = H

    def setMatchPairs(self, matchPairs):
        self.matches = matchPairs

    def concatenate(self):
        X, Y, cnt = 0, 0, 0
        x1, y1 = self.image1.shape()
        x2, y2 = self.image2.shape()

        for MatchPair in self.matches:
            if MatchPair.isAccepted():
                X += abs(MatchPair.point1[0] - MatchPair.point2[0])
                Y += abs(MatchPair.point1[1] - MatchPair.point2[1])
                cnt += 1

        if cnt == 0:
            return

        X = int(round(X / cnt))
        Y = int(round(Y / cnt))

        sX = int(round(x2 + X * 1.25))
        sY = int(round(y2 + Y * 1.25))

        im1 = self.image1.getInNumpy()
        warpedImage = cv2.warpPerspective(self.image2.getInNumpy(), self.transform, (int(x2+X*1.25), int(y2+Y*1.25)))

        for i in xrange(x1):
            for j in xrange(y1):
                warpedImage[j, i] = im1[j, i]

        self.dst = MyImage(warpedImage)
        self.dst.getInQImage().save("debug.png")

        return self.dst


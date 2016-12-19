# -*- coding: utf-8 -*-

"""
  Concatenate.py
    shape images using homography matrix and composite
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import cv2


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
        x1, y1 = im1.shape()
        x2, y2 = im2.shape()
        warpedImage = MyImage( \
                cv2.warpPerspective(self.image1.getInNumpy(gray=True), self.transform, (x2, y2)) )

        self.dst = warpedImage


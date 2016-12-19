# -*- coding: utf-8 -*-

# findHomographyMatcher.py
# class definition

import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gc

class MyMatcher:
    def __init__(self, method='SIFT', desc='BRIEF', matcher='BruteForce-Hamming'):

        # Create Instances (Init)
        self.detector = None
        self.descriptor = None
        self.matcher = None

        # Create Keypoint Detector
        self.setDetectorType(method)

        # Create Keypoint Descriptor
        self.setDescriptorType(desc)

        # Create Keypoint Matcher
        self.setMatcherType(matcher)

    def setDetectorType(self, method_type):
        if method_type == 'SIFT':
            self.detector = cv2.FeatureDetector_create('SIFT')
        elif method_type == 'SURF':
            self.detector = cv2.FeatureDetector_create('SURF')
        else:
            sys.exit("Error: Unknown Keypoint Type.")

    def setDescriptorType(self, descriptor_type):
        if descriptor_type == 'SIFT':
            self.descriptor = cv2.DescriptorExtractor_create('SIFT')
        elif descriptor_type == 'SURF':
            self.descriptor = cv2.DescriptorExtractor_create('SURF')
        elif descriptor_type == 'BRIEF':
            self.descriptor = cv2.DescriptorExtractor_create('BRIEF')
        elif descriptor_type == 'BRISK':
            self.descriptor = cv2.DescriptorExtractor_create('BRISK')
        elif descriptor_type == 'ORB':
            self.descriptor = cv2.DescriptorExtractor_create('ORB')
        elif descriptor_type == 'FREAK':
            self.descriptor = cv2.DescriptorExtractor_create('FREAK')
        else:
            sys.exit("Error: Unknown Keypoint-Descriptor Type.")

    def setMatcherType(self, matcher_type):
        if matcher_type == 'BruteForce-Hamming':
            self.matcher = cv2.DescriptorMatcher_create('BruteForce-Hamming')
        elif matcher_type == 'BruteForce-Hamming(2)':
            self.matcher = cv2.DescriptorMatcher_create('BruteForce-Hamming(2)')
        elif matcher_type == 'BruteForce-L1':
            self.matcher = cv2.DescriptorMatcher_create('BruteForce-L1')
        elif matcher_type == 'BruteForce-SL2':
            self.matcher = cv2.DescriptorMatcher_create('BruteForce-SL2')
        elif matcher_type == 'FlannBased':
            self.matcher = cv2.DescriptorMatcher_create('FlannBased')
        else:
            sys.exit("Error: Unknown Keypoint-Matcher Type.")

    def detect(self, grayscale):
        kp = self.detector.detect(grayscale)
        return kp

    def compute(self, grayscale, keypoint):
        keyp, desc_value = self.descriptor.compute(grayscale, keypoint)
        return (keyp, desc_value)

    def match(self, descriptor1, descriptor2):
        matches = self.matcher.match(descriptor1, descriptor2)
        return matches

    def knnMatch(self, descriptor1, descriptor2, k=2):
        matches = self.matcher.knnMatch(descriptor1, descriptor2, k)
        return matches


class MatchingProcessor:
    def __init__(self, myImage1=None, myImage2=None):
        self.im1, self.im2 = myImage1, myImage2
        self.kp1, self.kp2 = None, None
        self.k1 , self.k2  = None, None
        self.d1 , self.d2  = None, None
        self.matches = []
        self.matchesKNN = []
        self.matchPairs = []

        self.matchCompleteFlag = False

        self.matcher = MyMatcher()
        self.H = None

    def clean(self):
        if self.matchCompleteFlag == True:
            del(self.kp1)
            del(self.kp2)
            del(self.k1)
            del(self.k2)
            del(self.d1)
            del(self.d2)
            del(self.matches)
            del(self.matchesKNN)
            del(self.matchPairs)
            self.__init__(self.im1, self.im2)

    def setImage(self, pos, myImage):
        if pos == 0:
            self.im1 = myImage
        elif pos == 1:
            self.im2 = myImage

    def detect(self):
        self.kp1 = self.matcher.detect(self.im1.getSlicedInNumpy(gray=True))
        self.kp2 = self.matcher.detect(self.im2.getSlicedInNumpy(gray=True))

    def compute(self):
        self.k1, self.d1 = \
                self.matcher.compute(self.im1.getSlicedInNumpy(gray=True), self.kp1)
        self.k2, self.d2 = \
                self.matcher.compute(self.im2.getSlicedInNumpy(gray=True), self.kp2)

    def match(self):
        self.matches = self.matcher.match(self.d1, self.d2)

    def knnMatch(self, k=2):
        if k >= 2:
            self.matchesKNN = self.matcher.knnMatch(self.d1, self.d2, k)

    def nndr(self, ratio=1.0):
        for m in self.matchesKNN:
            if m[0].distance < m[1].distance * ratio:
                self.matches.append(m[0])

    def extractMatches(self):
        self.matchPairs = [MatchPair( \
                np.float32([self.k1[m.queryIdx].pt[0], self.k1[m.queryIdx].pt[1]]), \
                np.float32([self.k2[m.trainIdx].pt[0], self.k2[m.trainIdx].pt[1]]), \
                m.distance) for m in self.matches]

    # threshold: real value
    def distanceCutOff(self, threshold):
        for (i, m) in enumerate(self.matchPairs):
            if m.distance > threshold:
                del(self.matchPairs[i])

    # threshold: percentage(0-1 float)
    def YCutOff(self, threshold):
        y1, y2 = self.im1.shape()[1], self.im2.shape()[1]
        y = y1 if y1 > y2 else y2

        for (i, m) in enumerate(self.matchPairs):
            if abs(m.point1[1] - m.point2[1]) > threshold * y:
                del(self.matchPairs[i])

    def calculateHomography(self):
        self.H, Hstatus = cv2.findHomography( \
                np.float32([m.point2 for m in self.matchPairs]), \
                np.float32([m.point1 for m in self.matchPairs]), \
                cv2.RANSAC)

        for (i, stat) in enumerate(Hstatus):
            if stat == [0]:
                self.matchPairs[i].disable()

    def rehashHomography(self):
        self.H, _ = cv2.findHomography( \
                np.float32([m.point2 for m in matchPairs if m.isAccepted()]), \
                np.float32([m.point1 for m in matchPairs if m.isAccepted()]))
    
    def drawMatch(self):
        self.im1.pixmapItem.deleteAllMatchingPoint()
        self.im2.pixmapItem.deleteAllMatchingPoint()
        for match in self.matchPairs:
            self.im1.pixmapItem.addMatchingPoint(match.point1[0], match.point1[1])
            self.im2.pixmapItem.addMatchingPoint(match.point2[0], match.point2[1])

        self.matchCompleteFlag = True

    def deleteAllMatches(self):
        self.im1.pixmapItem.deleteAllMatchingPoint()
        self.im2.pixmapItem.deleteAllMatchingPoint()
        self.clean()



class MatchPair:
    def __init__(self, p1, p2, d, stat=[1]):
        self.point1 = p1
        self.point2 = p2
        self.distance = d
        self.inlier = stat[0]

    def isAccepted(self):
        if self.inlier == 1:
            return True
        else:
            return False

    def enable(self):
        self.inlier = 1

    def disable(self):
        self.inlier = 0

    def setPoint(self, index, x=None, y=None):
        # その対応の座標位置を強制的に書き換える
        # index == 1でpoint1を, index == 2でpoint2を書き換える
        if index == 1:
            p = self.point1
        elif index == 2:
            p = self.point2
        else:
            return

        if x is not None:
            p[0] = x
        if y is not None:
            p[1] = y

    def setPointByOffset(self, index, x=None, y=None):
        # その対応の座標位置を強制的に書き換える
        # setPointの指定方法の代わりに差分(移動量)を用いる
        if index == 1:
            p = self.point1
        elif index == 2:
            p = self.point2
        else:
            return

        if x is not None:
            p[0] += x
        if y is not None:
            p[1] += y


# モジュールとして読み込まれるため単独動作はしない
if __name__ == '__main__':
    pass



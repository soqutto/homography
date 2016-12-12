# -*- coding: utf-8 -*-

# findHomographyMatcher.py
# class definition

import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

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

    def setDetectorType(method_type):
        if method_type == 'SIFT':
            self.detector = cv2.FeatureDetector_create('SIFT')
        elif method_type == 'SURF':
            self.detector = cv2.FeatureDetector_create('SURF')
        else:
            sys.exit("Error: Unknown Keypoint Type.")

    def setDescriptorType(descriptor_type):
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

    def setMatcherType(matcher_type):
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

    def detect(grayscale):
        kp = self.detector.detect(grayscale)
        return kp

    def compute(grayscale, keypoint):
        keyp, desc_value = self.descriptor.compute(grayscale, keypoint)
        return (keyp, desc_value)

    def match(descriptor1, descriptor2):
        matches = self.matcher.match(descriptor1, descriptor2)
        return matches

    def knnMatch(descriptor1, descriptor2, k=2):
        matches = self.matcher.knnMatch(descriptor1, descriptor2, k)
        return matches

class MatchingSet:
    def __init__(self, myImage1, myImage2):
        self.kp1, self.kp2 = None, None
        self.k1 , self.k2  = None, None
        self.d1 , self.d2  = None, None
        self.matches = None
        self.matchPairs = []

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
        # setPointの指定方法の代わりに差分を用いる
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



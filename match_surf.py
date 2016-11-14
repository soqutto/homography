# -*- coding: utf-8 -*-

import cv2
import numpy as np
import sys
import random

im1_pth = 'images/parkaxis/s-IMG_4562.jpg'
im2_pth = 'images/parkaxis/s-IMG_4564.jpg'

im1_pth = 'images/flowerheights/100067843309_9o.jpg'
im2_pth = 'images/flowerheights/100067843309_8o.jpg'

im1 = cv2.imread(im1_pth, 0)
im2 = cv2.imread(im2_pth, 0)

#im1 = cv2.imread('images/IMG_5894.JPG', cv2.CV_LOAD_IMAGE_GRAYSCALE)
#im2 = cv2.imread('images/IMG_5895.JPG', cv2.CV_LOAD_IMAGE_GRAYSCALE)

im1 = cv2.resize(im1, (640, 480))
im2 = cv2.resize(im2, (640, 480))

imcat = cv2.hconcat([im1, im2])

detector = cv2.FeatureDetector_create("SURF")
descriptor = cv2.DescriptorExtractor_create("BRIEF")
matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")

kp1 = detector.detect(im1)
kp2 = detector.detect(im2)

print "Keypoints in im1: {0}, im2: {1}".format(len(kp1), len(kp2))

k1, d1 = descriptor.compute(im1, kp1)
k2, d2 = descriptor.compute(im2, kp2)

print "Keypoints in im1: {0}, im2: {1}".format(len(d1), len(d2))

matches = matcher.match(d1, d2)

print "matches: {0}".format(len(matches))

dist = [m.distance for m in matches]

# 平均値
threshold_dist = sum(dist)/len(dist) * 0.9

# 振るいかけ
sel_matches = [m for m in matches if m.distance < threshold_dist]

print "distance_min: %.3f" % min(dist)
print "distance_mean: %.3f" % (sum(dist)/len(dist))
print "distance_max: %.3f" % max(dist)

# (x,y)
print "selected matches: {0}".format(len(sel_matches))

print("len(k1):", len(k1))
print("len(k2):", len(k2))

point1 = [[k1[m.queryIdx].pt[0], k1[m.queryIdx].pt[1]] for m in sel_matches]
point2 = [[k2[m.trainIdx].pt[0], k2[m.trainIdx].pt[1]] for m in sel_matches]

point1 = np.array(point1)
point2 = np.array(point2)

im1 = cv2.imread(im1_pth)
im2 = cv2.imread(im2_pth)

im1 = cv2.resize(im1, (640, 480))
im2 = cv2.resize(im2, (640, 480))

imcat = cv2.hconcat([im1, im2])

cv2.namedWindow('result')
cv2.imshow('result', imcat)

for (p1, p2) in zip(point1, point2):
    color = tuple([random.randint(0,255) for i in (0,1,2)])
    origin = tuple(map(int, [p1[0], p1[1]]))
    terminal = tuple(map(int, [p2[0]+im2.shape[1], p2[1]]))
    print p1, p2
    cv2.line(imcat, origin, terminal, color)
    cv2.imshow('result', imcat)
    k = cv2.waitKey(0) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

 

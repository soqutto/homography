#!/usr/bin/python
# -*- coding: utf-8 -*-

# ref: http://authorunknown408.blog.fc2.com/blog-entry-38.html

import cv2
import sys
import numpy

im1_pth = 'images/labo/IMG_5894.jpg'
im2_pth = 'images/labo/IMG_5895.jpg'

im1_pth = 'images/flowerheights/100067843309_ro.jpg'
im2_pth = 'images/flowerheights/100067843309_7o.jpg'
#im2_pth = 'images/result.jpg'

im1 = cv2.imread(im1_pth, cv2.CV_LOAD_IMAGE_GRAYSCALE)
im2 = cv2.imread(im2_pth, cv2.CV_LOAD_IMAGE_GRAYSCALE)

#im1 = cv2.resize(im1, (1024,768))
#im2 = cv2.resize(im2, (1024,768))

detector = cv2.FeatureDetector_create("SURF")
descriptor = cv2.DescriptorExtractor_create("BRIEF")
matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")

# detect keypoints
kp1 = detector.detect(im1)
kp2 = detector.detect(im2)

print "#keypoints in image1: {0}, image2: {1}".format(len(kp1), len(kp2))

# descriptors
k1, d1 = descriptor.compute(im1, kp1)
k2, d2 = descriptor.compute(im2, kp2)

print "#keypoints in image1: {0}, image2: {1}".format(len(d1), len(d2))

# match the keypoints
matches = matcher.match(d1, d2)

# visualize the matches
print "#matches:", len(matches)
dist = [m.distance for m in matches]

print "distance_min: %.3f" % min(dist)
print "distance_mean: %.3f" % (sum(dist)/len(dist))
print "distance_max: %.3f" % max(dist)

# threshold: half the mean
thres_dist = (sum(dist) / len(dist)) * 0.9

# keep only the reasonable matches
sel_matches = [m for m in matches if m.distance < thres_dist]

print "#selected matches:", len(sel_matches)

point1 = [[k1[m.queryIdx].pt[0], k1[m.queryIdx].pt[1]] for m in sel_matches]
point2 = [[k2[m.trainIdx].pt[0], k2[m.trainIdx].pt[1]] for m in sel_matches]

point1 = numpy.array(point1)
point2 = numpy.array(point2)

H, Hstatus = cv2.findHomography(point2, point1, cv2.RANSAC)

# 移動量を算出
x = 0
y = 0
cnt = 0
for i,v in enumerate(Hstatus):
    if v == 1:
        x += point1[i][0] - point2[i][0]
        y += point1[i][1] - point2[i][1]
        cnt += 1

# カラー画像として改めて読み込む
im1 = cv2.imread(im1_pth)
im2 = cv2.imread(im2_pth)
#im1 = cv2.resize(im1, (1024,768))
#im2 = cv2.resize(im2, (1024,768))

x = abs(int(round(x/cnt)))
y = abs(int(round(y/cnt)))

# sizeを取得
h1, w1 = im1.shape[:2]
h2, w2 = im2.shape[:2]

dst = cv2.warpPerspective(im2, H, (w2+x, h2+y))

for i in xrange(w1):
    for j in xrange(h1):
        dst[j,i] = im1[j,i]

cv2.imshow("result", dst)
cv2.waitKey()





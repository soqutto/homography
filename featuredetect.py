# -*- coding: utf-8 -*-

import cv2
import numpy as np

# グレースケール画像を読み込む
im1 = cv2.imread('images/IMG_5894.JPG', 0)

im1_gray = cv2.resize(im1, (800,600))

# SIFT detector
sift = cv2.SIFT()
kp_sift, des_sift = sift.detectAndCompute(im1_gray, None)


# SURF detector
surf = cv2.SURF()
surf.hessianThreshold = 1000
kp_surf, des_surf = surf.detectAndCompute(im1_gray, None)

# FAST detector
fast = cv2.FastFeatureDetector()
kp_fast = fast.detect(im1_gray, None)

print "keypoints(sift): {0}".format(len(kp_sift))
print "keypoints(surf): {0}".format(len(kp_surf))
print "surf.hessianThreshold: {0}".format(surf.hessianThreshold)
print "keypoints(fast): {0}".format(len(kp_fast))

im_result_sift = cv2.drawKeypoints(im1_gray, kp_sift, None, (255,0,0), 4)
im_result_surf = cv2.drawKeypoints(im1_gray, kp_surf, None, (255,0,0), 4)
#im_result_fast = cv2.drawKeypoints(im1_gray, kp_fast, color=(0,0,255))
cv2.imshow('image_sift', im_result_sift)
cv2.imshow('image_surf', im_result_surf)
#cv2.imshow('image_fast', im_result_fast)
cv2.waitKey(0)
cv2.destroyAllWindows()


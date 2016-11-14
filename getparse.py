# -*- coding: utf-8 -*-
# getparse.py
# ホモグラフィ変換スクリプト
import numpy as np
import cv2

img = cv2.imread('images/flowerheights/100067843309_7o.jpg')

vertices_src = np.float32([[81,232],[289,251],[288,363],[77,364]])
vertices_dst = np.float32([[305,280],[519,260],[517,397],[302,388]])

homography = cv2.getPerspectiveTransform(vertices_src, vertices_dst)

dsize = (1000,2000)

img_proc = cv2.warpPerspective(img, homography, dsize)

cv2.imshow('img', img)
cv2.imshow('img_proc', img_proc)
while(1):
    k = cv2.waitKey(0) & 0xFF
    if k == 27: # [Esc] Key
        break

cv2.imwrite('images/result.jpg', img_proc)
cv2.destroyAllWindows()


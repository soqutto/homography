#!/usr/bin/python
# -*- coding: utf-8 -*-

# reference: http://authorunknown408.blog.fc2.com/blog-entry-38.html

import cv2
import numpy as np
import sys
import os.path
#import random

# リサイズ時の最大サイズ定義
IMAGE_MAX_XSIZE = 800
IMAGE_MAX_YSIZE = 1000

# MyMatchクラス
# マッチング点対をクラスとして再定義

class MyMatch:
    def __init__(self, point1, point2, distance, inlier):
        # コンストラクタ
        # 引数: 点1, 点2, 距離, インライア
        self.point1 = point1
        self.point2 = point2
        self.distance = distance
        self.inlier = inlier[0]

    def isAccepted(self):
        # その対応についてインライアを真偽値で返す
        if self.inlier == 1:
            return True
        else:
            return False

    def enable(self):
        # その対応について強制的に有効(インライア)にする
        self.inlier = 1

    def disable(self):
        # その対応について強制的に無効(アウトライア)にする
        self.inlier = 0



# リサイズの計算
# 縦は1000, 横は800が最大
def compute_resize(image):
    y, x = image.shape[:2]
    if x > IMAGE_MAX_XSIZE:
        y = y * (IMAGE_MAX_XSIZE / float(x))
        x = IMAGE_MAX_XSIZE
    if y > IMAGE_MAX_YSIZE:
        x = x * (IMAGE_MAX_YSIZE / float(y))
        y = IMAGE_MAX_YSIZE

    return (int(x), int(y))


# トリミング関数
def image_trim(image, p1, p2):
    return image[p1[1]:p2[1], p1[0]:p2[0]]

# パノラマ合成関数
def composite_panorama(im1, im2, method='SURF', desc='BRIEF', matcher='BruteForce-Hamming', threshold_ratio=1.0):
    # 画像のモノクロ化
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # キーポイント検出器生成
    if method == 'SURF':
        # SURF検出器生成
        detector = cv2.FeatureDetector_create("SURF")
        print "### Keypoint mode: SURF"
    elif method == 'SIFT':
        # SIFT検出器生成
        detector = cv2.FeatureDetector_create("SIFT")
        print "### Keypoint mode: SIFT"
    else:
        sys.exit("Unknown Keypoint")

    # ディスクリプタ生成
    if desc == 'BRIEF':
        descriptor = cv2.DescriptorExtractor_create("BRIEF")
        print "### Descriptor mode: BRIEF"
    elif desc == 'SIFT':
        descriptor = cv2.DescriptorExtractor_create("SIFT")
        print "### Descriptor mode: SIFT"
    elif desc == 'SURF':
        descriptor = cv2.DescriptorExtractor_create("SURF")
        print "### Descriptor mode: SURF"
    elif desc == 'BRISK':
        descriptor = cv2.DescriptorExtractor_create("BRISK")
        print "### Descriptor mode: SIFT"
    elif desc == 'ORB':
        descriptor = cv2.DescriptorExtractor_create("ORB")
        print "### Descriptor mode: ORB"
    elif desc == 'FREAK':
        descriptor = cv2.DescriptorExtractor_create("FREAK")
        print "### Descriptor mode: FREAK"
    else:
        sys.exit("Unknown Descriptor Type")

    # Matcher生成
    if matcher == 'BruteForce-Hamming':
        keypointmatcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
        print "### Keypoint-Matcher mode: BruteForce-Hamming"
    elif matcher == 'BruteForce-L1':
        keypointmatcher = cv2.DescriptorMatcher_create("BruteForce-L1")
        print "### Keypoint-Matcher mode: BruteForce-L1"
    elif matcher == 'BruteForce-SL2':
        keypointmatcher = cv2.DescriptorMatcher_create("BruteForce-SL2")
        print "### Keypoint-Matcher mode: BruteForce-SL2"
    elif matcher == 'BruteForce-Hamming(2)':
        keypointmatcher = cv2.DescriptorMatcher_create("BruteForce-Hamming(2)")
        print "### Keypoint-Matcher mode: BruteForce-Hamming(2)"
    elif matcher == 'FlannBased':
        keypointmatcher = cv2.DescriptorMatcher_create("FlannBased")
        print "### Keypoint-Matcher mode: FlannBased"
    else:
        sys.exit("Unknown Keypoint-Matcher type")

    # detect keypoints
    kp1 = detector.detect(im1_gray)
    kp2 = detector.detect(im2_gray)

    # descriptors
    k1, d1 = descriptor.compute(im1_gray, kp1)
    k2, d2 = descriptor.compute(im2_gray, kp2)
    
    # match the keypoints
    matches = keypointmatcher.match(d1, d2)

    print "#keypoints in image1: {0}, image2: {1}".format(len(k1), len(k2))
    print "#keypoints in image1: {0}, image2: {1}".format(len(d1), len(d2))
    print "#matches:", len(matches)
    dist = [m.distance for m in matches]
    
    print "distance_min: %.3f" % min(dist)
    print "distance_mean: %.3f" % (sum(dist)/len(dist))
    print "distance_max: %.3f" % max(dist)
    
    # threshold: half the mean
    thres_dist = (sum(dist) / len(dist)) * threshold_ratio
    
    # keep only the reasonable matches
    sel_matches = [m for m in matches if m.distance < thres_dist]
    print "#threshold ratio: %.3f" % threshold_ratio
    print "#threshold distance: %.3f" % thres_dist
    print "#selected matches: %d" % len(sel_matches)
    if len(sel_matches) <= 4:
        return (None, None)

    # マッチングされた点の抽出(しきい値処理済み)
    point1 = [[k1[m.queryIdx].pt[0], k1[m.queryIdx].pt[1]] for m in sel_matches]
    point2 = [[k2[m.trainIdx].pt[0], k2[m.trainIdx].pt[1]] for m in sel_matches]
    dist_table = [m.distance for m in sel_matches]
    
    # マッチング点の範囲絞り込み
    #del_list = []
    #for i in reversed(range(0, len(point1))):
    #    if  point1[i][0] < 220 or \
    #        point1[i][0] > 524 or \
    #        point1[i][1] < 160 or \
    #        point1[i][1] > 557 or \
    #        point2[i][0] <   0 or \
    #        point2[i][0] > 331 or \
    #        point2[i][1] < 100 or \
    #        point2[i][1] > 497:
    #            point1.pop(i)
    #            point2.pop(i)
    #
    #print "#selected matches:", len(point1)
    

    # y座標差が規定を超えるものについて対応を無効とし
    # 対応リストから削除する
    Y_threshold = im1.shape[0] * 0.4
    for i in range(len(point1)-1, -1, -1):
        if abs(point1[i][1] - point2[i][1]) > Y_threshold:
            del point1[i]
            del point2[i]
            dist_table.pop(i)

    print "#selected matches(Y-subtraction over vertices were excluded): %d" % len(point1)

    point1 = np.array(point1)
    point2 = np.array(point2)

    # H: ホモグラフィ行列
    # Hstatus: RANSACにより取捨選択された点のマスク[0,1]
    H, Hstatus = cv2.findHomography(point2, point1, cv2.RANSAC)

    # インライアの数を計算
    num_inliers = np.count_nonzero(Hstatus)

    print "#selected matches(inliers): %d" % num_inliers
    print "#selected matches(outliers): %d" % (len(point1) - num_inliers)

    # MyMatchリストを作成
    matches = [ MyMatch(p1, p2, d, stat) for (p1, p2, d, stat) \
            in zip(point1, point2, dist_table, Hstatus) ]

    # 移動量を算出
    x = 0
    y = 0
    cnt = 0
    for i,v in enumerate(Hstatus):
        if v == 1:
            x += point1[i][0] - point2[i][0]
            y += point1[i][1] - point2[i][1]
            cnt += 1
    
    x = abs(int(round(x/cnt)))
    y = abs(int(round(y/cnt)))
    
    # sizeを取得
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    
    dst = cv2.warpPerspective(im2, H, (w2+x, h2+y))
    
    for i in xrange(w1):
        for j in xrange(h1):
            dst[j,i] = im1[j,i]

    return (dst, matches)
    #return (dst, (point1, point2, dist_table))
    

def draw_match(im1, im2, match_list, m=0, M=255, drawinliers=True):
    imcat = cv2.hconcat([im1, im2])
    hoffset = im1.shape[1]
    dist_max = max([i.distance for i in match_list])

    for p in match_list:
        if p.distance >= m and p.distance <= M:
            if drawinliers == True and p.isAccepted() or drawinliers == False: 
                color_hsv = np.uint8([[(100*(p.distance/float(dist_max)), 255, 255)]])
                color_rgb = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)
                color = tuple(map(int,color_rgb[0,0]))
                origin = tuple(map(int, [p.point1[0], p.point1[1]]))
                terminal = tuple(map(int, [p.point2[0]+hoffset, p.point2[1]]))
                cv2.line(imcat, origin, terminal, color)

    return imcat


def main():
    # 引数の取得
    argc = len(sys.argv)
    argv = sys.argv
    
    # 既定ファイルパス(エディタ実行用)
    #im1_path = 'images/labo/IMG_5894.jpg'
    #im2_path = 'images/labo/IMG_5895.jpg'
    #im1_path = 'images/labo/IMG_5909.jpg'
    #im2_path = 'images/labo/IMG_5927.jpg'
    im1_path = 'images/flowerheights/100067843309_ro.jpg'
    im2_path = 'images/flowerheights/100067843309_7o.jpg'
    
    # コマンドライン入力用(パスが上書きされる)
    if argc == 3:
        im1_path = argv[1]
        im2_path = argv[2]
        if not os.path.isfile(im1_pth) or not os.path.isfile(im2_pth):
            print "given file(s) don't exist."
            sys.exit()

    im1 = cv2.imread(im1_path)
    im2 = cv2.imread(im2_path)
    im1 = cv2.resize(im1, compute_resize(im1))
    im2 = cv2.resize(im2, compute_resize(im2))
    im1 = image_trim(im1, (220,160), (524,557))
    im2 = image_trim(im2, (  0,100), (331,497))

    #dst, match = composite_panorama( \
    #        im1, im2, 'SURF', 'BRIEF', 'BruteForce-Hamming', 1.3)
    #dst2 = draw_match(im1, im2, match)
    #cv2.imwrite("homography.png", dst)
    #cv2.imwrite("matching.png", dst2)


    # マッチングしきい値変化実験イテレータ

    # 画像保存ディレクトリの定義
    os.chdir("experiment/threshold_flower_sift_Ycutoff")

    for i in range(0,30):
        dst, match = composite_panorama( \
             im1, im2, 'SIFT', 'BRIEF', 'BruteForce-Hamming', 0.1+0.1*i)
        if dst is not None:
            dst2 = draw_match(im1, im2, match)
            cv2.imwrite("img-%02d.jpg" % (i+1), dst)
            cv2.imwrite("match-%02d.png" % (i+1), dst2)
            print "write: %s/img-%02d.jpg" % (os.getcwd(), i+1)
            print "write: %s/match-%02d.jpg" % (os.getcwd(), i+1)

    cv2.imwrite("im1.jpg", im1)
    cv2.imwrite("im2.jpg", im2)

    #cv2.imshow("image1", im1)
    #cv2.imshow("image2", im2)
    cv2.imshow("result", dst)
    cv2.imshow("result2", dst2)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()



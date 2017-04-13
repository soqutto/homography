
from resultlog import *
from operator import mul, div

import numpy as np
import matplotlib.pyplot as plt

pct_01_w_2a = sum(l_01_w_2a) / 4.0 / 300
pct_01_w_2b = sum(l_01_w_2b) / 4.0 / 300
pct_01_w_3w = sum(map(div, l_01_w_3w, truth_plane_01)) / 4.0
pct_01_w_3b = sum(l_01_w_3b) / 4.0 / 300

pct_01_s_2a = sum(l_01_s_2a) / 4.0 / 300
pct_01_s_2b = sum(l_01_s_2b) / 4.0 / 300
pct_01_s_3w = sum(map(div, l_01_s_3w, truth_plane_01)) / 4.0
pct_01_s_3b = sum(l_01_s_3b) / 4.0 / 300


pct_02_w_2a = sum(l_02_w_2a) / 4.0 / 300
pct_02_w_2b = sum(l_02_w_2b) / 4.0 / 300
pct_02_w_3w = sum(map(div, l_02_w_3w, truth_plane_02)) / 4.0
pct_02_w_3b = sum(l_02_w_3b) / 4.0 / 300

pct_02_s_2a = sum(l_02_s_2a) / 4.0 / 300
pct_02_s_2b = sum(l_02_s_2b) / 4.0 / 300
pct_02_s_3w = sum(map(div, l_02_s_3w, truth_plane_02)) / 4.0
pct_02_s_3b = sum(l_02_s_3b) / 4.0 / 300


pct_03_w_2a = sum(l_03_w_2a) / 4.0 / 300
pct_03_w_2b = sum(l_03_w_2b) / 4.0 / 300
pct_03_w_3w = sum(map(div, l_03_w_3w, truth_plane_03)) / 4.0
pct_03_w_3b = sum(l_03_w_3b) / 4.0 / 300

pct_03_s_2a = sum(l_03_s_2a) / 4.0 / 300
pct_03_s_2b = sum(l_03_s_2b) / 4.0 / 300
pct_03_s_3w = sum(map(div, l_03_s_3w, truth_plane_03)) / 4.0
pct_03_s_3b = sum(l_03_s_3b) / 4.0 / 300


pct_04_w_2a = sum(l_04_w_2a) / 4.0 / 300
pct_04_w_2b = sum(l_04_w_2b) / 4.0 / 300
pct_04_w_3w = sum(map(div, l_04_w_3w, truth_plane_04)) / 4.0
pct_04_w_3b = sum(l_04_w_3b) / 4.0 / 300

pct_04_s_2a = sum(l_04_s_2a) / 4.0 / 300
pct_04_s_2b = sum(l_04_s_2b) / 4.0 / 300
pct_04_s_3w = sum(map(div, l_04_s_3w, truth_plane_04)) / 4.0
pct_04_s_3b = sum(l_04_s_3b) / 4.0 / 300


pct_05_w_2a = sum(l_05_w_2a) / 4.0 / 300
pct_05_w_2b = sum(l_05_w_2b) / 4.0 / 300
pct_05_w_3w = sum(map(div, l_05_w_3w, truth_plane_05)) / 4.0
pct_05_w_3b = sum(l_05_w_3b) / 4.0 / 300

pct_05_s_2a = sum(l_05_s_2a) / 4.0 / 300
pct_05_s_2b = sum(l_05_s_2b) / 4.0 / 300
pct_05_s_3w = sum(map(div, l_05_s_3w, truth_plane_05)) / 4.0
pct_05_s_3b = sum(l_05_s_3b) / 4.0 / 300

pct_01_s_gp = sum(l_01_s_gp) / 2.0 / truth_plane_01[0]
pct_02_s_gp = sum(l_02_s_gp) / 2.0 / truth_plane_02[1]
pct_03_s_gp = sum(l_03_s_gp) / 2.0 / truth_plane_03[1]
pct_04_s_gp = sum(l_04_s_gp) / 2.0 / truth_plane_04[0]
pct_05_s_gp = sum(l_05_s_gp) / 2.0 / truth_plane_05[1]

print (pct_01_s_gp+pct_04_s_gp)/ 2.0
print (pct_02_s_gp+pct_03_s_gp+pct_05_s_gp) / 3.0

w_x1 = [1,2,3,4,5]
w_x2 = [1,2,3,4,5]
w_x3 = [1,2,3,4,5]
w_x4 = [1,2,3,4,5]

w_y1 = [pct_01_w_2a, pct_02_w_2a, pct_03_w_2a, pct_04_w_2a, pct_05_w_2a]
w_y2 = [pct_01_w_2b, pct_02_w_2b, pct_03_w_2b, pct_04_w_2b, pct_05_w_2b]
w_y3 = [pct_01_w_3w, pct_02_w_3w, pct_03_w_3w, pct_04_w_3w, pct_05_w_3w]
w_y4 = [pct_01_w_3b, pct_02_w_3b, pct_03_w_3b, pct_04_w_3b, pct_05_w_3b]

s_x1 = [1,2,3,4,5]
s_x2 = [1,2,3,4,5]
s_x3 = [1,2,3,4,5]
s_x4 = [1,2,3,4,5]

s_y1 = [pct_01_s_2a, pct_02_s_2a, pct_03_s_2a, pct_04_s_2a, pct_05_s_2a]
s_y2 = [pct_01_s_2b, pct_02_s_2b, pct_03_s_2b, pct_04_s_2b, pct_05_s_2b]
s_y3 = [pct_01_s_3w, pct_02_s_3w, pct_03_s_3w, pct_04_s_3w, pct_05_s_3w]
s_y4 = [pct_01_s_3b, pct_02_s_3b, pct_03_s_3b, pct_04_s_3b, pct_05_s_3b]

fig = plt.figure()
MARKER_SIZE = 50

ax1 = fig.add_subplot(1,2,1)
ax1.grid(True)
ax1.set_title('whole')
ax1.set_xlabel('sample')
ax1.set_ylabel('(estimated size) / (ground truth)')
ax1.scatter(w_x1, w_y1, c='red', s=MARKER_SIZE, marker='<', label='A')
ax1.scatter(w_x2, w_y2, c='blue', s=MARKER_SIZE, marker='>', label='B')
ax1.scatter(w_x3, w_y3, c='green', s=MARKER_SIZE, marker='*', label='C')
ax1.scatter(w_x4, w_y4, c='yellow', s=MARKER_SIZE, marker='h', label='B\'')
ax1.legend(loc='upper left')
plt.ylim([0.8, 1.2])

ax2 = fig.add_subplot(1,2,2)
ax2.grid(True)
ax2.set_title('split')
ax2.set_xlabel('sample')
ax2.set_ylabel('(estimated size) / (ground truth)')
ax2.scatter(s_x1, s_y1, c='red', s=MARKER_SIZE, marker='<', label='A')
ax2.scatter(s_x2, s_y2, c='blue', s=MARKER_SIZE, marker='>', label='B')
ax2.scatter(s_x3, s_y3, c='green', s=MARKER_SIZE, marker='*', label='C')
ax2.scatter(s_x4, s_y4, c='yellow', s=MARKER_SIZE, marker='h', label='B\'')
ax2.legend(loc='upper left')
plt.ylim([0.8, 1.2])

plt.show()
plt.savefig('result.png')


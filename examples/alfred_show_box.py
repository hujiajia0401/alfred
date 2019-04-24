import os

import sys
import numpy as np
from alfred.vis.image.common import get_unique_color_by_id
from alfred.fusion.kitti_fusion import LidarCamCalibData, \
    load_pc_from_file, lidar_pts_to_cam0_frame, lidar_pt_to_cam0_frame
from alfred.fusion.common import draw_3d_box, compute_3d_box, center_to_corner_3d
import cv2

# from 2011_09_26/2011_09_26_drive_0051_sync

img_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), './data/0000000002.png')
v_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), './data/0000000172.bin')

frame_calib = LidarCamCalibData()
frame_calib.T_lidar_to_cam_0 = [-4.069766e-03, -7.631618e-02, -2.717806e-01]
frame_calib.R_lidar_to_cam_0 = [7.533745e-03, -9.999714e-01, -6.166020e-04,
                                1.480249e-02, 7.280733e-04, -9.998902e-01,
                                9.998621e-01, 7.523790e-03, 1.480755e-02]
frame_calib.P_cam_0 = [7.215377e+02, 0.000000e+00, 6.095593e+02, 4.485728e+01,
                       0.000000e+00, 7.215377e+02, 1.728540e+02, 2.163791e-01,
                       0.000000e+00, 0.000000e+00, 1.000000e+00, 2.745884e-03]
frame_calib.Rect_cam_0 = [9.998817e-01, 1.511453e-02, -2.841595e-03,
                          -1.511724e-02, 9.998853e-01, -9.338510e-04,
                          2.827154e-03, 9.766976e-04, 9.999955e-01]
frame_calib.bootstrap()

# here are some SECOND 3d detector predicted result
# format: x, y, z, w, l, h, rotation_y
# KITTI is: x, y, z, h, w, l
# res = [[19.346336, 6.042622, -0.88500285, 1.600879, 3.8648725, 1.4550171, 5.1091743],
#        [29.93538, 1.5939925, -0.7215852, 1.5986736, 3.9108684, 1.4486158, 5.132188],
#        [40.259136, -1.3263291, -0.49155748, 1.5632737, 3.5060253, 1.4809406, 5.0916004],
#        [-4.681837, -6.570671, -1.2175045, 0.5555831, 0.5860929, 1.7398148, 1.001932],
#        [44.961884, 6.4837523, -1.5046263, 1.616607, 3.8675663, 1.4858866, 1.7715162],
#        [0.64804363, 9.268159, -0.9675394, 1.8812318, 4.664515, 2.0319507, 5.0961885],
#        [-18.386389, 28.60111, -1.3757074, 1.6804752, 4.304487, 1.4874152, 2.06815],
#        [11.712319, 15.615373, -0.98922193, 1.7269207, 4.3874264, 1.8423097, 1.8905786],
#        [-16.170248, -41.480247, -0.03097564, 0.686153, 0.6771428, 1.8784987, 0.22216623],
#        [25.267305, 45.637974, -2.197287, 2.0249672, 6.042538, 2.5292294, 1.0557717],
#        [-34.88346, -0.23137291, -2.1260715, 1.6999425, 4.036162, 1.5583847, 4.417797],
#        [-23.926195, 38.775394, -0.7054695, 1.5999469, 3.6549242, 1.5186816, 3.4325807],
#        [-2.1349354, 41.610023, -1.061486, 1.5652899, 3.5885417, 1.4904435, 0.03756565],
#        [-37.84355, 9.966844, -2.0794232, 1.9736364, 5.68608, 2.3399365, -0.5510466],
#        [8.264814, 33.205574, -1.3255441, 0.66961116, 0.7869765, 1.7961475, 3.5903516],
#        [28.852833, 10.282812, -1.0287172, 1.7898955, 4.7827206, 1.9273052, 1.8356056],
#        [-40.51386, 11.45538, -1.4465854, 0.6127639, 0.82885593, 1.7860174, 2.8919942],
#        [45.52217, -44.360752, -0.27851295, 1.9680248, 5.3572354, 2.2599475, 1.3303113],
#        [5.2633886, -27.981445, -0.22103542, 1.5714979, 3.5747764, 1.4712721, 1.3403505],
#        [24.08377, 32.71529, -0.1687476, 0.66240907, 0.75329924, 1.9358437, 1.1187644],
#        [-48.508858, 18.35507, -1.66853, 1.8876363, 4.866377, 2.1564689, -0.60276866],
#        [5.330953, -0.9705932, -1.8973715, 1.6167549, 4.0601134, 1.4391421, 3.4941106],
#        [-2.3959641, 17.38118, 0.11143422, 0.71009207, 0.67894447, 1.8217698, 2.5325458],
#        [-28.052588, -22.133669, 0.12951618, 0.7079723, 0.9623915, 1.8848807, 0.45091885],
#        [48.304996, -38.2871, -0.18393707, 1.8629241, 4.7361383, 2.012711, 4.508177],
#        [-27.806732, 4.885225, -0.93330365, 0.6153931, 0.76756793, 1.8323035, 2.430164],
#        [2.2722428, -7.6006374, -0.4065826, 0.67797977, 0.972077, 1.8399079, 0.2572404],
#        [-10.013947, 20.21774, -2.0035238, 1.7139361, 4.3931947, 1.5490046, 5.134586],
#        [14.573635, 26.88822, -1.6583468, 1.5832527, 3.80545, 1.490011, 0.52612585],
#        [-40.794884, 22.16341, -2.1041782, 0.6467646, 0.89500916, 1.7931361, -0.27015173]]

res = [[12.189727, 4.65575, -1.0090133, 1.6713146, 3.9860756, 1.4752198, 1.4311914],
       [7.0290184, 18.43234, -1.0616484, 1.5949062, 3.7942128, 1.4587526, 0.03434156],
       [9.716782, 18.663864, -1.081424, 1.6270422, 4.0220504, 1.428338, 0.010275014],
       [12.390503, 18.554394, -1.0709403, 1.5716408, 3.8583813, 1.4068353, 0.092568964],
       [9.162392, -3.2395134, -0.9900443, 0.48879692, 1.7805163, 1.780584, 4.7180395],
       [1.5449369, 19.820513, -1.1250883, 1.61444, 4.0291963, 1.4679328, 0.20142984],
       [15.010401, 17.861265, -0.61177015, 1.8016329, 4.52904, 1.9179995, -0.0009133518],
       [0.2915942, 14.302571, -1.6358033, 0.6031256, 1.7338636, 1.693197, 2.0567284],
       [32.58985, 16.622143, -0.9154575, 1.56024, 3.6420622, 1.4507264, 1.5841204],
       [10.96289, 33.31957, -1.8625767, 1.6718575, 4.1056437, 1.5355072, -0.5065325],
       [-20.711775, 12.870968, -1.3916719, 0.6494945, 0.6588189, 1.7635618, 2.878424],
       [-14.706663, 14.144306, -1.4347086, 0.5646943, 1.7102921, 1.7303042, 1.6427889],
       [-34.937218, -32.419926, -1.9705622, 2.0217955, 6.3850527, 2.5362377, 0.9260524],
       [-25.85193, 13.433075, -1.6172849, 0.5029159, 1.7657202, 1.6948656, 1.8433876],
       [-8.7119255, 15.603356, -0.861634, 0.61332655, 1.7866454, 1.7575798, -0.15929039],
       [0.44268692, -31.126797, -1.4658432, 0.6214817, 1.778398, 1.6685283, 2.7185097],
       [-1.3864591, 43.80352, -1.6687126, 1.990596, 5.726587, 2.5764484, 0.53529406],
       [-46.30665, -24.680546, -1.5553175, 0.54056036, 1.8155692, 1.7282323, 1.4364488],
       [-25.206638, 14.19597, -1.6388608, 0.60298264, 0.6539766, 1.7206633, 2.6259918],
       [42.099804, 16.609531, -0.95861834, 1.6101078, 3.805344, 1.5348499, 1.4423454]]

pcs = load_pc_from_file(v_f)
img = cv2.imread(img_f)

# _, coords = lidar_pts_to_cam0_frame(pcs, frame_calib)

# coords = np.transpose(coords)
# print(coords.shape)
# for p in coords:
#     # print(p[:2])
#     cv2.circle(img, (int(p[0]), int(p[1])), 2, (0, 255, 255), -1)

for p in res:
    xyz = np.array([p[: 3]])

    c2d = lidar_pt_to_cam0_frame(xyz, frame_calib)
    if c2d is not None:
        cv2.circle(img, (int(c2d[0]), int(c2d[1])), 3, (0, 255, 255), -1)

    # hwl -> lwh
    lwh = np.array([p[3: 6]])[:, [2, 1, 0]]
    print('lwh: ', lwh)
    r_y = p[6]
    print('r_y: ', r_y)
    # pts3d = center_to_corner_3d(xyz, lwh, origin=(0, 0, 0), axis=2)[0]
    pts3d = compute_3d_box(xyz[0], lwh[0], r_y)

    pts2d = []
    for pt in pts3d:
        coords = lidar_pt_to_cam0_frame(pt, frame_calib)
        if coords is not None:
            pts2d.append(coords[:2])
    pts2d = np.array(pts2d)
    draw_3d_box(pts2d, img)

cv2.imshow('rr', img)
cv2.waitKey(0)

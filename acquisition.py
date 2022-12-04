import cv2
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors
import networkx as nx
import numpy as np


def get_key_points(image_name, nb_points):
    # open image & convert to grayscale
    image = cv2.imread('input-images/{}'.format(image_name))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # generate keypoints
    orb = cv2.ORB_create(nb_points)
    keypoints, des = orb.detectAndCompute(gray, None)

    # generate output image
    img_final = cv2.drawKeypoints(gray, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite('output-images/keypoints-{}'.format(image_name), img_final)

    return keypoints


def processing(image_name, point_rate=200):
    img = cv2.imread('input-images/{}'.format(image_name))

    # get image shape
    height = img.shape[0]
    width = img.shape[1]

    # image preprocessing (grayscale, blur and binarisation)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    # introduce discontinuity
    print('=> Getting key points')
    for u in tqdm(range(width)):
        for v in range(height):
            if u == 20 or v == 20: thresh[v, u] = 0
            if u % point_rate == 0 or v % point_rate == 0: thresh[v, u] = 0

    # get centroids of fractions of drawing
    connectivity = 8
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    centroids = output[3]
    img_final = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    cnt = 0

    # overlay centroid on image + fill point list
    points = np.zeros((1000, 3), dtype=np.uint16)
    for c in centroids:
        if cnt != 0:  # avoid 1st centroid
            points[cnt][0] = int(c[1])
            points[cnt][1] = int(c[0])
            img_final[int(c[1]) - 8: int(c[1]) + 16, int(c[0]) - 8: int(c[0]) + 16] = [0, 255, 0]
        cnt += 1
    # write final image
    cv2.imwrite('output-images/keypoints-{}'.format(image_name), img_final)
    return points, cnt


def order_array(unordered_points, nb_points, generate_video=0, image_name=None):
    points = unordered_points

    clf = NearestNeighbors().fit(points)
    G = clf.kneighbors_graph()
    T = nx.from_scipy_sparse_matrix(G)

    paths = [list(nx.dfs_preorder_nodes(T, i)) for i in range(nb_points)]

    mindist = np.inf
    minidx = 0

    for i in range(nb_points):
        p = paths[i]  # order of nodes
        ordered = points[p]  # ordered nodes
        # find cost of that order by the sum of euclidean distances between points (i) and (i+1)
        cost = (((ordered[:-1] - ordered[1:]) ** 2).sum(1)).sum()
        if cost < mindist:
            mindist = cost
            minidx = i

    opt_order = paths[minidx]

    x = unordered_points[opt_order, 0]
    y = unordered_points[opt_order, 1]

    if generate_video:
        print('\n=> Generating video')

        img = cv2.imread('input-images/{}'.format(image_name))
        vid = cv2.VideoWriter('output-images/point-order.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                              5, (img.shape[1], img.shape[0]))

        for i in tqdm(range(nb_points)):
            img[x[i] - 8: x[i] + 16, y[i] - 8: y[i] + 16] = [0, 0, 255]
            vid.write(img)

        vid.release()

    return x, y

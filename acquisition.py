import cv2
from tqdm import tqdm
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
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


def get_keypoints(image_name, point_rate=200):
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
    points = np.zeros((len(centroids), 3), dtype=np.uint16)
    for c in centroids:
        if cnt != 0:  # avoid 1st centroid
            points[cnt][0] = int(c[1])
            points[cnt][1] = int(c[0])
            img_final[int(c[1]) - 8: int(c[1]) + 16, int(c[0]) - 8: int(c[0]) + 16] = [0, 255, 0]
        cnt += 1
    # write final image
    cv2.imwrite('output-images/keypoints-{}'.format(image_name), img_final)
    return points


def build_path(image_name, downsample, gen_video=0):
    # get key points
    unordered_points = get_keypoints(image_name, 50)

    # compute distance between each point
    distance_matrix = cdist(unordered_points, unordered_points)

    # set 1st point
    ordered_points = [(unordered_points[0, 0], unordered_points[0, 1])]
    unordered_points[0, 2] = 1

    # iterate over all points
    i = 0
    for u in range(len(unordered_points)):        # repeat u times to process all elements
        candidate = 0
        min_dist = 10000
        for v in range(len(unordered_points)):    # find the closest point to the previous one
            if distance_matrix[i, v] < min_dist and distance_matrix[i, v] != 0 and unordered_points[v, 2] == 0:
                min_dist = distance_matrix[i, v]
                candidate = v
        if u%downsample == 0:
            ordered_points.append((int(unordered_points[candidate, 0]), int(unordered_points[candidate, 1])))
        unordered_points[candidate, 2] = 1
        if distance_matrix[i, candidate] > 300:
            print('Step (', unordered_points[candidate, 0], unordered_points[candidate, 1], ') -> ', round(distance_matrix[i, candidate]))
        i = candidate

    # video generation (for infography)
    if gen_video:
        generate_video(ordered_points, image_name)

    return ordered_points


def get_image_format(image_name):
    img = cv2.imread('input-images/{}'.format(image_name))

    # get image shape
    height = img.shape[0]
    width = img.shape[1]

    return width, height


def split(keypoints, image_name):
    points = []
    slope_old = 0
    cnt = 0

    for i in range(len(keypoints)-5):
        x = keypoints[i][0]
        y = keypoints[i][1]
        x_next = keypoints[i+5][0]
        y_next = keypoints[i+5][1]
        th = 0.5

        slope = compute_slope(x, y, x_next, y_next)
        if slope != -1:
            if abs((abs(slope)-abs(slope_old))) > th or slope*slope_old < 0:
                cnt += 1
            points.append((x, y, cnt))
            slope_old = slope

    print(len(keypoints))
    print(len(points))
    get_extreme(points, image_name)
    generate_video(points, image_name)


def get_extreme(points, image_name):
    img = cv2.imread('input-images/{}'.format(image_name))
    limits = []

    for i in range(len(points)-1):
        x1, y1, t1 = points[i]
        x2, y2, t2 = points[i+1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(t1), (y1 + 30, x1 + 30), font, 1, (255, 0, 0), 1, cv2.LINE_AA)
        if t1 != t2:
            limits.append(points[i])
            limits.append(points[i+1])



    for i in range(len(limits)-1):
        x1, y1, t1 = limits[i]
        x2, y2, t2 = limits[i + 1]
        if t1 == t2 and x1 != x2 and y1 != y2:
            cv2.line(img, (int(y1), int(x1)), (int(y2), int(x2)), (0, 255, 0), 10)
            cv2.circle(img, (int(y1), int(x1)), radius=1, color=(0, 0, 255), thickness=20)
            cv2.circle(img, (int(y2), int(x2)), radius=1, color=(0, 0, 255), thickness=20)



    cv2.imwrite('output-images/lines.png'.format(image_name), img)

def compute_slope(x1, y1, x2, y2):
    slope = -1
    if abs(x2 - x1) > 0.1 and x2-x1 != 0:
        slope = (y2 - y1) / (x2 - x1)
    return slope


def generate_video(points, image_name):
    print('\n=> Generating video')

    img = cv2.imread('input-images/{}'.format(image_name))
    vid = cv2.VideoWriter('output-images/point-order.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                          5, (img.shape[1], img.shape[0]))
    for i in tqdm(range(len(points))):
        x, y, z = points[i]
        img[x - 8: x + 16, y - 8: y + 16] = [0, 0, 255]
        vid.write(img)

    vid.release()

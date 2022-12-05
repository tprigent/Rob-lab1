import cv2
from tqdm import tqdm
from scipy.spatial.distance import cdist
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


def build_path(image_name, point_rate, generate_video=0):
    # get key points
    unordered_points = get_keypoints(image_name, point_rate)

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
        ordered_points.append((int(unordered_points[candidate, 0]), int(unordered_points[candidate, 1])))
        unordered_points[candidate, 2] = 1
        if distance_matrix[i, candidate] > 300:
            print('Step (', unordered_points[candidate, 0], unordered_points[candidate, 1], ') -> ', round(distance_matrix[i, candidate]))
        i = candidate

    # video generation (for infography)
    if generate_video:
        print('\n=> Generating video')

        # init video
        img = cv2.imread('input-images/{}'.format(image_name))
        vid = cv2.VideoWriter('output-images/point-order.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                              5, (img.shape[1], img.shape[0]))

        # show points
        for i in tqdm(range(len(unordered_points))):
            x, y = ordered_points[i]
            img[x - 8: x + 16, y - 8: y + 16] = [0, 0, 255]
            vid.write(img)
        vid.release()

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

    for i in range(len(keypoints)-1):
        x = keypoints[i][0]
        y = keypoints[i][1]
        x_next = keypoints[i+1][0]
        y_next = keypoints[i+1][1]
        th = 200

        if abs(x_next - x) > 1 and x_next != 0:
            slope = y_next-y / x_next-x
            #print(abs(slope))
            if abs(slope-slope_old) > th:
                points.append((x, y))
            slope_old = slope

    print(len(keypoints))
    print(len(points))


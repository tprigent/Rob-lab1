import cv2
from tqdm import tqdm
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


def analyse_image(image_name):
    # open image & convert to grayscale
    image = cv2.imread('input-images/{}'.format(image_name))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # get image shape
    width = thresh.shape[0]
    height = thresh.shape[1]

    # detect contours
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

    # store contour points
    points = []
    for contour in enumerate(contours):
        data = contour[1]
        for i in range(len(data) - 1):
            # if i % 10 == 0:     # downsampling
            points.append(data[i][0])

    # draw resulting points on image
    cont_image = np.zeros([width, height, 1])
    cont_image.fill(255)

    for i in range(len(points) - 1):
        cont_image[points[i][1], points[i][0]] = 0
        if i % 2000 == 0:
            cv2.imwrite('output-images/keypoints-{}-{}'.format(i, image_name), cont_image)


def vertical_analysis(image_name):
    # open image & convert to grayscale
    image = cv2.imread('input-images/{}'.format(image_name))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 1, 100)
    # get image shape
    height = image.shape[0]
    width = image.shape[1]

    points0 = []

    # draw resulting points on image
    res_im0 = np.zeros([height, width, 1])
    res_im0.fill(255)
    res_im1 = np.zeros([height, width, 1])
    res_im1.fill(255)

    print('=> scanning lines')
    for u in tqdm(range(1, height)):
        for v in range(1, width):
            if edges[u, v] == 255:
                points0.append((u, v))

    for i in range(1, len(points0) - 1):
        if points0[i][0] != points0[i + 1][0]:
            res_im0[points0[i][0], points0[i][1]] = 0
        if points0[i - 1][0] != points0[i][0]:
            res_im1[points0[i][0], points0[i][1]] = 0

    cv2.imwrite('output-images/keypoints-0-{}'.format(image_name), res_im0)
    cv2.imwrite('output-images/keypoints-1-{}'.format(image_name), res_im1)


def processing(image_name):
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
            if u % 200 == 0 or v % 200 == 0: thresh[v, u] = 0

    # get centroids of fractions of drawing
    connectivity = 8
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    centroids = output[3]
    img_final = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    cnt = 0

    # overlay centroid on image + fill point list
    points = []
    for c in centroids:
        if cnt != 0:    # avoid 1st centroid
            points.append([int(c[1]), int(c[0])])
            img_final[int(c[1]) - 8: int(c[1]) + 16, int(c[0]) - 8: int(c[0]) + 16] = [0, 255, 0]
        else: cnt += 1
    # write final image
    cv2.imwrite('output-images/keypoints-{}'.format(image_name), img_final)
    return points

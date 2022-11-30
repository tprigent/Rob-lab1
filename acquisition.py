import cv2
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

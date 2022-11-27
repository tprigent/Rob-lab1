import cv2


def get_key_points(image_name, nb_points):
    # open image & convert to grayscale
    image = cv2.imread('input-images/{}'.format(image_name))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect edges
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # generate keypoints
    orb = cv2.ORB_create(nb_points)
    keypoints, des = orb.detectAndCompute(edges, None)

    # generate output image
    img_final = cv2.drawKeypoints(edges, keypoints, None)
    cv2.imwrite('output-images/keypoints-{}'.format(image_name), img_final)

    # return keypoints
    return keypoints

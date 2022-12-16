import cv2
import tools
from tqdm import tqdm
from scipy.spatial.distance import cdist
from collections import Counter
import numpy as np
import math


# use of OpenCV function to detect key points (not used yet)
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


# get all black points of an image
# down sample them by introducing discontinuities at a certain point rate
# and computing the centroids of the remaining points
def get_points(image_name, point_rate=200):
    img = cv2.imread('input-images/{}'.format(image_name))

    # get image shape
    height = img.shape[0]
    width = img.shape[1]

    # image preprocessing (grayscale, blur and binarisation)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    # introduce discontinuity
    print('=> Reading image points')
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


# get points from the drawing and order them according to the distance to each other (path following)
def get_ordered_points(image_name, gen_video=0):
    # get key points
    unordered_points = get_points(image_name, 50)

    # compute distance between each point
    distance_matrix = cdist(unordered_points, unordered_points)

    # set 1st point
    ordered_points = [(unordered_points[1, 0], unordered_points[1, 1])]
    unordered_points[1, 2] = 1

    # iterate over all points
    i = 1
    for u in range(len(unordered_points) - 1):  # repeat u times to process all elements
        candidate = 0
        min_dist = 10000
        for v in range(len(unordered_points)):  # find the closest point to the previous one
            if distance_matrix[i, v] < min_dist and distance_matrix[i, v] != 0 and unordered_points[v, 2] == 0:
                min_dist = distance_matrix[i, v]
                candidate = v
        if int(unordered_points[candidate, 0]) > 1:
            if int(unordered_points[candidate, 1]) > 1:
                ordered_points.append((int(unordered_points[candidate, 0]), int(unordered_points[candidate, 1])))
                unordered_points[candidate, 2] = 1

        if distance_matrix[i, candidate] > 300:
            print('Step (', unordered_points[candidate, 0], unordered_points[candidate, 1], ') -> ',
                  round(distance_matrix[i, candidate]))
        i = candidate
    # video generation (for infography)
    if gen_video:
        generate_video(ordered_points, image_name)

    return ordered_points


# classify points regarding the angle they make regarding the x-axis
def identify_class(ordered_points, image_name):
    img = cv2.imread('input-images/{}'.format(image_name))
    prev_angle = 0
    th = 4
    id = 0

    class_points = []

    for i in range(len(ordered_points) - 2):
        x1, y1 = ordered_points[i]
        x2, y2 = ordered_points[i + 2]
        angle = math.atan2(y2 - y1, x2 - x1) * 180 / np.pi
        if abs(angle - prev_angle) > th:
            id += 1

        prev_angle = angle
        class_points.append((ordered_points[i + 1], id))
        img = cv2.putText(img, str(id), (y1 + 8, x1 + 8), cv2.FONT_HERSHEY_SIMPLEX,
                          1, (255, 0, 0), 1, cv2.LINE_AA)

    cv2.imwrite('output-images/label.png'.format(image_name), img)
    return class_points


# returns array containing first and last point of each class (making segments)
def extract_segments_from_class(class_points):
    segments = []
    current_class = 0

    # create a new list that contains only the classes that occur once (noise)
    counts = Counter([c for pt, c in class_points])
    once = [c for c, count in counts.items() if count == 1]

    # analyse remaining segments
    for i in range(1, len(class_points)):
        class_p = class_points[i][1]
        if (class_p != current_class and class_p not in once) or len(class_points)-i <= 2:
            segments.append(class_points[i-1][0])
            segments.append(class_points[i][0])
            current_class = class_p

    return segments


# from start and end point of each class, remove points in a too close neighborhood
def extract_POI(points):
    cleaned_list = []
    exception_list = []
    in_exception = 0
    th = 120
    for i in range(len(points) - 2):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        dist = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5

        if dist < th:  # start exception list if points are too close to each other
            exception_now = 1
            in_exception = 1
            exception_list.append(points[i + 1])
        else:  # else simply add it to regular list
            exception_now = 0
            exception_list.append(points[i])

        if exception_now == 0 and in_exception == 1:  # detect switch between close points and far points
            in_exception = 0
            cleaned_list.append(tools.centroid(exception_list))

            exception_list = []

    cleaned_list.append(points[-1])
    return cleaned_list


# overlay segment drawing between all contiguous points of an array
def draw_segments(segments, image_name):
    img = cv2.imread('input-images/{}'.format(image_name))

    for i in range(len(segments)-1):
        y1, x1 = segments[i]
        y2, x2 = segments[i+1]

        cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 10)
        cv2.circle(img, (int(x1), int(y1)), radius=1, color=(0, 0, 255), thickness=30)
        cv2.circle(img, (int(x2), int(y2)), radius=1, color=(0, 0, 255), thickness=30)

    cv2.imwrite('output-images/lines.png'.format(image_name), img)

#from start to finish, remove
def comp_segments(all_points,segments, threshold):
    for i in range(len(segments)-1):
        y1, x1 = segments[i]         #get segment points
        y2, x2 = segments[i+1]
        angle = math.atan2(y2 - y1, x2 - x1) * 180 / np.pi
        for j in range(len(all_points)-1):
            y3, x3 = segments[j]
            y4, x4 = segments[j]
            if math.tan(angle)


def get_image_format(image_name):
    img = cv2.imread('input-images/{}'.format(image_name))

    # get image shape
    height = img.shape[0]
    width = img.shape[1]

    return width, height


# line detection function using Hough transform and OpenCV (not used yet)
def get_lines(image_name, print_lines):
    img = cv2.imread('input-images/{}'.format(image_name))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    dilation = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=5)
    cv2.imwrite('output-images/edges.png'.format(image_name), dilation)

    l = []
    for i in np.array([1, 15, 30, 60, 90]):
        lines = cv2.HoughLinesP(dilation, 1, np.pi / i, 800, 60, 4)
        if lines is not None:
            x1, y1, x2, y2 = lines[0][0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 10)
            cv2.circle(img, (int(x1), int(y1)), radius=1, color=(0, 0, 255), thickness=30)
            cv2.circle(img, (int(x2), int(y2)), radius=1, color=(0, 0, 255), thickness=30)
            l.append((x1, y1, x2, y2))

    if print_lines:
        cv2.imwrite('output-images/lines.png'.format(image_name), img)


# generate video to demonstrate point apparition order
def generate_video(points, image_name):
    print('\n=> Generating video')

    img = cv2.imread('input-images/{}'.format(image_name))
    vid = cv2.VideoWriter('output-images/point-order.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                          5, (img.shape[1], img.shape[0]))
    for i in tqdm(range(len(points))):
        x, y = points[i]
        img[int(x) - 8: int(x) + 16, int(y) - 8: int(y) + 16] = [0, 0, 255]
        vid.write(img)

    vid.release()

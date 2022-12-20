import cv2
import tools
from tqdm import tqdm
from scipy.spatial.distance import cdist
from collections import Counter
import numpy as np
import math


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
    th = 90    # 120
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


def curve_approx(all_points, line_points, th_accept):
    curve_points = []
    correspondences = []
    index_lp = 0
    for p in line_points:
        candidate = (0, 0)
        min_dist = float('inf')
        index_correspondence = 0
        for k in all_points:
            dist = tools.distance(p, k)
            if dist < min_dist:
                candidate = index_correspondence
                min_dist = dist
            index_correspondence += 1
        correspondences.append((index_lp, candidate))
        index_lp += 1

    for i in range(len(correspondences)-1):
        curve_points.append(line_points[correspondences[i][0]])
        start = correspondences[i][1]
        end = correspondences[i+1][1]

        x1 = all_points[start][0]
        y1 = all_points[start][1]
        x2 = all_points[round((end-start)/2)][0]
        y2 = all_points[round((end-start) / 2)][1]
        x3 = all_points[end][0]
        y3 = all_points[end][1]

        if tools.is_aligned(x1, y1, x2, y2, x3, y3, th=th_accept) == 0:
            middle_index = round((start+end)/2)
            curve_points.append((all_points[middle_index][0], all_points[middle_index][1]))

    curve_points.append(line_points[-1])
    print(len(curve_points))
    return curve_points


# function that says if the line between two points are straight or circular and then chose the good move

# Approach: reading the array of point of interest we compute the equation of the straight line between two points
# Then, we compare the between the points in the array of ordered points to check if the line is straight or not
#          If the line is straight --> MOVE, if it's not, we add a point and do a MOVEC
def curve_path(cleaned_list, ordered_points):
    th=1500
    epsilon=1000
    compteur=0
    print('longeur tableau initial ={}'.format(len(cleaned_list)))
    print('Longueur du tableau de tous les points={}'.format(len(ordered_points)))
    print(cleaned_list)
    for i in range(len(cleaned_list)-1):
        if cleaned_list[i+1]!=cleaned_list[i]:
            a = cleaned_list[i+1][1]-cleaned_list[i][1]
            print(a)
            b = cleaned_list[i][0]-cleaned_list[i+1][0]
            print(b)
            c = a*(cleaned_list[0][0]) + b*(cleaned_list[0][0])
            for j in range(len(ordered_points)-1):
                    if cleaned_list[i+1] == ordered_points[j+1] or (abs(cleaned_list[i+1][0]-ordered_points[i+1][0]) < epsilon and abs(cleaned_list[i+1][1]-ordered_points[i+1][1]) < epsilon):
                        index1 = find_midcurve_index(ordered_points, cleaned_list[i])
                        index2 = find_midcurve_index(ordered_points, cleaned_list[i+1])
                        dist = abs((a * ordered_points[i][0] + b * ordered_points[i][1] + c)) / (math.sqrt(a * a + b * b))
                        middle = math.floor(abs(index1-index2)/2)
                        if dist > th:
                            new_point = ordered_points[middle+index1]
                            cleaned_list.insert(i+1, new_point)
                            compteur = compteur+1
    print(new_point)
    print('longeur nv tableau = {}'.format(len(cleaned_list)))
    print(cleaned_list)


#function that returns the index of the nearest point of "point" in a table of points
def find_midcurve_index(ordered_points, point):
    d_min = 1000
    index = 0
    for i in range(len(ordered_points)):
        if tools.distance(ordered_points[i], point) < d_min:
            index = i
            d_min = tools.distance(ordered_points[i], point)
    return index


def draw_segments(segments, image_name, out_name):
    img = cv2.imread('input-images/{}'.format(image_name))

    for i in range(len(segments)-1):
        y1, x1 = segments[i]
        y2, x2 = segments[i+1]

        cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 10)
        cv2.circle(img, (int(x1), int(y1)), radius=1, color=(0, 0, 255), thickness=30)
        cv2.circle(img, (int(x2), int(y2)), radius=1, color=(0, 0, 255), thickness=30)

    cv2.imwrite('output-images/{}'.format(out_name), img)

#from start to finish, remove lines that don't match the drawing and. Get line and circle movements
def comp_segments(all_points,segments, threshold, image_name):

    img = cv2.imread('input-images/{}'.format(image_name))
    true_segments = []
    for i in range(len(segments)-1):
        y1, x1 = segments[i]         #get segment points
        y2, x2 = segments[i+1]
        cy, cx = (y1+y2)/2 , (x1+x2)/2       #get middle point/center of circle
        dist_max = 0
        dist_thresh_total = 0
        dist_average = 0
        remove_point = 0
        width = 500
        y4, x4 = 0,0
        dist_1_2 = math.dist((y1,x1),(y2,x2))                 #segment distance
        angle = math.atan2((y1-y2),(x1-x2))
        radius = dist_1_2/2                                   #radius of circle
        for j in range(len(all_points)-1):                    #compare segment line with all other points
            y3, x3 = all_points[j]
            if is_create_rectangle(y1,x1, y2,x2 , y3, x3):           #if's point inside circle
                dist_1_3 = math.dist((y1,x1),(y3,x3))
                dist_2_3 = math.dist((y2,x2),(y3,x3))
                dist_thresh = abs(dist_1_3 + dist_2_3 - dist_1_2)         #calc thresh average
                dist_thresh_total += dist_thresh
                if j != 0:
                    dist_average = dist_thresh_total/j
                if dist_max < dist_thresh:
                    dist_max = dist_thresh
                    y4 = y3
                    x4 = x3
            else:   #outside of circle
                continue                                       #doesn't matter

        true_segments.append(segments[i])
        #cv2.circle(img, (int(x1), int(y1)), radius=1, color=(0, 255, 0), thickness=30)
        #img = cv2.putText(img, str(int(dist_max)), (int(x4) + 8, int(y4) + 8), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 1, cv2.LINE_AA)
        if dist_thresh_total > threshold:                            #not a perfect line
            true_segments.append((y4,x4))
            cv2.circle(img, (int(x4), int(y4)), radius=1, color=(0, 0, 255), thickness=30)  #movec
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 10)          #red
            #testing
            cv2.line(img, (int(x1), int(y1)), (int(x4), int(y4)), (255, 0, 0), 1)          #debug distances
            cv2.line(img, (int(x2), int(y2)), (int(x4), int(y4)), (255, 0, 0), 1)          #red
        #if remove_point == 0:
        #else:
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 10)        #normal line
        img = cv2.putText(img, str(int(dist_average)), (int(x1) + 8, int(y1) + 8), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 1, cv2.LINE_AA)
        true_segments.append(segments[i+1])
        cv2.circle(img, (int(x2), int(y2)), radius=1, color=(0, 255, 0), thickness=30)

    cv2.imwrite('output-images/true_segments.png'.format(image_name), img)
    return true_segments

def is_create_rectangle(y1,x1, y2,x2 , yt, xt):
    width = 500
    origin = x1 , y1
    length = math.dist((y1,x1),(y2,x2))
    #get angle
    angle = math.atan2((y1-y2),(x1-x2))
    x_point, y_point = rotate(origin, (xt,yt), 2*math.pi -angle)
    #create rectangle
    tl_y = y1 + width
    tl_x = x1
    bl_y = y1 - width
    bl_x = x1

    tr_y = y1 + width
    tr_x = x1 + length
    br_y = y2 - width
    br_x = x1 + length

    if x_point > tl_x and x_point < tr_x and y_point > bl_y and y_point < tr_y:
        return True
    else:
        return False


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def get_image_format(image_name):
    img = cv2.imread('input-images/{}'.format(image_name))

    # get image shape
    height = img.shape[0]
    width = img.shape[1]

    return width, height


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

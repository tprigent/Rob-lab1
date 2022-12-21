import datetime


# Console text formatting for titles
def print_title(text):
    print('\u001b[32m \n{}\u001b[0m'.format(text))
    log(text)


# Console text formatting for sent messages
def print_robot_send(text):
    print('\u001b[36;1m {}\u001b[0m'.format(text))
    log(text)


# Console text formatting for received messages
def print_robot_receive(text):
    print('\u001b[34;1m {}\u001b[0m'.format(text))
    log(text)


# Log message in the log file
def log(msg):
    f_log = open('history.log', 'a+')
    timestamp = datetime.datetime.now()
    log_text = '{}: {}\n'.format(timestamp, msg)
    f_log.write(log_text)


# Math: compute the centroid of an array of points
def centroid(arr):
    sum_x = 0
    sum_y = 0
    length = len(arr)
    for i in range(length):
        sum_x += arr[i][0]
        sum_y += arr[i][1]
    return sum_x / length, sum_y / length


# Math: compute distance between two points
def distance(point1, point2):
    # Calculate the Euclidean distance between two points
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


# check if pt3 is aligned with pts 1 & 2, according to a threshold
def is_aligned(x1, y1, x2, y2, x3, y3, th):
    if x1 == x2:
        return x1 - th <= x3 <= x1 + th
    slope = (y2 - y1) / (x2 - x1)
    y_intercept = y1 - (slope * x1)
    y = slope * x3 + y_intercept
    return abs(y - y3) < th

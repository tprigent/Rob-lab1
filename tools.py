import datetime


def print_title(text):
    print('\u001b[32m \n{}\u001b[0m'.format(text))
    log(text)


def print_robot_send(text):
    print('\u001b[36;1m {}\u001b[0m'.format(text))
    log(text)


def print_robot_receive(text):
    print('\u001b[34;1m {}\u001b[0m'.format(text))
    log(text)


def log(msg):
    f_log = open('history.log', 'a+')
    timestamp = datetime.datetime.now()
    log_text = '{}: {}\n'.format(timestamp, msg)
    f_log.write(log_text)


def centroid(arr):
    sum_x = 0
    sum_y = 0
    length = len(arr)
    for i in range(length):
        sum_x += arr[i][0]
        sum_y += arr[i][1]
    return sum_x/length, sum_y/length


def distance(point1, point2):
    # Calculate the Euclidean distance between two points
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
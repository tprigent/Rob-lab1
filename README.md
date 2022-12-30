# Drawing robot

## Context
This project has been realised in the context of an introduction course to robotics at [IST Liboa](https://tecnico.ulisboa.pt).

The problem has been solved in a limited amount of time (around 7 weeks). Results are the ones presented for evaluation.

The global aim was to control a robot designed for pick&place (Scorbot) in order to make it reproduce a path 
represented by a black line over a white background with a marker, on an A3 sheet of paper. 
This path, not known in advance was given in the form of an image.
A computer was used to process the image, to generate a sequence of points and movements to be exectuted by the robot, 
over a RS232-serial connexion.

![Robotics - lab 1 drawio](https://user-images.githubusercontent.com/14911193/210113706-fdd1ed36-9d1f-423a-8683-d9ade36f3d68.png)


Two main fields were thus involved in this project: image processing and control.


## Table of content
1. [Image processing](#1-image-processing)
   1. [General approach](#i-general-approach)
   2. [Process](#ii-process)
   3. [Results](#iii-results)
2. [Communication & robot control](#3-communication-and-robot-control)
   1. [ACL commands](#i-acl-commands)
   2. [Script](#ii-script)
   3. [Results](#iii-results-1)
3. [References](#references)

## 1. Image processing
Several constraints linked to the nature of both input images and robot environment made the development of a robust 
solution very challenging.
The few backgrounds the team had in image processing (morphological operations, Hough transforms, ...) were not 
sufficient to provide a straightforward solution.

### i. General approach
The desired output of the image processing part was to have a collection of points, cleverly spaced so that the 
general shape of the drawing can be respect, but without having too much of them. Indeed, defining points in the robot 
is a very time-expensive process.

The second major issue was to have this collection of points in an ordered way so that the robot draws the path by just 
going from one to another. All of this had to be done considering complex paths, including crossings, U-turns and 
close or open shapes.

### ii. Process
Our solution was composed of multiple steps, whose code can be found in the `acquisition.py` file.
The library OpenCV has been used mostly for image managing (opening, creation, points/lines overlay, ...).
Most of the image operations have been done by the hand, using images has Numpy arrays.

The following table represents the logical order of the functions used, their role, and the number of points associated.
*NB: the number of points is relative to [`test_draw_1.png`](/input-images/test_draw_1.png)*

| Function                      | Description                                                                                                                      | Number of points |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------|
| `get_points`                  | Recognition of black pixels, and downsampling by splitting the drawing regularly and computing the centroid of each sub-element. | 507              |
| `get_ordered_points`          | Order the array of point, taking the first of the top, and taking the closest neighbour each time.                               | 507              |
| `identify_class`              | Group points in classes: points forming the same angle to the horizontal line are considered to be part of the same class.       | 507              |
| `extract_segments_from_class` | Keep only first and last element of point in the same class, image now approximated by segments.                                 | 68               |
| `extract_POI`                 | Keep only points of interests, *i.e.* take the centroid of points that are too close to each other.                              | 25               |
| `curve_approx`                | Increase reliability of approximation by adding the middle point of the curves not detected before (done twice)                  | 44               |

This combination of techniques allows to reduce the number of points by 91%, while keeping the general shape of the drawing.

### iii. Results
For both given images, here are the results, assuming that the robot will draw straight lines between each point, from the first to the last.
<!-- Insert images here -->

| [`test_draw_1.png`](/input-images/test_draw_1.png) | [`test_draw_2.png`](/input-images/test_draw_2.png) |
|----------------------------------------------------|----------------------------------------------------|
|        <img width="180" alt="Draw1 with lines" src="https://user-images.githubusercontent.com/14911193/210113802-068c44ac-34df-4e88-aa1f-aee6f2bd92c1.png"> |  <img width="180" alt="Draw2 with lines" src="https://user-images.githubusercontent.com/14911193/210113891-1da6610c-f330-42c4-8b31-769efeb51527.png">
  |

As it is impossible for us to move the pen up, we see some incorrectness, especially for closed shapes including crossings (like `test_draw_2.png`).

We can also see that the beginning of the path is not taken into account, as on `test_draw_1.png`.

## 2. Communication and robot control
### i. ACL commands
The instructions are sent through a serial connection to the robot. With the help of the serial Python library, useful functions have been created to automate the creation of ACL commands, and to send them.
For instance, a small library of functions has been built to help in formatting the string to send to the robot, with the right end characters. 
It was then easier to send commands, via a single line of code. Some data structures to handle points (Point) and groups of points (Vector) have been created to make the data management easier.

All the corresponding functions have been grouped in the [`robot.py`](robot.py) file.

### ii. Script
A provided script (in [`main.py`](main.py)) is aimed to automate the whole process, from the input image to the output drawing. It contains the following steps, with some prompts to the user:
1. Home the robot (optional)
2. Image processing
3. Ask user to place the robot at the starting point (wait for user confirmation)
4. Change the point frame according to the starting point (is the starting point correct ?)
5. Record the points in the robot memory

Moreover, a neat display of the steps of the script is generated, but also of the commands sent and the responses received. This can be launched, after installing the needed modules indicated in [`requirements.txt`](requirements.txt), by simply running the main function.

*NB: The serial port must be edited in the main script (very beginning).*

<img width="400" alt="Console output" src="https://user-images.githubusercontent.com/14911193/210113944-4fa7f168-8a79-444e-9569-e24ed2ef953d.png">


### iii. Results
The results using the robot are the following:

| [`test_draw_1.png`](/input-images/test_draw_1.png)      | [`test_draw_2.png`](/input-images/test_draw_2.png)      |
|---------------------------------------------------------|---------------------------------------------------------|
| <img width="180" alt="Draw1 robot" src="https://user-images.githubusercontent.com/14911193/210113969-659f5f37-d762-45dc-9165-bbeae94748c9.png"> | <img width="180" alt="Draw2 robot" src="https://user-images.githubusercontent.com/14911193/210114228-76571831-4709-42a4-a434-d9a77a2aa774.png"> |
| [Corresponding video](https://go.tprigent.fr/Rob-draw1) | [Corresponding video](https://go.tprigent.fr/Rob-draw2) | 

Here, we can see that we have some incorrectness regarding the original drawing:
1. The robot starts to draw from the origin of the new frame and not the first point
2. The starting point is not the right one
3. The drawing has imprecision. The robot is moving point to point, theoretically in a straight line (using ACL command `MOVE`).
Other way of drawing might be more accurate (*e.g.* `MOVEC` for curves).

## References
- ACL reference guide - 4th edition, Eshed Robotec
- Scorbot-ER VII user’s manual - 2nd edition, Eshed Robotec
- Guidelines to use Scorbot-ER VII, Alberto Vale & João Sequeira (IST, 2022) 
-  OpenCV Python tutorials, [docs.opencv.org](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

# Drawing robot

## Context
This project has been realised in the context of an introduction course to robotics at [IST Liboa](https://tecnico.ulisboa.pt).

The global aim was to control a robot designed for pick&place (Scorbot) in order to make it reproduce a path 
represented by a black line over a white background with a marker, on an A3 sheet of paper. 
This path, not known in advance was given in the form of an image.
A computer was used to process the image, to generate a sequence of points and movements to be exectuted by the robot, 
over a RS232-serial connexion.

Two main fields were thus involved in this project: image processing and control.


## Table of content
1. [Image processing](#1-image-processing)
   1. [General approach](#i-general-approach)
   2. [Process](#ii-process)
   3. [Results](#iii-results)
2. [Data conversion](#2-data-conversion)
3. [Communication & robot control](#3-communication-and-robot-control)

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

| Function                      | Description                                                                                                                | Number of points |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------|------------------|
| `get_points`                  | Basic recognition of black pixels                                                                                          | 507              |
| `get_ordered_points`          | Order the array of point, taking the first of the top, and taking the closest neighbour each time.                         | 507              |
| `identify_class`              | Group points in classes: points forming the same angle to the horizontal line are considered to be part of the same class. | 507              |
| `extract_segments_from_class` | Keep only first and last element of point in the same class, image now approximated by segments.                           | 68               |
| `extract_POI`                 | Keep only points of interests, *i.e.* take the centroid of points that are too close to each other.                        | 25               |
| `curve_approx`                | Increase reliability of approximation by adding the middle point of the curves not detected before (done twice)            | 44               |

### iii. Results

## 2. Data conversion
## 3. Communication and robot control


## References

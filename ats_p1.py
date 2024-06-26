# -*- coding: utf-8 -*-
"""ATS P1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NKWeghqZvc4oYGZkJg2YMLOtyOwA0z3a

# Praktikum Autonome Systeme
Place Recognition and Homing Using the Snapshot Model

Daniel Kröber - 11145549  
Robert Roppel - 11144682

# Import libaries
"""

from __future__ import annotations
import itertools
import math
import numpy as np
import matplotlib
import matplotlib.axes
import matplotlib.colors
import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot as plt

"""# Setup

## Helper
"""

def arc_length(left, right, radius=1):  # Arc-length on circle
    arc = abs(right - left)
    if left < right:
        arc = 2 * np.pi - arc
    return arc * radius

def calc_angle(x1, y1, x2, y2):  # Angle between (x1,y1) and (x2,y2)
            return math.atan2(y2 - y1, x2 - x1)

def calc_dist(x1, y1, x2, y2):  # Distance between (x1,y1) and (x2,y2)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def to_vector(angle: float):    # Turns angle into a unit vector
    vec = np.array([math.cos(angle), math.sin(angle)])
    return vec / np.linalg.norm(vec)


def closest_angle(input_angle, feautre_list: list[Feature]): # Matches the input_angle to the closest angle on feature_list (angle)
    min_difference = 2 * np.pi

    for f in feautre_list:
        difference = abs(f.center - input_angle)
        difference = min(difference, 2 * np.pi - difference)

        if difference < min_difference:
            min_difference = difference
            closest_angle = f

    return closest_angle  # Returns the feature with the closest angle

"""## Landmark"""

class Landmark:   # Structure to save position and radius of landmarks
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def __str__(self):
        return "Landmark(x={}, y={}, radius={})".format(self.x, self.y, self.radius)

    def plot(self, ax: matplotlib.axes.Axes):
        circle = matplotlib.patches.Circle((self.x, self.y), self.radius, color="#99cdfc")
        ax.add_patch(circle)

"""## Feature"""

class Feature:  # Stucture to save properties of a feature (feature = "space between landmarks" or "landmarks")
    def __init__(self, center, length, left, right):
        self.center = center
        self.length = length
        self.left = left
        self.right = right

    def __str__(self):
        return "Feature(center={}, length={})".format(self.center, self.length)

    def center_feature_cw(self, other: Feature):
        if self.center == other.center:
            space = self.center
        elif self.center > other.center:
            space = self.center + (other.center - self.center) / 2
        else:
            space = self.center + np.pi + (other.center - self.center) / 2

        left = self.right
        right = other.left
        length = arc_length(left, right)
        return Feature(space, length, left, right)

    def plot_at(self, x, y, ax: matplotlib.axes.Axes, length=None, color="green", *args, **kwargs):
        if length is None:
            length = self.length
        x1 = x + math.cos(self.center) * length
        y1 = y + math.sin(self.center) * length
        ax.plot([x, x1], [y, y1], color=color, *args, **kwargs)

    def plot_angle_at(self, x, y, ax: matplotlib.axes.Axes, length=None, color="red", *args, **kwargs):
        if length is None:
            length = 20
        x1 = x + math.cos(self.left) * length
        y1 = y + math.sin(self.left) * length
        ax.plot([x, x1], [y, y1], color=color, *args, **kwargs)
        x2 = x + math.cos(self.right) * length
        y2 = y + math.sin(self.right) * length
        ax.plot([x, x2], [y, y2], color=color, *args, **kwargs)

"""## Snapshot"""

class Snapshot:   # Structure to save all properties of a snapshot (position, features(landmarks), features(spaces between landmarks))
    def __init__(self, x, y, landmarks: list[Landmark]):
        self.x = x
        self.y = y
        self.features: list[Feature] = []
        self.snapshot(landmarks)
        self.spaces_features: list[Feature] = []
        self.calc_spaces_features()

    def __str__(self):
        snap = "Snapshot(x={}, y={})".format(self.x, self.y)
        features = "\n".join([str(f) for f in self.features])
        spaces = "\n".join([str(f) for f in self.spaces_features])
        return snap + "\n" + features + "\n" + spaces

    def snapshot(self, landmarks: list[Landmark]):  # Returns angles to all marks for current point
        for l in landmarks:
            dist = calc_dist(self.x, self.y, l.x, l.y)
            center = calc_angle(self.x, self.y, l.x, l.y)     # Middle of mark
            left_side = center + math.asin(l.radius / dist)   # Left side of mark
            right_side = center - math.asin(l.radius / dist)  # Right side of mark
            length = arc_length(left_side, right_side)
            self.features.append(Feature(center, length, left_side, right_side))

    def calc_spaces_features(self):
        for i in range(len(self.features)):
            f_from = self.features[i]
            f_to = self.features[(i + 1) % len(self.features)]
            center = f_from.center_feature_cw(f_to)
            if f_from.left > f_to.right and f_from.right < f_to.left:   # When Features Overlap dont draw a space between
                continue
            self.spaces_features.append(center)

    def plot_at(self, x, y, ax: matplotlib.axes.Axes, length=None, *args, **kwargs):
        for f in self.features:
            f.plot_at(x, y, ax, length, *args, **kwargs)
            f.plot_angle_at(x, y, ax, length, *args, **kwargs)
        for f in self.spaces_features:
            f.plot_at(x, y, ax, length, color="blue", *args, **kwargs)

"""## Plot"""

def create_plot() -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    fig = plt.figure()
    ax = fig.subplots()
    if ax is None or not isinstance(ax, matplotlib.axes.Axes):
        raise ValueError("Failed to create plot")
    ax.set_axisbelow(True)
    ax.grid()

    ax.set_xticks(np.arange(-7, 7, 1))
    ax.set_yticks(np.arange(-7, 7, 1))
    ax.set_ylim(-7, 7)
    ax.set_xlim(-7, 7)
    ax.set_aspect("equal", adjustable="box")

    center = matplotlib.patches.Circle((0, 0), 0.1, color="black")
    ax.add_patch(center)

    return (fig, ax)


def plot_vector(ax, x, y, vec, color="black"):
    ax.quiver(x, y, vec[0], vec[1], angles="xy", scale_units="xy", scale=1, color=color)

"""# Calculation"""

# Zur De/Aktivierung der Test
TEST = False #@param["False","True"] {type="raw"}

"""## Cylinder landmarks

The landmarks are in the form of `(x, y, radius)`
"""

radius = 1.0 / 2.0
marks = [
    Landmark(3.5, 2, radius),
    Landmark(3.5, -2, radius),
    Landmark(0, -4, radius),
]

"""### Origin"""

origin = Snapshot(0, 0, marks)  # Takes a snapshot from the origin (0,0) position
if(TEST):
  print(origin)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  origin.plot_at(origin.x, origin.y, ax, 20, linewidth=0.5)

  plt.show()

"""### Test at (-3, -3)"""

if(TEST):
  current = Snapshot(-3, -3, marks)   # Takes a snapshot from the testposition (-3,-3)
  print(current)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  current.plot_at(current.x, current.y, ax, 20, linewidth=0.5)

  plt.show()

"""## Turn vectors"""

def turn_vectors(current: Snapshot, origin: Snapshot):    # Calculates all turn_vectors for the current snapshot
    turn_vec: list[tuple[Feature, Feature, float]] = []
    for feature in origin.features:     # Do for all features
        nearest = closest_angle(feature.center, current.features)   # Find closest feature
        if nearest.center < feature.center:                   # Rotates turn_vector based on direction from origin
            vec_ang = nearest.center - np.pi / 2.0
        else:
            vec_ang = nearest.center + np.pi / 2.0
        if nearest.length > np.pi:                            # Flips turn_vector if segment is larger then 180°
            vec_ang += np.pi
            if vec_ang > np.pi:                               # Cuts turn_vector down to range -pi to +pi
                vec_ang -= 2 * np.pi

        turn_vec.append((feature, nearest, vec_ang))

    for feature in origin.spaces_features:  # Do for all spaces
        nearest = closest_angle(feature.center, current.spaces_features)
        if nearest.center < feature.center:
            vec_ang = nearest.center - np.pi / 2.0
        else:
            vec_ang = nearest.center + np.pi / 2.0
        if nearest.length > np.pi:
            vec_ang += np.pi
            if vec_ang > np.pi:
                vec_ang -= 2 * np.pi

        turn_vec.append((feature, nearest, vec_ang))

    return turn_vec

"""### Test"""

if(TEST):
  turn_angles = turn_vectors(current, origin) # List of tuples (origin, nearest current, turn angle)
  turn_vecs = [to_vector(v[2]) for v in turn_angles]

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  for a in turn_angles:
      x1 = current.x + math.cos(a[2]) * 5
      y1 = current.y + math.sin(a[2]) * 5
      ax.plot([current.x, x1], [current.y, y1], color="orange", linewidth=0.5)

  for v in turn_vecs:
      print(v)
      color = (np.random.random(), np.random.random(), np.random.random())  # RGB color
      color_hex = matplotlib.colors.to_hex(color)
      plot_vector(ax, current.x, current.y, v, color=color_hex)

  current.plot_at(current.x, current.y, ax, 20, linewidth=1)
  origin.plot_at(current.x, current.y, ax, 20, linewidth=0.5)

  plt.show()

  turn_vec = np.sum(turn_vecs, axis=0)
  print("Turn vector: ", turn_vec)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)
  plot_vector(ax, current.x, current.y, turn_vec, "orange")

  plt.show()

"""## Approach vector"""

def approach_vectors(map: list[tuple[Feature, Feature, float]]):  # Calculates approach_vectors for current snapshot (Input turn_angles)
    approach = []
    for v in map:
        vec = to_vector(v[1].center)
        if v[0].length > v[1].length: # When current_feature > origin_feature
            approach.append(vec)      # Move towards feature
        else:
            approach.append(-vec)     # Move away form feature

    return approach

"""### Test"""

if(TEST):
  approach_vecs = approach_vectors(turn_angles)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  for v in approach_vecs:
      print(v)
      color = (np.random.random(), np.random.random(), np.random.random())  # RGB color
      color_hex = matplotlib.colors.to_hex(color)
      plot_vector(ax, current.x, current.y, v, color=color_hex)

  current.plot_at(current.x, current.y, ax, 20, linewidth=1)
  origin.plot_at(current.x, current.y, ax, 20, linewidth=0.5)

  plt.show()

  approach_vec = np.sum(approach_vecs, axis=0)
  print("Approach vector: ", approach_vec)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  plot_vector(ax, current.x, current.y, approach_vec, "orange")

  plt.show()

"""## Homing vector + Test"""

if(TEST):
  homing_vec = turn_vec + approach_vec * 3  # Ratio (1:3)
  homing_vec /= np.linalg.norm(homing_vec)  # Normalize
  print("Homing vector: ", homing_vec)

  fig, ax = create_plot()
  for m in marks:
      m.plot(ax)

  plot_vector(ax, current.x, current.y, homing_vec, "orange")

  plt.show()

"""# Solution

## Homing vector field
"""

fig, ax = create_plot()
for m in marks:
    m.plot(ax)

precisions = []

for x in np.arange(-7, 8, 1):                                           # Do for whole grid x
    for y in np.arange(-7, 8, 1):                                       # Do fro whole grid y
        if x == 0 and y == 0:                                           # Exclude origin position
            continue
        if (x, y) in [(m.x, m.y) for m in marks]:                       # Exclude positions blocked by marks
            continue
        current = Snapshot(x, y, marks)                                 # Take snapshot from current position
        turn_angles = turn_vectors(current, origin)                     # Calculate turn_angles
        turn_vecs = [to_vector(v[2]) for v in turn_angles]              # Transform into turn_vectors
        turn_vec = np.sum(turn_vecs, axis=0)                            # Transform into one turn_vector

        approach_vecs = approach_vectors(turn_angles)                   # Calculate approach_vectors
        approach_vec = np.sum(approach_vecs, axis=0)                    # Transform into one approach_vector

        homing_vec = turn_vec + approach_vec * 3                        # Calculate homing_vector (ratio 1:3)
        homing_vec /= np.linalg.norm(homing_vec)                        # Normalize

        ideal_angle = calc_angle(x, y, 0, 0)                            # Calculate ideal_angle to origin
        ideal_vec = to_vector(ideal_angle)                              # Tranform into ideal_vector
        angle_diff = abs(np.arccos(np.dot(homing_vec, ideal_vec)))      # Calculate angular_difference between ideal_vector an homing_vector
        precisions.append(angle_diff)                                   # Append to precissions list

        plot_vector(ax, x, y, homing_vec, "orange")                     # Plot current homing_vector

plt.title("Average homing precision: \n"+ str(np.mean(precisions) * 180 / np.pi) +"°") # Takes average from precisions list and transforms to degrees
plt.show()                                                              # Outputs vector_field image
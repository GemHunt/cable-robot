import math
import numpy as np

class LineModel(object):
   def __init__(self, line):
       """
           :type line: tuple((x1,y1),(x2,y2))
       """

       self.line = line
       self.x_intercept = 0.0
       self.slope = 0.0
       self.y_intercept = 0.0
       self.set_line_attributes()

   def set_line_attributes(self):
       y_difference = float(self.line[1][1]) - float(self.line[0][1])
       x_difference = float(self.line[1][0]) - float(self.line[0][0])
       x_intercept = 0.0
       if float(abs(x_difference)) == 0.0:
           slope = 9999999999999999.0
       else:
           slope = y_difference / x_difference

       y_intercept = float(self.line[0][1]) - slope * float(self.line[0][0])
       if slope != 0.0:
           x_intercept = -y_intercept / slope
       """
           constructor values for usage
           :type y_intercept : float
           :type slope : float

       """
       self.x_intercept = x_intercept
       self.slope = slope
       self.y_intercept = y_intercept

   # check pt1 or pt2 which one is smaller
   @classmethod
   def group_lines_concat_two_endpoint(cls, lists):
       # create dictionary for easier readable code
       _vertical = []
       _horizontal = []
       _others = []
       _verset = set()
       _horiset = set()
       _otherset = set()
       list.sort(lists)
       for line in lists:

           # vertical
           if line[0][0] == line[1][0]:
               _verset.add(line[0][0])
               _vertical.append(line)
           elif line[0][1] == line[1][1]:
               _horiset.add(line[0][1])
               _horizontal.append(line)
           else:
               _others.append(line)

       pivot_vertical = _vertical[0][0]

       line_points = []
       for index, line in enumerate(_vertical):
           if index == len(_vertical) - 1:
               line_points.append([pivot_vertical, _vertical[index][1]])

           if line[0][0] != pivot_vertical[0]:
               endpoint = _vertical[index - 1][1]
               line_points.append([pivot_vertical, endpoint])
               pivot_vertical = line[0]

       pivot_horizontal = _horizontal[0][0]
       for index, line in enumerate(_horizontal):
           if index == len(_horizontal) - 1:
               line_points.append([pivot_horizontal, _horizontal[index][1]])

           if line[0][1] != pivot_horizontal[1]:
               endpoint = _horizontal[index - 1][1]
               line_points.append([pivot_horizontal, endpoint])
               pivot_horizontal = line[0]

       #############################
       pivot_others = _others[0][0]
       for index, line in enumerate(_others):
           slope = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0])

           pivot_slope_detect = (line[1][1] - pivot_others[1]) / (line[1][0] - pivot_others[0])

           if slope != pivot_slope_detect:
               endpoint = _others[index - 1][1]
               line_points.append([pivot_others, endpoint])
               pivot_others = line[0]

           if index == len(_others) - 1:
               line_points.append([pivot_others, _others[index][1]])

       return line_points

   @classmethod
   def get_lines_in_bounding_box(cls, lines, pt1, pt2):
       in_the_bounding_box = []
       if pt1[0] < pt2[0] and pt1[1] < pt2[1]:
           for line in lines:
               if pt1[0] <= line[0][0] and pt1[1] <= line[0][1] <= pt2[0] and pt2[1] >= line[1][1]:
                   print("inside the box")
                   in_the_bounding_box.append([line])
       return in_the_bounding_box

   @classmethod
   def is_line_in_bounding_box(cls, line):
       bbx1 = 6400
       bby1 = 5000
       bbx2 = 7200
       bby2 = 6200

       pt1, pt2 = line

       x1, y1 = pt1
       x2, y2 = pt2
       if bbx1 < x1 < bbx2 and bbx1 < x2 < bbx2 and bby1 < y1 < bby2 and bby1 < y2 < bby2:
           return True
       else:
           return False

   def get_points_to_draw(self):
       pt1, pt2 = self.line
       pt1 = (int(pt1[0]), int(pt1[1]))
       pt2 = (int(pt2[0]), int(pt2[1]))
       """
           :type pt1,pt2: int
       """
       return pt1, pt2

   # def get_distance_from_point(self,point):
   #     pt1,pt2 = np.array(self.line)
   #     point = np.array(point)
   #     dist = np.linalg.norm(np.cross(pt2 - pt1, pt1 - point)) / np.linalg.norm(pt2 - pt1)
   #     return dist

   def get_close_lines(self, input_lines, tolerance=.1):
       close_lines = []
       for line in input_lines:
           dist_start = self.get_distance_from_point(line[0])
           dist_end = self.get_distance_from_point(line[1])
           # print dist_end, dist_start
           if (dist_start < tolerance) and (dist_end < tolerance):
               # print("in")
               close_lines.append(line)
       return close_lines

   def get_distance_from_point(self, other_point):
       pt1, pt2 = np.array(self.line)
       pt1x, pt1y = pt1
       pt2x, pt2y = pt2

       dx = pt2x - pt1x
       dy = pt2y - pt1y
       dr2 = float(dx ** 2 + dy ** 2)

       lerp = ((other_point[0] - pt1x) * dx + (other_point[1] - pt1y) * dy) / dr2
       if lerp < 0:
           lerp = 0
       elif lerp > 1:
           lerp = 1

       x = lerp * dx + pt1x
       y = lerp * dy + pt1y

       _dx = x - other_point[0]
       _dy = y - other_point[1]
       return math.sqrt(_dx ** 2 + _dy ** 2)

   def get_angle(self):
       angle = math.degrees(math.atan(self.slope))
       x_difference = float(self.line[1][0] - self.line[0][0])
       if x_difference < 0:
           angle += 180
       if x_difference == 0:
           y_difference = float(self.line[1][1] - self.line[0][1])
           if y_difference < 0:
               angle += 180
       if angle < 0:
           angle += 360
       # This still gives out 360 due to float issues.
       return angle


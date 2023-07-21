import cv2
import numpy as np
import random
import math
from operator import itemgetter

def nothing(x):
    pass

def draw_region(image, poly):
    # WIZUALIZACJA OBSZARU ZAINTERESOWANIA
    height = image.shape[0]
    width = image.shape[1]
    image_copy = image
    mask = np.zeros_like(image_copy)
    contours = np.array( [ [round(poly[0]*width), round(poly[1]*height)],
                           [round(poly[2]*width), round(poly[3]*height)],
                           [round(poly[4]*width), round(poly[5]*height)],
                           [round(poly[6]*width), round(poly[7]*height)]
                           ])
    cv2.fillPoly(mask, pts=[contours], color=(255, 0, 0))
    dst = cv2.addWeighted(image_copy,1,mask,0.7,1)
    return dst

def region_of_interest(image, poly):
    # MASKA OBSZARU ZAINTERESOWANIA
    height = image.shape[0]
    width = image.shape[1]
    polygons = np.array([[
                        (round(poly[0]*width), round(poly[1]*height)),              #1  BOT LEFT
                        (round(poly[2]*width), round(poly[3]*height)),              #2  BOT RIGHT
                        (round(poly[4]*width), round(poly[5]*height)),              #3  TOP RIGHT
                        (round(poly[6]*width), round(poly[7]*height))               #4  TOP LEFT
                        ]])
    mask = np.zeros_like(image) #maska = caly czarny obraz
    cv2.fillPoly(mask, polygons, (255,255,255)) #wypelnia bialy obiekt triangle w masce
    dst = cv2.bitwise_and(image,mask)

    return dst

def display_lines(image_BGR, lines, color = 'random'):
    # WYŚWIETLANIE LINII
    line_image = np.zeros_like(image_BGR)
    if lines is not None:
        for num,line in enumerate(lines):
            b = random.randint(0, 255)
            g = random.randint(0, 255)
            r = random.randint(0, 255)
            if color != 'random':
                b=255*int(color=='blue')
                g=255*int(color=='green')
                r=255*int(color=='red')

            x1, y1, x2, y2 = line[0:4]
            cv2.line(line_image, (x1, y1), (x2, y2), (b, g, r), 2)
            # (img, text, position, font, size, color, LineWidth, anti-alliasing)
            if color == 'random':
                line_image = show_angles(line_image, line, b, g, r)
            #cv2.circle(line_image, (x1, y1), 5, (0, 0, 255), -1)  # thickness, color, -1 = fill    #Początek lini

    return line_image

def show_angles(image, line, b, g, r):
    # WYŚWIETLANIE KĄTÓW OBOK LINII, W TYM SAMYM KOLORZE
    line_slope = get_slope(line)
    line_angle = get_angle(line_slope)
    line_center = get_center(line)

    image = cv2.putText(image, str(line_angle),(line_center), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (b, g, r), 1, cv2.LINE_AA )
    return image

def display_arrow_tip(arrow_tip, line_image):
    #WYŚWIETLANIE PUNKTÓW PRZECIĘĆ GROTÓW STRZAŁEK
    if arrow_tip:
        for point in arrow_tip:
            corner_x = point[0][0]
            corner_y = point[0][1]
            cv2.circle(line_image, (corner_x,corner_y), 5, (0, 0, 255), -1)  # thickness, color, -1 = fill
    return line_image

def group_lines(lines,angle_range):# returns array of lines with angle between given values
    # ZWRACA LINIE ZNAJDUJĄCE SIĘ W PODANYM ZAKRESIE
    lanes_in_range = []
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            line_slope = get_slope(line[0])
            line_angle = get_angle(line_slope)
            if abs(line_angle) in range(angle_range[0],angle_range[1]):
                lanes_in_range.append([x1,y1,x2,y2,line_angle, line_length(line[0])])
    return lanes_in_range

def group_divide(lanes_array):
    # DZIELI LISTE NA KĄTY DODATNIE I UJEMNE
    positive_angle = []
    negative_angle = []
    for i,lane in enumerate(lanes_array):
        if lane[4] > 1:
            positive_angle.append(lane)
        elif lane[4] < -1:
            negative_angle.append(lane)
    #print(len(positive_angle),len(negative_angle))
    #print(positive_angle)
    return positive_angle,negative_angle

def find_corner(positive,negative):
    # NADAJE ETYKIETĘ ZWROTU STRZAŁKI
    corners = []
    if positive is not None and negative is not None:
        for pos_line in positive:
            for neg_line in negative:
                if points_touch(pos_line,neg_line,5,5)=='FWD':
                    corners.append([pos_line,neg_line, 'FWD'])

                if points_touch(pos_line,neg_line,5,5)=='LEFT':
                    corners.append([pos_line, neg_line, 'LEFT'])

                if points_touch(pos_line,neg_line,5,5)=='RIGHT':
                    corners.append([pos_line, neg_line, 'RIGHT'])

                if points_touch(pos_line,neg_line,10,10)=='DWN':
                    corners.append([pos_line, neg_line, 'DWN'])

    return corners

def points_touch(pos_line, neg_line, offset_x, offset_y):
    # ZWRACA ODPOWIEDNIĄ ETYKIETĘ NA PODSTAWIE WZAJEMNEGO UŁOŻENIA LINII
    if abs(pos_line[0]-neg_line[2])<offset_x and abs(pos_line[1]-neg_line[3])<offset_y:
        return 'FWD'
    elif abs(pos_line[0]-neg_line[0])<offset_x and abs(pos_line[1]-neg_line[1])<offset_y:
        return 'LEFT'
    elif abs(pos_line[2]-neg_line[2])<offset_x and abs(pos_line[3]-neg_line[3])<offset_y:
        return 'RIGHT'
    elif abs(pos_line[2]-neg_line[0])<offset_x and abs(pos_line[3]-neg_line[1])<offset_y:
        return 'DWN'

def remove_duplicates(lines, coordinate, n=2):  #remove numbers that are -n:n close from coordinate (0 for X, 1 for Y)
    # USUWA Z LISTY DUPLIKATY
    if len(lines)>1:
        lines = lines_sort(lines)
        nearVals = set()
        new_lines = []
        for line in lines:
            if line[coordinate] not in nearVals:
                new_lines.append(line)

                for near_val in range(line[coordinate]-n, line[coordinate]+n):
                    nearVals.add(near_val)
            # else: print(str(line)+' duplicate removed')
        return new_lines
    return lines

def lines_sort(lines):
    # SORTUJE LINIE NA PODSTAWIE DŁUGOŚCI
    lines_sorted = sorted(lines, key=itemgetter(5), reverse=True)   #sorts by lenght of line, from longest to shortest
    return lines_sorted

def get_center(line):
    # OBLICZA GEOMETRYCZNY ŚRODEK LINII
    return (round((line[0]+line[2])/2),round((line[1]+line[3])/2))

def get_slope(line):
    # NACHYLENIE LINII ( TANGENS )
    if line[2]!=line[0]:
        a = (line[3]-line[1])/(line[2]-line[0])
    else:
        a = 58
    return a

def get_angle(slope):
    return round(math.atan(slope) * 180 / math.pi)

def line_length(line):
    # DŁUGOŚĆ LINII
    return round(math.sqrt((line[0] - line[2])**2 + (line[1] - line[3])**2))

def length_filter(lines, thresh):
    # FILTRUJE LINIE SPOZA ZAKRESU
    filtered_lines = []
    for line in lines:
        if line[5]in range(thresh[0], thresh[1]):
            filtered_lines.append(line)
    return filtered_lines

def isLight(image):
    # TWORZY MASKĘ NA OBSZARZE O JASNOŚCI W PODANYM ZAKRESIE
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 40])
    upper_white = np.array([360, 20, 255])
    mask = cv2.inRange(hsv_image, lower_white, upper_white)
    return mask

def display_corners(edge_image, dst, maxCorn, quality, distance):
    # WYŚWIETLA NAROŻNIKI (PRZECIĘCIA)
    dst2 = np.zeros_like(dst)
    corners = cv2.goodFeaturesToTrack(edge_image, maxCorn, quality, distance)  # (img, maxCorners, quality ratio, minDistance)
    if corners is not None:
        corners = np.int0(corners) #usuwa czesc decymalną
        print('corners: '+ str(corners))
        for corner in corners:
            x, y = corner.ravel()   #odpakowuje x,y
            cv2.circle(dst2, (x, y), 5, (0,0,255),-1)    #thickness, color, -1 = fill
    return dst2

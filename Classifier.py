
from filters import points_touch
from gui import showDetection

def classify(img, lines_fwd, lines_turn, lines_vertical, lines_horizontal):
    if lines_fwd or lines_turn or lines_horizontal or lines_vertical:
        img = img.copy()
        fwd_occured = 0
        right_occured = 0
        left_occured = 0
        dwn_occured = 0
        for line_fwd in lines_fwd:  #COUNTING LABELS
            if line_fwd[-1]=='FWD':         #[-1] last element of array
                fwd_occured += 1
            if line_fwd[-1]=='DWN':
                dwn_occured += 1
        for line_turn in lines_turn:
            if line_turn[-1]=='LEFT':
                left_occured += 1
            if line_turn[-1]=='RIGHT':
                right_occured += 1
        if lines_fwd and lines_vertical and fwd_occured:
            if lines_turn and left_occured:                                 #LEFT FORWARD
                img = left_fwd_arrow(img, lines_turn, lines_fwd, lines_vertical)
            elif lines_turn and right_occured:                              #RIGHT FORWARD
                img = right_fwd_arrow(img, lines_turn, lines_fwd, lines_vertical)
            else:
                img = fwd_arrow(img, lines_fwd, lines_vertical)             #FORWARD

        elif lines_turn and lines_vertical and left_occured:                  #LEFT
            img = left_arrow(img, lines_turn, lines_vertical)

        elif lines_turn and lines_vertical and right_occured:                 #RIGHT
            img = right_arrow(img, lines_turn, lines_vertical)

        elif lines_fwd and lines_vertical and dwn_occured:              #TRIANGLE
            img = triangle(img, lines_fwd, lines_horizontal)

    return img

def triangle(img, lines_dwn, lines_horizontal):
    for lines in lines_dwn:
        if lines[-1]=='DWN':
            if abs(lines[0][4])+abs(lines[1][4]) in range(100,140): #if the angle is in range
                for hor_line in lines_horizontal:
                    if points_touch(hor_line, lines[1], 10, 10) or points_touch(lines[0], hor_line, 10, 10):
                        topleft = (lines[0][0] - 10, lines[0][1] - 10)
                        botright = (lines[1][2] + 10, lines[1][1] + 30)
                        print(topleft,botright)
                        img = showDetection(img, botright, topleft, 'YIELD TRIANGLE')
    return img

def fwd_arrow(img, lines_fwd, lines_vertical,offset=15):
    if len(lines_vertical)>1:
        x1 = min(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2])-offset
        x2 = max(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2])+offset
        # cv2.line(img, (x1, 0), (x1, 720), (255, 0, 0), 2)
        # cv2.line(img, (x2, 0), (x2, 720), (255, 0, 0), 2)
        if lines_fwd[0][0][0] in range(x1,x2):
            botright_y = 0
            for line in lines_vertical:  # calculating highest y for botright point
                if max(line[1], line[3]) > botright_y:
                    botright_y = max(line[1], line[3])

            topleft = (lines_fwd[0][1][0] - 10, lines_fwd[0][1][3] - 10)
            botright = (lines_fwd[0][0][2] + 10, botright_y + 10)
            img = showDetection(img, botright, topleft, 'FWD ARROW')
    return img

def left_arrow(img, lines_turn, lines_vertical):
    if len(lines_vertical) > 1:
        x1 = lines_turn[0][1][0] + 30
        x2 = lines_turn[0][1][0] + 250
        botright_y = 0
        for line in lines_vertical:
            if line[0] in range(x1, x2):
                if max(line[1], line[3]) > botright_y:
                    botright_y = max(line[1], line[3])
                topleft = (lines_turn[0][0][0] - 10, lines_turn[0][1][3] - 10)
                botright = (line[0] + 10, botright_y + 10)
                img = showDetection(img, botright, topleft, 'LEFT ARROW')
                break  # breaks if object detected
    return img

def right_arrow(img, lines_turn, lines_vertical):
    if len(lines_vertical)>1:
        x1 = lines_turn[0][0][0] - 250
        x2 = lines_turn[0][0][0] - 30
        #cv2.line(img,(x1,0),(x1,720),(255,0,0),2)
        #cv2.line(img, (x2, 0), (x2, 720), (255, 0, 0), 2)
        #print(lines_vertical)
        botright_y = 0
        for line in lines_vertical:
            if line[0] in range(x1,x2):
                if max(line[1], line[3]) > botright_y:
                    botright_y = max(line[1], line[3])
                topleft = (line[0] - 10, lines_turn[0][0][1] - 10)
                botright = (lines_turn[0][0][2] + 10, botright_y + 10)
                img = showDetection(img, botright, topleft, 'RIGHT ARROW')
                break   # breaks if object detected
    return img

def left_fwd_arrow(img, lines_turn, lines_fwd, lines_vertical, offset=15):
    arrow_order = False
    if len(lines_vertical) > 1:
        x1 = min(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2]) - offset
        x2 = max(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2]) + offset
        for line_fwd in lines_fwd:
            if line_fwd[-1] == 'FWD':
                saved_fwd_line = line_fwd         #saves 1 forward arrow line
        for line_turn in lines_turn:
            if line_turn[-1] == 'LEFT':
                if line_turn[0][0] < saved_fwd_line[0][0]:    #if line turn (left) is on the left of fwd_line (forward)
                    saved_turn_line = line_turn      #saves 1 turn arrow line
                    arrow_order = True
        if saved_fwd_line[0][0] in range(x1, x2) and arrow_order:
            botright_y = 0
            for line in lines_vertical:  # calculating highest y for botright point
                if max(line[1], line[3]) > botright_y:
                    botright_y = max(line[1], line[3])
            topleft = (saved_turn_line[1][0] - 10, saved_fwd_line[1][3] - 10)
            botright = (saved_fwd_line[0][2] + 10, botright_y + 10)
            img = showDetection(img, botright, topleft, 'LEFT FWD ARROW')
    return img

def right_fwd_arrow(img, lines_turn, lines_fwd, lines_vertical, offset=15):
    arrow_order = False
    if len(lines_vertical) > 1:
        x1 = min(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2]) - offset
        x2 = max(lines_vertical[0][0], lines_vertical[0][2], lines_vertical[1][0], lines_vertical[1][2]) + offset
        for line_fwd in lines_fwd:
            if line_fwd[-1] == 'FWD':
                saved_fwd_line = line_fwd         #saves 1 forward arrow line
        for line_turn in lines_turn:
            if line_turn[-1] == 'RIGHT':
                if line_turn[0][0] > saved_fwd_line[0][0]:    #if line turn (right) is on the right of fwd_line (forward)
                    saved_turn_line = line_turn      #saves 1 turn arrow line
                    arrow_order = True
        if saved_fwd_line[0][0] in range(x1, x2) and arrow_order:
            botright_y = 0
            for line in lines_vertical:  # calculating highest y for botright point
                if max(line[1], line[3]) > botright_y:
                    botright_y = max(line[1], line[3])
            topleft = (saved_fwd_line[1][0] - 10, saved_fwd_line[1][3] - 10)
            botright = (saved_turn_line[0][2] + 10, botright_y + 10)
            img = showDetection(img, botright, topleft, 'RIGHT FWD ARROW')
    return img

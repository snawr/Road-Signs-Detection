import cv2
import numpy as np
import time
import os
from matplotlib import pyplot as plt
def nothing(x):
    pass

def eval_fps(frames):
    global startTime
    global fps
    if frames == 0:
        startTime = time.time()
    else:
        elapsedTime = time.time() - startTime
        fps = round(frames/elapsedTime)
        return fps

def screenshot(images):
    ### TO BE DEBUGGED ###
    # now = time.localtime()
    # now_date = str(now[2]) + '.' + str(now[1]) + '_[' + str(now[3]) + '-' + str(now[4]) + '-' + str(now[5]) + ']'
    # path = os.path.join(r"C:\Users\Szymon\Desktop\Inżynierka\opencv\screenshots",str(now_date))
    # print(path)
    # os.mkdir(path)
    # os.chdir(path)
    # for i,image in enumerate(images):
    #     cv2.imwrite(str(i+1)+'.jpg', image)
    #     print('screenshot taken')
    pass

def skipBlurry(image, threshold, variance_array, plot=False):
    LaplacianVar = round(cv2.Laplacian(image, cv2.CV_8U).var())     #calc laplacian var
    variance_array.append(LaplacianVar)     #add var to var array
    if plot:
        plt.plot(variance_array)
        threshold_line = np.ones_like(variance_array) * threshold
        plt.plot(threshold_line)
        plt.show()
    return variance_array, LaplacianVar < threshold

def showDetection(img,botright, topleft, text):
    img = img.copy()
    cv2.putText(img, text, (topleft[0], topleft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1,
                cv2.LINE_AA)
    img = cv2.rectangle(img, topleft, botright, (0, 255, 0), 2)
    return img
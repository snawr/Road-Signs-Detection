# ŹRÓDŁO: https://github.com/gunshi/thresholding
#
import cv2
from avgfilter import average_filter
import numpy as np

def nick(image, window=(15, 15), k=-0.2, padding='edge'):
    image = image.astype(float)
    mean = average_filter(image, window, padding)

    mean_square = average_filter(image ** 2, window, padding)
    variance = mean_square - mean**2

    threshold = mean + k * np.sqrt(variance + mean**2)
    output = image > threshold   
    output = _binarize_color(output)
    return output


def _binarize_color(output):
    return output.astype(np.uint8) * 255

import cv2 as cv
from typing import Tuple


def get_center_coordinates_and_area(contour) -> Tuple[int, int, float]:
    M = cv.moments(contour)
    
    if M['m00']:
        contour_x: int = int(M['m10'] / M['m00'])
        contour_y: int = int(M['m01'] / M['m00'])
        
        return (contour_x, contour_y, M['m00'])
    
    return (-1, -1, M['m00'])
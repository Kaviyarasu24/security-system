import cv2
import numpy as np


def detect_color(vehicle_crop):

    try:

        resized = cv2.resize(
            vehicle_crop,
            (100, 100)
        )

        pixels = resized.reshape(
            (-1, 3)
        )

        avg_color = np.mean(
            pixels,
            axis=0
        )

        b, g, r = avg_color

        brightness = (
            r + g + b
        ) / 3

        if brightness > 180:
            return "WHITE"

        elif brightness < 60:
            return "BLACK"

        elif r > g and r > b:
            return "RED"

        elif g > r and g > b:
            return "GREEN"

        elif b > r and b > g:
            return "BLUE"

        else:
            return "SILVER"

    except Exception:

        return "UNKNOWN"
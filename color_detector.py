import cv2
import numpy as np


def detect_color(vehicle_crop):

    try:

        height, width = vehicle_crop.shape[:2]

        if height == 0 or width == 0:
            return "UNKNOWN"

        # Focus on the center area to reduce background influence.
        top = int(height * 0.2)
        bottom = int(height * 0.8)
        left = int(width * 0.2)
        right = int(width * 0.8)

        center_crop = vehicle_crop[top:bottom, left:right]

        if center_crop.size == 0:
            center_crop = vehicle_crop

        resized = cv2.resize(
            center_crop,
            (160, 160)
        )

        hsv = cv2.cvtColor(
            resized,
            cv2.COLOR_BGR2HSV
        )

        h, s, v = cv2.split(hsv)

        # Remove weakly colored pixels so shadows and highlights influence less.
        mask = (
            (s > 35)
            & (v > 45)
        )

        if np.count_nonzero(mask) < 50:
            mean_v = float(np.mean(v))

            if mean_v > 210:
                return "WHITE"

            if mean_v < 55:
                return "BLACK"

            return "SILVER"

        h_values = h[mask]
        s_values = s[mask]
        v_values = v[mask]

        hue = float(np.median(h_values))
        saturation = float(np.mean(s_values))
        value = float(np.mean(v_values))

        if value > 210 and saturation < 40:
            return "WHITE"

        if value < 55:
            return "BLACK"

        if saturation < 40:
            return "SILVER"

        if hue < 10 or hue >= 170:
            return "RED"

        if hue < 25:
            return "ORANGE"

        if hue < 40:
            return "YELLOW"

        if hue < 85:
            return "GREEN"

        if hue < 130:
            return "BLUE"

        if hue < 170:
            return "PURPLE"

        return "SILVER"

    except Exception:

        return "UNKNOWN"
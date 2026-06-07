from ultralytics import YOLO


class PlateDetector:

    def __init__(self):

        self.model = YOLO(
            "models/license_plate_detector.pt"
        )

    def detect(self, image):

        return self.model(
            image,
            verbose=False
        )
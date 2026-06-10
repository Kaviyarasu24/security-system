from ultralytics import YOLO

# COCO class IDs for vehicles we care about:
# 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASS_IDS = [2, 3, 5, 7]


class VehicleDetector:

    def __init__(self):

        self.model = YOLO("yolo11n.pt")

    def track(self, frame):

        return self.model.track(
            frame,
            persist=True,
            verbose=False,
            classes=VEHICLE_CLASS_IDS
        )
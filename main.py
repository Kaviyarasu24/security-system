import cv2
import os

from datetime import datetime

from detector import VehicleDetector
from tracker import LineCounter


# ====================================
# CONFIGURATION
# ====================================

VIDEO_PATH = "videos/input1.mp4"

LINE_Y = 350


# ====================================
# CREATE FOLDERS
# ====================================

os.makedirs("snapshots", exist_ok=True)


# ====================================
# INITIALIZE
# ====================================

detector = VehicleDetector()

counter = LineCounter(line_y=LINE_Y)

vehicle_records = {}

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():

    print("Error opening video")

    exit()

print("Video opened successfully")


# ====================================
# MAIN LOOP
# ====================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("End of video reached")

        break

    results = detector.track(frame)

    # Draw Entry Line
    cv2.line(
        frame,
        (0, LINE_Y),
        (frame.shape[1], LINE_Y),
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        "ENTRY LINE",
        (20, LINE_Y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()

        ids = results[0].boxes.id.cpu().numpy()

        classes = results[0].boxes.cls.cpu().numpy()

        names = results[0].names

        for box, track_id, cls_id in zip(
            boxes,
            ids,
            classes
        ):

            x1, y1, x2, y2 = map(int, box)

            track_id = int(track_id)

            vehicle_type = names[int(cls_id)]

            center_x = int((x1 + x2) / 2)

            center_y = int((y1 + y2) / 2)

            # Draw center point
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (0, 255, 0),
                -1
            )

            status = counter.check_crossing(
                track_id,
                center_y
            )

            if status == "ENTRY":

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d_%H-%M-%S"
                )

                image_path = (
                    f"snapshots/"
                    f"vehicle_{track_id}_{timestamp}.jpg"
                )

                vehicle_crop = frame[
                    max(0, y1):y2,
                    max(0, x1):x2
                ]

                cv2.imwrite(
                    image_path,
                    vehicle_crop
                )

                vehicle_records[track_id] = {

                    "id": track_id,

                    "type": vehicle_type,

                    "entry_time": timestamp,

                    "image": image_path
                }

                print("\n========== ENTRY ==========")

                print(
                    f"Vehicle ID : {track_id}"
                )

                print(
                    f"Type       : {vehicle_type}"
                )

                print(
                    f"Time       : {timestamp}"
                )

                print(
                    f"Image      : {image_path}"
                )

                print("===========================\n")

    annotated_frame = results[0].plot()

    # Draw line again on final frame
    cv2.line(
        annotated_frame,
        (0, LINE_Y),
        (frame.shape[1], LINE_Y),
        (0, 0, 255),
        3
    )

    cv2.putText(
        annotated_frame,
        "ENTRY LINE",
        (20, LINE_Y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    cv2.imshow(
        "Vehicle Entry Monitoring",
        annotated_frame
    )

    key = cv2.waitKey(30)

    if key == 27:
        break


# ====================================
# DISPLAY SAVED DATA
# ====================================

print("\nVehicle Records\n")

for vehicle_id, data in vehicle_records.items():

    print(data)


# ====================================
# CLEANUP
# ====================================

cap.release()

cv2.destroyAllWindows()
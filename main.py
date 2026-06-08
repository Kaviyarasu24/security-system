import cv2
import os
from datetime import datetime

from detector import VehicleDetector
from tracker import LineCounter
from plate_detector import PlateDetector
from plate_reader import read_plate
from color_detector import detect_color
from report_generator import generate_reports, append_daily_excel

# ====================================
# CONFIG
# ====================================

VIDEO_PATH = "videos/input1.mp4"

LINE_Y = 350

# ====================================
# FOLDERS
# ====================================

os.makedirs("snapshots", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ====================================
# INITIALIZE
# ====================================

vehicle_detector = VehicleDetector()
plate_detector = PlateDetector()

counter = LineCounter(LINE_Y)

vehicle_records = {}

# ====================================
# VIDEO
# ====================================

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Video open failed")
    exit()

print("Video opened successfully")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 20

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

video_writer = cv2.VideoWriter(
    "outputs/output_detected.mp4",
    fourcc,
    fps,
    (frame_width, frame_height)
)

# ====================================
# PROCESS VIDEO
# ====================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("End of video reached")
        break

    results = vehicle_detector.track(frame)

    annotated_frame = results[0].plot()

    # Entry line
    cv2.line(
        annotated_frame,
        (0, LINE_Y),
        (frame_width, LINE_Y),
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

            track_id = int(track_id)

            x1, y1, x2, y2 = map(
                int,
                box
            )

            vehicle_type = names[int(cls_id)]

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            cv2.circle(
                annotated_frame,
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

                # ==========================
                # VEHICLE CROP
                # ==========================

                vehicle_crop = frame[
                    max(0, y1):y2,
                    max(0, x1):x2
                ]

                if vehicle_crop.size == 0:
                    continue

                vehicle_color = detect_color(
                    vehicle_crop
                )

                vehicle_image = (
                    f"snapshots/vehicle_{track_id}.jpg"
                )

                cv2.imwrite(
                    vehicle_image,
                    vehicle_crop
                )

                # ==========================
                # PLATE DETECTION
                # ==========================

                plate_text = "UNKNOWN"

                plate_image = None

                debug_plate_path = None

                plate_results = plate_detector.detect(
                    vehicle_crop
                )

                if len(plate_results[0].boxes) > 0:

                    pbox = (
                        plate_results[0]
                        .boxes
                        .xyxy[0]
                        .cpu()
                        .numpy()
                    )

                    px1, py1, px2, py2 = map(
                        int,
                        pbox
                    )

                    # safety padding

                    padding = 10

                    px1 = max(
                        0,
                        px1 - padding
                    )

                    py1 = max(
                        0,
                        py1 - padding
                    )

                    px2 = min(
                        vehicle_crop.shape[1],
                        px2 + padding
                    )

                    py2 = min(
                        vehicle_crop.shape[0],
                        py2 + padding
                    )

                    plate_crop = vehicle_crop[
                        py1:py2,
                        px1:px2
                    ]

                    if plate_crop.size != 0:

                        plate_image = (
                            f"snapshots/plate_{track_id}.jpg"
                        )

                        cv2.imwrite(
                            plate_image,
                            plate_crop
                        )

                        debug_plate = cv2.resize(
                            plate_crop,
                            None,
                            fx=4,
                            fy=4,
                            interpolation=cv2.INTER_CUBIC
                        )

                        debug_plate_path = (
                            f"snapshots/debug_plate_{track_id}.jpg"
                        )

                        cv2.imwrite(
                            debug_plate_path,
                            debug_plate
                        )

                        plate_text = read_plate(
                            plate_crop
                        )

                # ==========================
                # STORE RECORD
                # ==========================

                vehicle_records[track_id] = {

                    "id": track_id,

                    "type": vehicle_type,

                    "color": vehicle_color,

                    "plate": plate_text,

                    "entry_time": timestamp,

                    "vehicle_image": vehicle_image,

                    "plate_image": plate_image,

                    "debug_plate_image": debug_plate_path
                }

                # ==========================
                # PRINT
                # ==========================

                print()
                print("=" * 50)

                print(
                    f"Vehicle ID : {track_id}"
                )

                print(
                    f"Type       : {vehicle_type}"
                )

                print(
                    f"Color      : {vehicle_color}"
                )

                print(
                    f"Plate      : {plate_text}"
                )

                print(
                    f"Time       : {timestamp}"
                )

                print(
                    f"Vehicle Img: {vehicle_image}"
                )

                print(
                    f"Plate Img  : {plate_image}"
                )

                print(
                    f"Debug Img  : {debug_plate_path}"
                )

                print("=" * 50)

    # Save processed frame
    video_writer.write(
        annotated_frame
    )

# ====================================
# CLEANUP
# ====================================

video_writer.release()
cap.release()

# ====================================
# FINAL REPORT
# ====================================

print("\nFINAL VEHICLE RECORDS\n")

for vehicle_id, data in vehicle_records.items():
    print(data)

# Generate CSV / Excel report
# Write daily Excel report (DD_MM_YYYY.xlsx). Appends if file exists.
daily_path = append_daily_excel(vehicle_records)

print(
    "\nSaved Video: outputs/output_detected.mp4"
)

if daily_path:
    print(f"Saved Daily Excel Report: {daily_path}")
else:
    print("Failed to write daily Excel report (file may be open).")
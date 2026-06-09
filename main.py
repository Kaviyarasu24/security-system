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

VIDEO_PATH = "videos/input3.mp4"

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

                # create dated snapshots folder and sanitized type name
                date_folder = datetime.now().strftime("%d_%m_%Y")
                snapshots_dir = os.path.join("snapshots", date_folder)
                os.makedirs(snapshots_dir, exist_ok=True)

                safe_type = str(vehicle_type).replace(" ", "_")

                vehicle_image = (
                    f"{snapshots_dir}/{safe_type}_{track_id}_{timestamp}.jpg"
                )

                cv2.imwrite(vehicle_image, vehicle_crop)

                # ==========================
                # PLATE DETECTION
                # ==========================

                plate_text = "UNKNOWN"

                plate_image = None

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
                            f"{snapshots_dir}/{track_id}_plate_image_{timestamp}.jpg"
                        )

                        cv2.imwrite(plate_image, plate_crop)

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

                    "plate_image": plate_image
                }

                # update the daily Excel report immediately after each new record
                daily_path = append_daily_excel({track_id: vehicle_records[track_id]})

                # ==========================
                # PRINT
                # ==========================

                print()
                print("=" * 50)


                if daily_path:
                    print(
                        f"Daily Excel Updated: {daily_path}"
                    )
                else:
                    print(
                        "Daily Excel update failed (file may be open)."
                    )
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

                # debug plate images are no longer saved

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

print(
    "\nSaved Video: outputs/output_detected.mp4"
)
import cv2

from detector import VehicleDetector
from tracker import LineCounter

# ==========================
# Configuration
# ==========================

VIDEO_PATH = "videos/BMW_320I_2018_black_1.mp4"

LINE_Y = 350

# ==========================
# Initialize
# ==========================

detector = VehicleDetector()

counter = LineCounter(line_y=LINE_Y)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Error opening video")
    exit()

print("Video opened successfully")

# ==========================
# Processing Loop
# ==========================

while True:

    ret, frame = cap.read()

    if not ret:
        print("End of video reached")
        break

    # YOLO Tracking
    results = detector.track(frame)

    # Draw virtual boundary line
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

    # Process tracked vehicles
    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()

        ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(boxes, ids):

            x1, y1, x2, y2 = map(int, box)

            track_id = int(track_id)

            # Vehicle center point
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

            # Check line crossing
            status = counter.check_crossing(
                track_id,
                center_y
            )

            if status:

                print(
                    f"Vehicle ID {track_id} {status}"
                )

                cv2.putText(
                    frame,
                    f"{status}",
                    (x1, y1 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

    # Draw YOLO detections
    annotated_frame = results[0].plot()

    # Draw line again on annotated frame
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
        "Vehicle Entry Detection",
        annotated_frame
    )

    key = cv2.waitKey(30)

    if key == 27:
        break

# ==========================
# Cleanup
# ==========================

cap.release()
cv2.destroyAllWindows()
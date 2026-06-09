# Security System

## About

This project is a lightweight vehicle detection and logging system that analyzes CCTV footage or video input to detect, track, and record vehicles crossing an entry line. For each vehicle it captures: type (via YOLO), license plate (if detected), timestamp, and cropped snapshots. It also generates an annotated output video and updates a daily Excel report while the video is running.

## How it works

- `main.py` opens a video or CCTV stream source (set `VIDEO_PATH`) and processes frames.
- `detector.py` uses an Ultralytics YOLO model (`yolo11n.pt`) to detect and track vehicles.
- `tracker.py` (`LineCounter`) tracks object center positions and flags vehicles that cross the configured entry line (set `LINE_Y`).
- On an ENTRY event, `main.py` crops the vehicle, saves a vehicle snapshot, attempts license plate detection with `plate_detector.py` (YOLO model in `models/license_plate_detector.pt`), and reads plates using `plate_reader.py` (EasyOCR).
- Snapshots are saved inside a date-based folder under `snapshots/DD_MM_YYYY/`.
- The daily Excel report is written to `reports/DD_MM_YYYY.xlsx` and is updated immediately whenever a new vehicle is recorded.
- An annotated video is written to `outputs/output_detected.mp4`.

## Files of interest

- `main.py` — main processing script (configurable constants `VIDEO_PATH`, `LINE_Y`).
- `detector.py` — vehicle detector wrapper (uses `yolo11n.pt`).
- `plate_detector.py` — license plate detector (uses `models/license_plate_detector.pt`).
- `plate_reader.py` — OCR using EasyOCR to read plate text.
- `tracker.py` — line-crossing tracker (`LineCounter`).
- `report_generator.py` — writes CSV/Excel reports; daily Excel reports are stored in `reports/`.
- `requirements.txt` — Python dependencies (may require adding `easyocr` and `torch` depending on your system).

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
# Also install missing packages if not listed:
pip install easyocr torch torchvision
```

Notes:
- `ultralytics` may require a compatible `torch` installation; visit https://pytorch.org/ for the correct `pip` command for your CUDA/CUDA-less setup.
- EasyOCR can use GPU if built with CUDA; in this repo `gpu=False` is used by default.

## Models

- `yolo11n.pt` — vehicle detection model (included in repository root).
- `models/license_plate_detector.pt` — license plate detector (located in `models/`).

If you replace or update models, ensure the file paths in `detector.py` and `plate_detector.py` remain correct.

## Running

1. Place or update the input video path in `main.py`:

```py
VIDEO_PATH = "videos/input1.mp4"
```

2. Run the main script:

```bash
python main.py
```

3. Outputs produced:
- Annotated video: `outputs/output_detected.mp4`
- Vehicle crops: `snapshots/DD_MM_YYYY/<vehicle_type>_<id>_<timestamp>.jpg`
- Plate crops: `snapshots/DD_MM_YYYY/<id>_plate_image_<timestamp>.jpg`
- Daily Excel report: `reports/DD_MM_YYYY.xlsx`
- Console printout with the final `vehicle_records` summary.

## Notes & Tips

- Color detection has been removed from the current pipeline.
- OCR accuracy depends on crop quality; improving plate detector or preprocessing may help.
- For real-time or high-performance use, run on a machine with a GPU and install CUDA-enabled `torch`.
- The daily Excel report is updated during runtime, so the file may stay open while CCTV is running.

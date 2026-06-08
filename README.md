# Security System

## About

This project is a lightweight vehicle detection and logging system that analyzes input video to detect, track, and record vehicles crossing an entry line. For each vehicle it captures: type (via YOLO), approximate color, license plate (if detected), timestamp, and cropped snapshots. It also generates an annotated output video.

## How it works

- `main.py` opens a video (set `VIDEO_PATH`) and processes frames.
- `detector.py` uses an Ultralytics YOLO model (`yolo11n.pt`) to detect and track vehicles.
- `tracker.py` (`LineCounter`) tracks object center positions and flags vehicles that cross the configured entry line (set `LINE_Y`).
- On an ENTRY event, `main.py` crops the vehicle, saves a vehicle snapshot, determines color via `color_detector.py`, attempts license plate detection with `plate_detector.py` (YOLO model in `models/license_plate_detector.pt`), and reads plates using `plate_reader.py` (EasyOCR).
- Snapshots and debug crops are saved to `snapshots/`. An annotated video is written to `outputs/output_detected.mp4`.

## Files of interest

- `main.py` — main processing script (configurable constants `VIDEO_PATH`, `LINE_Y`).
- `detector.py` — vehicle detector wrapper (uses `yolo11n.pt`).
- `plate_detector.py` — license plate detector (uses `models/license_plate_detector.pt`).
- `plate_reader.py` — OCR using EasyOCR to read plate text.
- `color_detector.py` — simple average-color based color estimator.
- `tracker.py` — line-crossing tracker (`LineCounter`).
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
- Vehicle crops: `snapshots/vehicle_<id>.jpg`
- Plate crops: `snapshots/plate_<id>.jpg`
- Debug plate crops: `snapshots/debug_plate_<id>.jpg`
- Console printout with final `vehicle_records` summary.

## Notes & Tips

- The color detector uses a simple average RGB heuristic and may be inaccurate for small or occluded crops.
- OCR accuracy depends on crop quality; improving plate detector or preprocessing may help.
- For real-time or high-performance use, run on a machine with a GPU and install CUDA-enabled `torch`.
- `report_generator.py` is currently empty — you can add reporting/export features (CSV, Excel) using `pandas`/`openpyxl`.

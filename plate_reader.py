import cv2
import easyocr
import re

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


def read_plate(plate_crop):

    try:

        plate_crop = cv2.resize(
            plate_crop,
            None,
            fx=4,
            fy=4,
            interpolation=cv2.INTER_CUBIC
        )

        gray = cv2.cvtColor(
            plate_crop,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.bilateralFilter(
            gray,
            11,
            17,
            17
        )

        results = reader.readtext(
            gray,
            detail=1,
            paragraph=True
        )

        if not results:
            return "UNKNOWN"

        full_text = ""

        for result in results:

            text = result[1]

            full_text += text + " "

        full_text = full_text.strip()

        full_text = re.sub(
            r'[^A-Z0-9]',
            '',
            full_text.upper()
        )


        return full_text

    except Exception as e:

        print("OCR Error:", e)

        return "UNKNOWN"
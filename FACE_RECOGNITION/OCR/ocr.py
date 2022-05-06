import os
import re
import cv2
import imutils
import numpy as np
import pytesseract
from PIL import Image


def detect_id(image):
    image = imutils.resize(image, 1024, 665)
    h0, w0 = image.shape[:2]
    h = int(h0 / 4) + 5
    strs = ["" for x in range(4)]
    for i in range(4):
        im = image[h * i:h * (i + 1), :]
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
        gray = cv2.medianBlur(gray, 3)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        strs[i] = text.strip().replace("\n", " ").strip()
    # post process
    id_num = None
    for line in strs:
        texts = line.split()
        if len(texts) > 1:
            for txt in texts:
                # checking only digits
                txt = re.sub("[^0-9]", "", txt)
                if len(txt) == 10:
                    id_num = txt
    return id_num

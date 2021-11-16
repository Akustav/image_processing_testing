import image_processor

import cv2
import numpy as np

import time

processor = image_processor.ImageProcessor(debug=True)

processor.start()

while True:
    processedData = processor.process_frame()

    debug_frame = processedData.debug_frame

    cv2.imshow('debug', debug_frame)

    k = cv2.waitKey(1) & 0xff
    if k == ord('q'):
        break

processor.stop()
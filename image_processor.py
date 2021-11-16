import camera
import segment
import _pickle as pickle
import numpy as np
import cv2

class Object():
    def __init__(self, x = -1, y = -1, size = -1, distance = -1, exists = False):
        self.x = x
        self.y = y
        self.size = size
        self.distance = distance
        self.exists = exists

    def __str__(self) -> str:
        return "x={}; y={}; size={}; distance={}; exists={}".format(self.x, self.y, self.size, self.distance, self.exists)

    def __repr__(self) -> str:
        return "x={}; y={}; size={}; distance={}; exists={}".format(self.x, self.y, self.size, self.distance, self.exists)

class ProcessedResults():

    def __init__(self, 
                balls=[], 
                basket_c=Object(exists = False), 
                basket_m=Object(exists = False), 
                color_frame = [],
                depth_frame = [],
                fragmented = [],
                debug_frame = []):
        self.balls = balls
        self.basket_c = basket_c
        self.basket_m = basket_m
        self.color_frame = color_frame
        self.depth_frame = depth_frame
        self.fragmented = fragmented
        self.debug_frame = debug_frame


class ImageProcessor():
    def __init__(self, color_config = "colors/colors.pkl", debug = False):
        self.camera = camera.RealsenseCamera()

        self.color_config = color_config
        with open(self.color_config, 'rb') as conf:
            self.colors_lookup = pickle.load(conf)
            segment.set_table(self.colors_lookup)

        self.fragmented	= np.zeros((self.camera.height, self.camera.width), dtype=np.uint8)

        self.t_balls = np.zeros((self.camera.height, self.camera.width), dtype=np.uint8)
        self.t_basket_c = np.zeros((self.camera.height, self.camera.width), dtype=np.uint8)
        self.t_basket_m = np.zeros((self.camera.height, self.camera.width), dtype=np.uint8)

        self.debug = debug
        self.debug_frame = np.zeros((self.camera.height, self.camera.width), dtype=np.uint8)


    def start(self):
        self.camera.open()

    def stop(self):
        cv2.destroyAllWindows()
        self.camera.close()

    def analyze_balls(self, t_balls) -> list:
        contours, hierarchy = cv2.findContours(t_balls, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        balls = []

        for contour in contours:
            size = cv2.contourArea(contour)

            if size < 25:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            ratio	= float(w) / h

            #if ratio < 0.5 or ratio > 2.0:
            #    continue

            ys	= np.repeat(np.arange(y + h, self.camera.height), 5)
            xs	= np.repeat(np.linspace(x + w/2, self.camera.width / 2, num=len(ys)/5), 5).astype('uint16')
            xs[::5] -= 2
            xs[1::5] -= 1
            xs[3::5] += 1
            xs[4::5] += 2
            
            line_pixels = self.fragmented[ys, xs]

            obj_x = int(x + (w/2))
            obj_y = int(y + (h/2))
            obj_dst = obj_y

            if self.debug:
                self.debug_frame[ys, xs] = [0, 0, 0]
                cv2.circle(self.debug_frame,(obj_x, obj_y), 5, (0,255,0), 1)

            balls.append(Object(x = obj_x, y = obj_y, size = size, distance = obj_dst, exists = True))

        balls.sort(key= lambda x: x.distance)

        return balls

    def process_frame(self) -> ProcessedResults:
        color_frame, depth_frame = self.camera.get_frames()      

        segment.segment(color_frame, self.fragmented, self.t_balls, self.t_basket_c, self.t_basket_m)

        if self.debug:
            self.debug_frame = color_frame

        balls = self.analyze_balls(self.t_balls)
        return ProcessedResults(balls = balls, color_frame=color_frame, depth_frame=depth_frame, fragmented=self.fragmented, debug_frame=self.debug_frame)
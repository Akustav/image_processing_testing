import image_processor
import camera
import motion
import cv2
import math
import time


def calc_speed(delta, max_delta, max_speed):
    delta_div = delta / max_delta
    sign = math.copysign(1, delta_div)
    normalized_delta = math.pow(abs(delta_div), 2) * sign
    return int(normalized_delta * max_speed)

def main_loop():
    debug = True
    #cam = camera.RealsenseCamera(exposure = 300)
    motion_sim = motion.TurtleRobot()
    motion_sim2 = motion.TurtleOmniRobot()

    cam = camera.OpenCVCamera(id = 2)
    processor = image_processor.ImageProcessor(cam, debug=debug)

    processor.start()
    motion_sim.open()
    motion_sim2.open()

    start = time.time()
    fps = 0
    frame = 0
    frame_cnt = 0
    try:
        while True:
            # has argument aligned_depth that enables depth frame to color frame alignment. Costs performance
            processedData = processor.process_frame(aligned_depth=False)

            # logic for driving goes here:
            if (len(processedData.balls)):
                largest_ball = processedData.balls[0]

                delta_x = largest_ball.x - cam.rgb_width / 2
                delta_y = cam.rgb_height / 2 - largest_ball.y

                speed_x = calc_speed(delta_x, cam.rgb_width / 2, 200)
                speed_y = calc_speed(delta_y, cam.rgb_height / 2, 200)
                rotation = calc_speed(delta_x, cam.rgb_width, 5)

                motion_sim.move(speed_x, speed_y, rotation)
                motion_sim2.move(speed_x, speed_y, rotation)
            else:
                motion_sim.move(0, 0, 0)
                motion_sim2.move(0, 0, 0)

            frame_cnt +=1

            frame += 1
            if frame % 30 == 0:
                frame = 0
                end = time.time()
                fps = 30 / (end - start)
                start = end
                print("FPS: {}, framecount: {}".format(fps, frame_cnt))
                print("ball_count: {}".format(len(processedData.balls)))
                #if (frame_cnt > 1000):
                #    break

            if debug:
                debug_frame = processedData.debug_frame

                cv2.imshow('debug', debug_frame)

                k = cv2.waitKey(1) & 0xff
                if k == ord('q'):
                    break
    except KeyboardInterrupt:
        print("closing....")
    finally:
        cv2.destroyAllWindows()
        processor.stop()
        motion_sim.close()
        motion_sim2.close()

main_loop()

import pyrealsense2 as rs
import numpy as np

class ICamera:
    def open(self):
        pass
    def close(self):
        pass

    def get_frames(self):
        pass



class RealsenseCamera(ICamera):
    def __init__(self, width = 848, height = 480, exposure = 300, white_balace = 3500):
        self.width = width
        self.height = height
        self.exposure = exposure
        self.white_balace = white_balace

        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 60)
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 60)
        self.align = rs.align(rs.stream.color)
        self.depth_scale = -1

    def open(self):
        profile = self.pipeline.start(self.config)
        color_sensor = profile.get_device().query_sensors()[1]
        color_sensor.set_option(rs.option.enable_auto_exposure, False)
        color_sensor.set_option(rs.option.enable_auto_white_balance, False)
        color_sensor.set_option(rs.option.white_balance, self.white_balace)
        color_sensor.set_option(rs.option.exposure, self.exposure)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        

    def close(self):
        self.pipeline.stop()

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        return np.asanyarray(aligned_frames.get_color_frame().get_data()), np.asanyarray(aligned_frames.get_depth_frame().get_data())

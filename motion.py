import turtle
import math
import numpy as np
import time

class IRobotMotion:
    def open(self):
        pass
    def close(self):
        pass
    def move(self, x_speed, y_speed, rot_speed):
        pass

class TurtleRobot(IRobotMotion):
    def __init__(self):
        turtle.speed(0)
        turtle.delay(0)

        self.steps = 20

    def open(self):
        print("Wroom! Starting up turtle!")

    def close(self):
        print("Going to sleep...")
        turtle.bye()

    #Very dumb logic to draw motion using turtle
    def move(self, x_speed, y_speed, rot_speed):
        turtle.tracer(0, 0)
        angle_deg = 0

        angle_deg = np.degrees(math.atan2(x_speed, y_speed))

        distance = math.sqrt(math.pow(x_speed, 2) + math.pow(y_speed, 2))

        distance_step = distance / float(self.steps)
        angel_step = np.degrees(rot_speed / float(self.steps))

        turtle.penup()
        turtle.reset()
        turtle.right(angle_deg - 90)
        turtle.pendown()

        for i in range(0, self.steps):
            turtle.right(angel_step)
            turtle.forward(distance_step)

        turtle.penup()
        turtle.update()



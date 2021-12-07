import cv2
import numpy as np
from constants import *


class Visualizer(object):
    def __init__(self, master):
        self.master = master

    def display(self, img):
        img = img.copy()
        for i in range(self.master.left_target.shape[0]):
            cv2.circle(img, (int(self.master.left_target[i, 0]), int(self.master.left_target[i, 1])), 20, (0, 204, 0), 3)
            cv2.circle(img, (int(self.master.left_target[i, 0]), int(self.master.left_target[i, 1])), 3, (0, 204, 0), -1)
        for i in range(self.master.right_target.shape[0]):
            cv2.circle(img, (int(self.master.right_target[i, 0]), int(self.master.right_target[i, 1])), 40, (255, 128, 0), 3)
            cv2.circle(img, (int(self.master.right_target[i, 0]), int(self.master.right_target[i, 1])), 3, (255, 128, 0), -1)
        if hasattr(self.master.tracker, "xy"):
            for i in range(self.master.tracker.xy.shape[0]):
                if self.master.tracker.r[i] < self.master.threshold:
                    cv2.circle(img, (int(self.master.tracker.xy[i, 0]), int(self.master.tracker.xy[i, 1])), int(self.master.tracker.r[i]), (14, 127, 255), 3)
                    cv2.circle(img, (int(self.master.tracker.xy[i, 0]), int(self.master.tracker.xy[i, 1])), 3, (14, 127, 255), -1)
                else:
                    cv2.circle(img, (int(self.master.tracker.xy[i, 0]), int(self.master.tracker.xy[i, 1])), int(self.master.tracker.r[i]), (40, 39, 214), 3)
                    cv2.circle(img, (int(self.master.tracker.xy[i, 0]), int(self.master.tracker.xy[i, 1])), 3, (40, 39, 214), -1)
            for i, j in enumerate(self.master.tracker.left_points):
                cv2.arrowedLine(img, (int(self.master.tracker.xy[j, 0]), int(self.master.tracker.xy[j, 1])), (int(self.master.left_target[i, 0]), int(self.master.left_target[i, 1])), (14, 127, 255), 3, cv2.LINE_4)
            for i, j in enumerate(self.master.tracker.right_points):
                cv2.arrowedLine(img, (int(self.master.tracker.xy[j, 0]), int(self.master.tracker.xy[j, 1])), (int(self.master.right_target[i, 0]), int(self.master.right_target[i, 1])), (40, 39, 214), 3, cv2.LINE_8)
        cv2.imshow("Auto clicker status", img)
        cv2.waitKey(1)
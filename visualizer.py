import cv2
import numpy as np
from constants import *


class Visualizer(object):
    def __init__(self, master):
        self.master = master

    def display(self, img):
        img = img.copy()
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        for i in range(self.master.left_target.shape[0]):
            cv2.circle(img, (int(self.master.left_target[i, 0]), int(self.master.left_target[i, 1])), 20, (0, 204, 0), 3)
            cv2.circle(img, (int(self.master.left_target[i, 0]), int(self.master.left_target[i, 1])), 3, (0, 204, 0), -1)
        for i in range(self.master.right_target.shape[0]):
            cv2.circle(img, (int(self.master.right_target[i, 0]), int(self.master.left_target[i, 1])), 40, (255, 128, 0), 3)
            cv2.circle(img, (int(self.master.right_target[i, 0]), int(self.master.left_target[i, 1])), 3, (255, 128, 0), -1)
        cv2.imshow("auto clicker status", img)
        cv2.waitKey(1)
import numpy as np
import win32api, win32con, win32gui
import time
from constants import *


class Tracker(object):
    def __init__(self, master, intersect=1.0, vanish=100):
        self.master = master
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.master.hwnd)
        self.intersect = intersect
        self.vanish = vanish
        self.obj_id = 0
        self.searching = True

    def update(self, new_objs):
        if new_objs is None:
            return
        if self.master.has_started:
            self.track(new_objs)
        else:
            self.gather(new_objs)

    def track(self, new_objs):
        pass

    def gather(self, new_objs):
        if hasattr(self, "xy"):
            self.freshness = self.freshness + 1
            dist = np.linalg.norm(self.xy.reshape((-1, 1, 2)) - new_objs[:, :2].reshape((1, -1, 2)), axis=2)
            added = []
            for i in range(new_objs.shape[0]):
                j = np.argmin(dist[:, i])
                if dist[j, i] < self.intersect * (self.r[j] + new_objs[i, 2]):
                    self.xy[j, :] = new_objs[i, :2]
                    self.r[j] = new_objs[i, 2]
                    self.freshness[j] = 0
                else:
                    added.append(i)
            added = new_objs[added, :]
            print(f"New Detection: {added.shape[0]} circles")

            self.xy = np.concatenate([self.xy, added[:, :2]], axis=0)
            self.r = np.concatenate([self.r, added[:, 2]], axis=0)
            self.freshness = np.concatenate([self.freshness, np.zeros_like(added[:, 2]).astype(np.uint8)], axis=0)
            # self.clicked = np.concatenate([self.clicked, np.zeros_like(added[:, 2]).astype(np.uint8)], axis=0)
            # self.click_all()

            mask = self.freshness < self.vanish
            self.xy = self.xy[mask]
            self.r = self.r[mask]
            self.freshness = self.freshness[mask]
            # self.clicked = self.clicked[mask]
        else:
            print(f"First Detection: {new_objs.shape[0]} circles")
            self.xy = new_objs[:, :2]
            self.r = new_objs[:, 2]
            self.freshness = np.zeros_like(new_objs[:, 2]).astype(np.uint8)
            # self.clicked = np.zeros_like(new_objs[:, 2]).astype(np.uint8)
            # self.click_all()

    def click_all(self):
        return
        if hasattr(self, "xy"):
            for i in range(self.xy.shape[0]):
                self.double_click(i)

    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def double_click(self, i):
        if self.clicked[i] == 1:
            return
        if self.pause.get() == 0:
            print(f"Double click on [{self.xy[i, 0], self.xy[i, 1]}]")
            x0, y0 = win32api.GetCursorPos()
            win32api.SetCursorPos([int(self.xy[i, 0] + self.left + crop_left), int(self.xy[i, 1] + self.top + crop_top)])
            self.click()
            self.click()
            self.clicked[i] = 1
            win32api.SetCursorPos([x0, y0])

    @property
    def can_start(self):
        if not hasattr(self, "xy"):
            return False
        h, w = self.matrix_shape
        return np.sum(self.r < self.threshold) >= h * w and np.sum(self.r > self.threshold) >= h * w

    @property
    def threshold(self):
        return self.master.threshold
    
    @property
    def matrix_shape(self):
        return self.master.matrix_shape
    

import numpy as np
import win32api, win32con, win32gui
import time
from constants import *


class Tracker(object):
    def __init__(self, master, intersect=1.0, vanish=30):
        self.master = master
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.master.hwnd)
        self.intersect = intersect
        self.vanish = vanish
        self.obj_id = 0
        self.target_large = np.array([(self.right - self.left) * 0.9, (self.bot - self.top) * 0.9])
        self.target_small = np.array([(self.right - self.left) * 0.9, (self.bot - self.top) * 0.1])

    def update(self, new_objs):
        if hasattr(self, "freshness"):
            self.freshness = self.freshness + 1

        if new_objs is not None:
            if hasattr(self, "xy"):
                if self.xy.shape[0] > 0:
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
                else:
                    added = np.arange(new_objs.shape[0])

                added = new_objs[added, :]

                self.xy = np.concatenate([self.xy, added[:, :2]], axis=0)
                self.r = np.concatenate([self.r, added[:, 2]], axis=0)
                self.freshness = np.concatenate([self.freshness, np.zeros_like(added[:, 2]).astype(np.uint8)], axis=0)

                print(f"New Detection: {added.shape[0]} circles")
            else:
                print(f"First Detection: {new_objs.shape[0]} circles")
                self.xy = new_objs[:, :2]
                self.r = new_objs[:, 2]
                self.freshness = np.zeros_like(new_objs[:, 2]).astype(np.uint8)

        if hasattr(self, "freshness"):
            self.freshness = self.freshness + 1
            mask = self.freshness < self.vanish
            self.xy = self.xy[mask]
            self.r = self.r[mask]
            self.freshness = self.freshness[mask]
            print(f"Now has {self.xy.shape[0]} tracked circles")

        if self.master.has_started and self.master.time % self.master.drag_interval == 0:
            self.drag()

    def drag(self, attract=10, repel=10, step=15):
        for i in range(self.xy.shape[0]):
            if self.xy[i][0] < (self.right - self.left) * 0.7 and 0.3 < self.xy[i][1] / (self.bot - self.top) < 0.7:
                # if self.r[i] < self.threshold:
                #     target = self.target_small
                # else:
                #     target = self.target_large
                # force = (target - self.xy[i]) * attract
                # for j in range(self.xy.shape[0]):
                #     if i != j:
                #         force += repel / (np.linalg.norm(self.xy[j] - self.xy[i]) ** 2) * (self.xy[i] - self.xy[j])
                # force = force / np.linalg.norm(force) * step
                # print(f"Dragging [{self.xy[i][0]:0.2f}, {self.xy[i][1]:0.2f}] with force [{force[0]:0.2f}, {force[1]:0.2f}]")
                print(f"Dragging [{self.xy[i][0]:0.2f}, {self.xy[i][1]:0.2f}]")
                self.drag_point(i, force)

    def drag_point(self, i, force=None):
        if not self.master.has_started:
            return
        x0, y0 = win32api.GetCursorPos()
        win32api.SetCursorPos([int(self.xy[i, 0] + self.left + crop_left), int(self.xy[i, 1] + self.top + crop_top)])
        self.click()
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_MOVE, int(force[0]), int(force[1]), 0, 0)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        win32api.SetCursorPos([x0, y0])
        self.master.root.focus_set()
        self.xy[i] += force

    # def start(self):
    #     if hasattr(self, "xy"):
    #         for i in self.left_points + self.right_points:
    #             self.double_click(i)

    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    # def double_click(self, i):
    #     # if self.clicked[i] == 1:
    #     #     return
    #     print(f"Double click on [{self.xy[i, 0], self.xy[i, 1]}]")
    #     x0, y0 = win32api.GetCursorPos()
    #     win32api.SetCursorPos([int(self.xy[i, 0] + self.left + crop_left), int(self.xy[i, 1] + self.top + crop_top)])
    #     self.click()
    #     self.click()
    #     # self.clicked[i] = 1
    #     win32api.SetCursorPos([x0, y0])
    #     self.master.root.focus_set()

    @property
    def threshold(self):
        return self.master.threshold
    

import os
import time
import imageio
from PIL import Image
import numpy as np
import argparse
import cv2
import win32api, win32con, win32gui, win32ui
from pywinauto import Desktop
from tkinter import Tk, IntVar, DoubleVar, Button, StringVar, Scale, HORIZONTAL
from tkinter.messagebox import showwarning

from capture import cap, detect
from tracker import Tracker
from visualizer import Visualizer
from constants import *


parser = argparse.ArgumentParser("Circle Clicker")
parser.add_argument("--window", type=str, default="hot.vi", help="window name")
args = parser.parse_args()


class Interface(object):
    def __init__(self, hwnd):
        self.hwnd = hwnd

        # create window
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.quitcallback)
        self.root.title("Auto Circle Clicker")
        self.root.geometry("200x410")
        self.root.iconbitmap("senpai.ico")

        # matrix selector
        self.matrix_h_selector = Scale(self.root, label="Target matrix height:", font=('Arial', 12), from_=1, to=9, resolution=1, digits=1, orient=HORIZONTAL, length=190, width=45)
        self.matrix_h_selector.set(3)
        self.matrix_h_selector.pack()

        self.matrix_w_selector = Scale(self.root, label="Target matrix width:", font=('Arial', 12), from_=1, to=9, resolution=1, digits=1, orient=HORIZONTAL, length=190, width=45)
        self.matrix_w_selector.set(3)
        self.matrix_w_selector.pack()

        # threshold selector
        self.threshold_selector = Scale(self.root, label="Split threshold:", font=('Arial', 12), from_=10, to=20, resolution=0.25, digits=4, orient=HORIZONTAL, length=190, width=45)
        self.threshold_selector.set(15.0)
        self.threshold_selector.pack()

        # button selector
        self.start_var = IntVar()
        self.start_var.set(0)
        self.main_switch_text = StringVar()
        self.main_switch_text.set("Start")
        self.main_switch = Button(self.root, height=90, width=190, font=('Arial', 40), textvariable=self.main_switch_text, command=self.start)
        self.main_switch.pack()

        # init tracker
        self.tracker = Tracker(self)

        # init visualizer
        self.visualizer = Visualizer(self)

        self.root.after(1, self.run)
        self.root.mainloop()

    def run(self):
        if not self.has_started:
            self.update_target()
        img = cap(self.hwnd)
        circles = detect(img)
        self.tracker.update(circles)
        self.visualizer.display(img)
        self.root.after(1, self.run)

    def start(self):
        if not self.has_started:
            if self.tracker.can_start:
                self.main_switch_text.set("Started")
                time.sleep(0.5)
                self.tracker.click_all()
                self.start_var.set(1)
            else:
                showwarning("Error", "Cannot find enough beads to form target matrix.")

    def update_target(self, ratio=0.4):
        assert 0 < ratio < 0.5
        h = crop_bottom - crop_top
        w = crop_right - crop_left
        mh, mw = self.matrix_shape
        x, y = np.meshgrid(np.arange(1, mw+1) * w * ratio / (mw+1), np.arange(1, mh+1) * h / (mh+1))
        x, y = x.reshape(-1, 1), y.reshape(-1, 1)
        self.left_target = np.concatenate([x, y], axis=1)
        self.right_target = np.concatenate([x + w * (1-ratio), y], axis=1)

    def quitcallback(self):
        self.root.destroy()

    @property
    def has_started(self):
        return self.start_var.get() != 0

    @property
    def threshold(self):
        return self.threshold_selector.get() * 359 / 180.0

    @property
    def matrix_shape(self):
        return int(self.matrix_h_selector.get()), int(self.matrix_w_selector.get())


if __name__ == "__main__":
    windows = Desktop(backend="uia").windows()
    window_names = [w.window_text() for w in windows]
    if args.window is None:
        print("\n".join(["Valid windows:"] + list(map(lambda x: f"    {x}", window_names))))
    else:
        window_name = [x for x in window_names if args.window in x.lower()][0]
        print(f"Window name: {window_name}")
        hwnd = win32gui.FindWindow(None, window_name)
        app = Interface(hwnd)

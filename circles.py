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
parser.add_argument("--window", type=str, default="tk", help="window name")
parser.add_argument("--interval", type=int, default=10, help="drag interval")
args = parser.parse_args()


class Interface(object):
    def __init__(self, hwnd, drag_interval):
        self.hwnd = hwnd
        self.time = 0
        self.drag_interval = drag_interval

        # create window
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.quitcallback)
        self.root.title("Auto Circle Clicker")
        self.root.geometry("200x180")
        self.root.iconbitmap("paimon.ico")
        self.root.bind('<Key-s>', self.start)

        # threshold selector
        self.threshold_selector = Scale(self.root, label="Split threshold:", font=('Arial', 12), from_=10, to=20, resolution=0.25, digits=4, orient=HORIZONTAL, length=190, width=45)
        self.threshold_selector.set(15.0)
        self.threshold_selector.pack()

        # button selector
        self.has_started = False
        # self.pause = True
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

    # def pause(self, event):
    #     self.pause = not self.pause
    #     print(self.pause)

    def run(self):
        self.time += 1
        img = cap(self.hwnd)
        circles = detect(img)
        self.tracker.update(circles)
        self.visualizer.display(img)
        self.root.after(1, self.run)

    def start(self):
        if not self.has_started:
            self.main_switch_text.set("Started")
            time.sleep(0.5)
            self.has_started = True
        else:
            self.main_switch_text.set("Start")
            time.sleep(0.5)
            self.has_started = False

    def quitcallback(self):
        self.root.destroy()

    @property
    def threshold(self):
        return self.threshold_selector.get() * 359 / 180.0


if __name__ == "__main__":
    windows = Desktop(backend="uia").windows()
    window_names = [w.window_text() for w in windows]
    if args.window is None:
        print("\n".join(["Valid windows:"] + list(map(lambda x: f"    {x}", window_names))))
    else:
        window_name = [x for x in window_names if args.window in x.lower()][0]
        print(f"Window name: {window_name}")
        hwnd = win32gui.FindWindow(None, window_name)
        app = Interface(hwnd, args.interval)

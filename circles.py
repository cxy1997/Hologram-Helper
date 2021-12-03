import os
import time
import imageio
from PIL import Image
import numpy as np
import argparse
import cv2
import win32api, win32con, win32gui, win32ui
from pywinauto import Desktop
from tkinter import Tk, IntVar, Button, StringVar

from capture import cap, detect
from tracker import Tracker


parser = argparse.ArgumentParser("Circle Clicker")
parser.add_argument("--window", type=str, default="hot.vi", help="window name")
args = parser.parse_args()


class Interface(object):
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.root = Tk()
        self.root.title("Auto Circle Clicker")
        self.root.geometry("200x100")
        self.root.iconbitmap("senpai.ico")
        self.pause = IntVar()
        self.pause.set(1)
        self.tracker = Tracker(hwnd, self.pause)
        self.text = StringVar()
        self.text.set("Off")
        self.button = Button(self.root, height=90, width=190, font=('Arial', 50), textvariable=self.text, command=self.switch)
        self.button.pack()
        self.root.protocol('WM_DELETE_WINDOW', self.quitcallback)
        self.root.after(1, self.run)
        self.root.mainloop()

    def run(self):
        img = cap(self.hwnd)
        circles = detect(img)
        self.tracker.update(circles)
        self.root.after(1, self.run)

    def switch(self):
        if self.pause.get() == 1:
            time.sleep(0.5)
        self.pause.set(1 - self.pause.get())
        if self.pause.get() == 0:
            self.text.set("On")
        else:
            self.text.set("Off")

    def quitcallback(self):
        self.pause.set(1)
        self.root.destroy()


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

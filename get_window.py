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


if __name__ == "__main__":
    target_window = "sublime"

    windows = Desktop(backend="uia").windows()
    window_names = [w.window_text() for w in windows]
    window_name = [x for x in window_names if target_window in x.lower()][0]
    hwnd = win32gui.FindWindow(None, window_name)

    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()

    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)

    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype=np.uint8)
    img.shape = (h, w, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    res = np.asarray(img)[:, :, :3]
    print(f"Capture successful, shape={res.shape}")
    cv2.imwrite("window_sample.png", res)
import numpy as np
import cv2
import win32api, win32con, win32gui, win32ui
import time
from constants import *


def cap(hwnd):
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
    cDC.BitBlt((0, 0), (w, h), dcObj, (left, top), win32con.SRCCOPY)
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype=np.uint8)
    img.shape = (h, w, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    res = np.asarray(img)[crop_top:crop_bottom, crop_left:crop_right, :3]
    print(f"Capture successful, shape={res.shape}")
    return res


def detect(img):
    img_small = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_small = cv2.resize(img_small, (720, 480))
    img_small = cv2.GaussianBlur(img_small, (5, 5), cv2.BORDER_DEFAULT)
    res = cv2.HoughCircles(img_small, cv2.HOUGH_GRADIENT, 1, 20,
        param1=30,
        param2=15,
        minRadius=10,
        maxRadius=20)
    if res is not None:
        res = res[0] * img.shape[1] / img_small.shape[1]
    return res
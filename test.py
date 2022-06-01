import win32api, win32con
import keyboard as kb
from time import sleep

while True:
    if kb.is_pressed('q'):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        sleep(0.2)
    if kb.is_pressed('esc'):
        break

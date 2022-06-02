import win32api
import win32con
from screeninfo import get_monitors
import cv2
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

increment = 6
left_clicked = False
right_clicked = False

prev_x, prev_y, curr_x, curr_y = 0, 0, 0, 0


def click(states):
    global left_clicked, right_clicked

    if not states[0] and states[1] and not left_clicked:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        left_clicked = True

    if states[0] and not states[1] and not right_clicked:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        right_clicked = True

    if states[0] or states[1]:
        left_clicked = False
        right_clicked = False


def fingers_up(positions):
    states = [False] * 4

    indices = ((6, 8), (10, 12), (14, 16), (18, 20))

    for i, f in enumerate(indices):
        if positions[f[0]].y > positions[f[1]].y:
            states[i] = True

    return states


def move_mouse(positions, i_w, i_h, states):
    if states[0] and states[1]:
        global increment, prev_x, prev_y, curr_x, curr_y
        monitor = get_monitors()[0]

        m_w = monitor.width
        m_h = monitor.height

        pos_index = positions[8].x * i_w, positions[8].y * i_h
        pos_middle = positions[12].x * i_w, positions[12].y * i_h

        pos = pos_middle
        if pos_index[1] < pos_middle[1]:
            pos = pos_index

        x = np.interp(pos[0], (100, i_w - 100), (0, m_w))
        y = np.interp(pos[1], (20, i_h - 180), (0, m_h))

        curr_x = prev_x + (x - prev_x) / increment
        curr_y = prev_y + (y - prev_y) / increment

        win32api.SetCursorPos((int(m_w - curr_x), int(curr_y)))
        prev_x, prev_y = curr_x, curr_y


while True:
    success, image = cap.read()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)
    h, w, temp = image.shape

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            up_fin = fingers_up(landmarks.landmark)
            click(up_fin)
            move_mouse(landmarks.landmark, w, h, up_fin)
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.rectangle(image, (100, 20), (w - 100, h - 180), (255, 0, 255), 3)
    cv2.imshow("Real Time", cv2.flip(image, 1))
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()

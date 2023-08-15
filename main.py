"""Virtual Mouse made with Mediapipe."""

import cv2
import mediapipe as mp
from screeninfo import get_monitors
from pynput.mouse import Button, Controller
import numpy as np

cap = cv2.VideoCapture(0)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

increment = 6

prev_x, prev_y, curr_x, curr_y = 0, 0, 0, 0
left_clicked, right_clicked = False, False

mouse = Controller()


def click(states):
    """Handle Button clicks."""
    global left_clicked, right_clicked

    if not states[0] and states[1] and not left_clicked:
        mouse.press(Button.left)
        mouse.release(Button.left)
        left_clicked = True

    if states[0] and not states[1] and not right_clicked:
        mouse.press(Button.right)
        mouse.release(Button.right)
        right_clicked = True

    if states[0] and states[1]:
        left_clicked = False
        right_clicked = False


def get_states(positions):
    """Return if fingers are up or down."""
    states = [False] * 2
    indices = ((6, 8), (10, 12))

    for i, f in enumerate(indices):
        if positions[f[0]].y > positions[f[1]].y:
            states[i] = True

    return states


def move_mouse(positions, image_w, image_h):
    """Move the cursor relative to the hand and smoothen the transition."""
    global prev_x, prev_y, curr_x, curr_y

    monitor = get_monitors()[0]

    m_w = monitor.width
    m_h = monitor.height

    x_pos = sum([positions[i].x for i in range(5, 18, 4)]) / 4
    y_pos = sum([positions[i].y for i in range(5, 18, 4)]) / 4

    pos = (x_pos * image_w, y_pos * image_h)

    x = np.interp(pos[0], (200, image_w - 200), (0, m_w))
    y = np.interp(pos[1], (200, image_h - 200), (0, m_h))

    curr_x = prev_x + (x - prev_x) / increment
    curr_y = prev_y + (y - prev_y) / increment

    mouse.position = (int(m_w - curr_x), int(curr_y))
    prev_x, prev_y = curr_x, curr_y


while True:
    success, image = cap.read()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)
    h, w, temp = image.shape

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            up_fingers = get_states(landmarks.landmark)
            click(up_fingers)
            move_mouse(landmarks.landmark, w, h)
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.rectangle(image, (200, 200), (w - 200, h - 200), (0, 255, 0), 3)
    cv2.imshow("Real Time", cv2.flip(image, 1))
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()

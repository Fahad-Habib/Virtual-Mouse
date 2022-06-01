import win32api
import win32con
from screeninfo import get_monitors
import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
# cap.set(3, get_monitors()[0].width)
# cap.set(4, get_monitors()[0].height)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

prev_x = None
prev_y = None
increment = 10
left_clicked = False
right_clicked = False
hold_click = False


def click(states):
    global left_clicked, right_clicked, hold_click

    # if states[0] and states[1] and states[2] and not hold_click:
    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    #     hold_click = True
    #     return
    # if not states[1] and not states[2]:
    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    #     hold_click = False
    #     return

    if states[0] and states[1] and not left_clicked:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        left_clicked = True
        return
    elif states[0] and not states[1]:
        left_clicked = False
        return

    if states[0] and states[3] and not right_clicked:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        right_clicked = True
        return
    elif states[0] and not states[3]:
        right_clicked = False
        return


def get_coordinates(positions, shape):
    h, w, c = shape
    return int(positions[8].x * w), int(positions[8].y * h)


def fingers_up(positions):
    states = [False] * 4

    indices = ((6, 8), (10, 12), (14, 16), (18, 20))

    for i, f in enumerate(indices):
        if positions[f[0]].y > positions[f[1]].y:
            states[i] = True

    return states


def move_mouse(pos, shape):
    global prev_x, prev_y, increment
    if prev_x is None and prev_y is None:
        prev_x, prev_y = pos
        return
    mouse_x, mouse_y = win32api.GetCursorPos()
    monitor = get_monitors()[0]
    m_w = monitor.width
    m_h = monitor.height
    i_h, i_w, temp = shape
    w = (m_w // i_w) * pos[0]
    h = (m_h // i_h) * pos[1]
    win32api.SetCursorPos((m_w - w, h * 2))


while True:
    success, image = cap.read()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            coords = get_coordinates(landmarks.landmark, image.shape)
            up_fin = fingers_up(landmarks.landmark, image.shape)
            move_mouse(coords, image.shape)
            click(up_fin)
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Real Time", cv2.flip(image, 1))
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()

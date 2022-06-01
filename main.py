import win32api
import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_drawing = mp.solutions.drawing_utils

mp_hands = mp.solutions.hands

# hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands()


def get_coordinates(positions, shape):
    h, w, c = shape
    for lm, pos in enumerate(positions):
        if lm == 8:
            return int(pos.x * w), int(pos.y * h)


def mouse(pos):
    win32api.SetCursorPos(pos)


while True:
    success, image = cap.read()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            coords = get_coordinates(landmarks.landmark, image.shape)
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)
            # cv2.putText(image, f'{c}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
            mouse(coords)

    cv2.imshow("Real Time", cv2.flip(image, 1))
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()

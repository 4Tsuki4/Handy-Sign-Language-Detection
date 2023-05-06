# DEPENDENCIES ------>
import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3


class TextToAudio:
    engine: pyttsx3.Engine

    def __init__(self, voice, rate: int, volume: float):
        self.engine = pyttsx3.init()
        if voice:
            self.engine.setProperty("voice", voice)
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

    def text_to_audio(self, text: str):
        self.engine.say(text)
        print(f"Signer: {predicted_sign}")
        self.engine.runAndWait()


model_dict = pickle.load(open("./model.p", "rb"))
model = model_dict["model"]
capture = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.9, min_tracking_confidence=0.9)
labels_dict = {0: "hello", 1: "i love you", 2: "yes", 3: "good", 4: "bad", 5: "okay", 6: "you", 7: "i/i'm", 8: "why", 9: "no"}

prev_time = time.time()

while True:
    data_aux = []
    x_ = []
    y_ = []
    ret, frame = capture.read()
    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x)
                data_aux.append(y)
                x_.append(x)
                y_.append(y)
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10
            prediction = model.predict([np.asarray(data_aux)])
            predicted_sign = labels_dict[int(prediction[0])]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
            cv2.putText(frame, predicted_sign, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
            data_aux = []
            x_ = []
            y_ = []

            if time.time() - prev_time >= 2:
                tta = TextToAudio("com.apple.speech.synthesis.voice.Alex", 200, 1.0)
                tta.text_to_audio(predicted_sign)
                prev_time = time.time()

    cv2.imshow("Handy", frame)
    cv2.waitKey(1)

capture.release()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import time

# ====================== INIT ======================
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Variables
counter = 0
set_count = 0
stage = None
REPS_PER_SET = 10
last_spoken = ""

def speak(text):
    global last_spoken
    if text != last_spoken:
        engine.say(text)
        engine.runAndWait()
        last_spoken = text

def calculate_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# ====================== CAPTURE ======================
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

print("Push-Up Coach PRO → Compte quand tu entends 'PUSH!'")
speak("En position planche. Prêt ?")

with pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        annotated = frame.copy()

        feedback = "En position planche"
        show_push_text = False  # Pour afficher "PUSH UP!" et compter

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=3),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=3)
            )

            lm = results.pose_landmarks.landmark

            # On prend le côté le plus visible (gauche ou droite)
            try:
                shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW].y]
                wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST].x, lm[mp_pose.PoseLandmark.LEFT_WRIST].y]
                hip = [lm[mp_pose.PoseLandmark.LEFT_HIP].y]
                nose_y = lm[mp_pose.PoseLandmark.NOSE].y
            except:
                try:
                    shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
                    elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
                    wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST].x, lm[mp_pose.PoseLandmark.RIGHT_WRIST].y]
                    hip = [lm[mp_pose.PoseLandmark.RIGHT_HIP].y]
                    nose_y = lm[mp_pose.PoseLandmark.NOSE].y
                except:
                    feedback = "Corps non détecté"
                    hip = [0.5]

            elbow_angle = calculate_angle(shoulder, elbow, wrist)

            # === NOUVELLE LOGIQUE : COMPTE QUAND "PUSH UP!" APPARAÎT ===
            if elbow_angle > 155:
                stage = "up"
                feedback = "Descends bien bas !"

            elif elbow_angle < 100 and stage == "up":
                stage = "down"
                show_push_text = True
                feedback = "POUSSE !"

                # ICI ON COMPTE AU MOMENT DU "PUSH UP!"
                if stage == "down":
                    counter += 1
                    speak(f"{counter} !")  # Son motivant au bon moment
                    # Option : son plus fort
                    # engine.say(f"{counter} ! Allez !")
                    # engine.runAndWait()

                    if counter % REPS_PER_SET == 0:
                        set_count += 1
                        speak(f"Série {set_count} terminée ! Bravo !")
                        time.sleep(2)

        else:
            feedback = "Mets tout ton corps dans le cadre !"

        # === AFFICHAGE ===
        cv2.rectangle(annotated, (0,0), (1280,160), (0,0,0), -1)

        cv2.putText(annotated, f'REPS: {counter}', (40, 80),
                    cv2.FONT_HERSHEY_DUPLEX, 2.8, (255,255,255), 5)
        cv2.putText(annotated, f'SÉRIES: {set_count}', (40, 140),
                    cv2.FONT_HERSHEY_DUPLEX, 2.5, (0,255,255), 5)

        cv2.putText(annotated, feedback, (300, 100),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (0,255,255), 4)

        # LE MESSAGE "PUSH UP!" QUI FAIT COMPTER
        if show_push_text:
            cv2.putText(annotated, "PUSH UP!", (380, 420),
                        cv2.FONT_HERSHEY_DUPLEX, 5.5, (0,255,0), 12)
            cv2.putText(annotated, f"{counter}", (600, 300),
                        cv2.FONT_HERSHEY_DUPLEX, 6, (255,215,0), 14)

        cv2.imshow("Push-Up Coach - Compte quand tu entends PUSH!", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

# Fin de séance
print(f"\nFINI ! Tu as fait {counter} pompes en {set_count} séries !")
speak(f"Incroyable ! Tu as fait {counter} pompes ! T'es un monstre !")
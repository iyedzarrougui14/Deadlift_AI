import cv2
import mediapipe as mp
import time
import pandas as pd

# Initialisation MediaPipe
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Scènes et sports associés
scenes = {
    "Plage": "Yoga",
    "Forêt": "Trail",
    "Stade": "Football",
    "Salle de sport": "Musculation"
}
scene_names = list(scenes.keys())
scene_index = 0
user_results = []

# Détection du sourire (mesure distance entre points de la bouche)
def is_smiling(landmarks, img_w):
    left = landmarks[61]
    right = landmarks[291]
    mouth_width = abs(right.x - left.x) * img_w
    return mouth_width > 50  # Seuil à ajuster si besoin

# Webcam ON
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Impossible d'ouvrir la webcam")
    exit()

timer_start = time.time()

while cap.isOpened() and scene_index < len(scene_names):
    success, frame = cap.read()
    if not success:
        print("❌ Problème avec la webcam.")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    img_h, img_w, _ = frame.shape

    # Affiche la scène actuelle
    current_scene = scene_names[scene_index]
    cv2.putText(frame, f"Regarde cette scène : {current_scene}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(frame, face_landmarks, mp_face.FACEMESH_TESSELATION)

            if is_smiling(face_landmarks.landmark, img_w):
                reaction_time = round(time.time() - timer_start, 2)
                user_results.append({
                    "scene": current_scene,
                    "smile": 1,
                    "reaction_time": reaction_time
                })
                print(f"😊 Sourire détecté pour {current_scene} (temps : {reaction_time}s)")
                scene_index += 1
                timer_start = time.time()
                break

    cv2.imshow("😊 Souris à la scène que tu préfères", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        print("🔚 Fermeture par l'utilisateur.")
        break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()

# Sauvegarde
if user_results:
    df = pd.DataFrame(user_results)
    df.to_csv("smile_scene_dataset.csv", index=False)
    print("✅ Données enregistrées dans smile_scene_dataset.csv")

    # Recommandation du sport
    favorite_scene = df.loc[df['reaction_time'].idxmin()]['scene']
    recommended_sport = scenes[favorite_scene]
    print(f"\n🎯 Ton sport idéal est : **{recommended_sport}** (tu as souri le plus vite à la scène {favorite_scene})")
else:
    print("😕 Aucun sourire détecté. Relance l'app et essaie de sourire devant une scène.")

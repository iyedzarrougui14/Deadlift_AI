"""
Flask API for Deadlift AI - Pose Detection Backend
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import pickle
import numpy as np
import pandas as pd
import mediapipe as mp
import base64
from io import BytesIO
from PIL import Image
from landmarks import landmarks

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

# Load the trained model
try:
    with open('deadlift.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Warning: deadlift.pkl model file not found")
    model = None

# Global state for counter and stage tracking
session_state = {
    'counter': 0,
    'current_stage': '',
    'bodylang_class': '',
    'bodylang_prob': [0, 0]
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Deadlift AI API is running'
    }), 200


@app.route('/detect', methods=['POST'])
def detect():
    """
    Detect deadlift pose from an image
    Expected JSON: {
        'image': base64_encoded_image_string
    }
    Returns: {
        'stage': current body stage (up/down),
        'class': predicted class,
        'probability': confidence score,
        'counter': rep count,
        'annotated_image': base64_encoded_result_image
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(BytesIO(image_data))
        image_np = np.array(image)
        
        # Convert RGB to BGR for OpenCV compatibility
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            frame = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            frame = image_np
        
        # read options from request
        return_image = data.get('return_image', True)
        max_width = int(data.get('max_width', 640))
        jpeg_quality = int(data.get('jpeg_quality', 70))

        # downscale while preserving aspect ratio
        h, w = frame.shape[:2]
        if w > max_width:
            scale = max_width / w
            frame = cv2.resize(frame, (int(w*scale), int(h*scale)))

        # process pose
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # produce landmarks list
        landmarks_list = []
        if results.pose_landmarks:
            for i, lm in enumerate(results.pose_landmarks.landmark):
                landmarks_list.append({
                    'index': i,
                    'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility
                })

        # only draw/encode annotated image if requested
        annotated_base64 = None
        if return_image:
            annotated_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
            )
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            _, buffer = cv2.imencode('.jpg', annotated_image, encode_param)
            annotated_base64 = base64.b64encode(buffer).decode()

        # respond with landmarks and optionally image
        return jsonify({
            'stage': session_state['current_stage'],
            'class': session_state['bodylang_class'],
            'probability': max(session_state['bodylang_prob']) if session_state['bodylang_prob'] else 0,
            'counter': session_state['counter'],
            'annotated_image': annotated_base64,
            'landmarks_detected': results.pose_landmarks is not None,
            'landmarks': landmarks_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset', methods=['POST'])
def reset():
    """Reset the rep counter and stage"""
    session_state['counter'] = 0
    session_state['current_stage'] = ''
    session_state['bodylang_class'] = ''
    session_state['bodylang_prob'] = [0, 0]
    
    return jsonify({
        'message': 'Counter reset',
        'counter': session_state['counter']
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """Get current session status"""
    return jsonify({
        'counter': session_state['counter'],
        'current_stage': session_state['current_stage'],
        'class': session_state['bodylang_class'],
        'probability': max(session_state['bodylang_prob']) if session_state['bodylang_prob'] else 0
    }), 200


@app.route('/stream', methods=['POST'])
def stream_detect():
    """
    Process video stream from webcam (for continuous detection)
    Expected JSON: {
        'frame': base64_encoded_frame
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame provided'}), 400
        
        # Decode base64 frame
        frame_data = base64.b64decode(data['frame'])
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid frame data'}), 400
        
        # Process pose
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        mp_drawing.draw_landmarks(
            image_rgb, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
        )
        
        # Extract landmarks and predict
        if model and results.pose_landmarks:
            try:
                row = np.array([
                    [res.x, res.y, res.z, res.visibility] 
                    for res in results.pose_landmarks.landmark
                ]).flatten().tolist()
                
                X = pd.DataFrame([row], columns=landmarks)
                bodylang_prob = model.predict_proba(X)[0]
                bodylang_class = model.predict(X)[0]
                
                # Update stage tracking
                if bodylang_class == "down" and bodylang_prob[bodylang_prob.argmax()] > 0.7:
                    session_state['current_stage'] = "down"
                elif session_state['current_stage'] == "down" and bodylang_class == "up" and bodylang_prob[bodylang_prob.argmax()] > 0.7:
                    session_state['current_stage'] = "up"
                    session_state['counter'] += 1
                
                session_state['bodylang_class'] = bodylang_class
                session_state['bodylang_prob'] = bodylang_prob.tolist()
                
            except Exception as e:
                print(f"Error during prediction: {e}")
        
        # Encode result frame to base64
        _, buffer = cv2.imencode('.jpg', image_rgb)
        result_base64 = base64.b64encode(buffer).decode()
        
        return jsonify({
            'frame': result_base64,
            'stage': session_state['current_stage'],
            'class': session_state['bodylang_class'],
            'probability': max(session_state['bodylang_prob']) if session_state['bodylang_prob'] else 0,
            'counter': session_state['counter']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    # Serve existing index.html if present, otherwise return a simple JSON message
    try:
        return send_from_directory('.', 'index.html')
    except Exception:
        return jsonify({'status': 'healthy', 'message': 'Deadlift AI API. See /health'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

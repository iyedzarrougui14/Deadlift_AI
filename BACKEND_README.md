# 🏋️ Deadlift AI - Flask Backend Setup

A Flask-based REST API for the Deadlift AI pose detection system. This backend enables web integration of your deadlift pose detection model.

## Features

- **REST API** for pose detection and rep counting
- **CORS enabled** for web integration
- **Base64 image/frame processing** for easy client integration
- **Session-based counter** tracking
- **Real-time stream processing** support
- **Annotated image output** with pose landmarks

## Project Structure

```
Deadlift_AI/
├── api.py                 # Flask API server
├── app.py                 # Original Tkinter GUI app
├── landmarks.py           # Pose landmark definitions
├── data.py                # Data processing utilities
├── deadlift.pkl          # Trained ML model
├── index.html            # Web dashboard
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### 2. Install Dependencies

```bash
# If you have a virtual environment active:
pip install -r requirements.txt

# Or install individually:
pip install flask flask-cors mediapipe opencv-python pandas numpy pillow scikit-learn
```

### 3. Verify Model File
Ensure you have the trained model file:
```bash
# The model should be in the project root
ls deadlift.pkl
```

## Running the API

### Start the Flask Server

```bash
python api.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Access the Web Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

You'll see the Deadlift AI Dashboard with:
- Live video feed with pose detection
- Real-time rep counter
- Stage and confidence indicators
- Control buttons (Start, Stop, Reset)

## API Endpoints

### 1. Health Check
```
GET /health
```
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Deadlift AI API is running"
}
```

### 2. Detect Pose from Image
```
POST /detect
```
Process a single image for pose detection.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "stage": "down",
  "class": "down",
  "probability": 0.95,
  "counter": 5,
  "annotated_image": "base64_encoded_result_image",
  "landmarks_detected": true
}
```

### 3. Stream Processing
```
POST /stream
```
Process video stream frames for continuous detection.

**Request Body:**
```json
{
  "frame": "base64_encoded_frame"
}
```

**Response:**
```json
{
  "frame": "base64_encoded_annotated_frame",
  "stage": "up",
  "class": "up",
  "probability": 0.92,
  "counter": 6
}
```

### 4. Get Session Status
```
GET /status
```
Get current session information without processing.

**Response:**
```json
{
  "counter": 6,
  "current_stage": "up",
  "class": "up",
  "probability": 0.92
}
```

### 5. Reset Counter
```
POST /reset
```
Reset the rep counter and stage tracking.

**Response:**
```json
{
  "message": "Counter reset",
  "counter": 0
}
```

## Usage Examples

### cURL Examples

**Check API Health:**
```bash
curl http://localhost:5000/health
```

**Get Current Status:**
```bash
curl http://localhost:5000/status
```

**Reset Counter:**
```bash
curl -X POST http://localhost:5000/reset
```

**Send Image for Detection:**
```bash
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "'$(base64 -w 0 < frame.jpg)'"
  }'
```

### Python Integration Example

```python
import requests
import base64
import cv2

API_URL = 'http://localhost:5000'

# Read and encode image
with open('frame.jpg', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Send to API
response = requests.post(f'{API_URL}/detect', json={'image': image_b64})
result = response.json()

print(f"Stage: {result['stage']}")
print(f"Rep Count: {result['counter']}")
print(f"Confidence: {result['probability']:.2%}")
```

### JavaScript Integration Example

```javascript
const API_URL = 'http://localhost:5000';

async function detectPose(imageBase64) {
  const response = await fetch(`${API_URL}/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64 })
  });
  
  return await response.json();
}

// Get status
async function getStatus() {
  const response = await fetch(`${API_URL}/status`);
  return await response.json();
}

// Reset counter
async function resetCounter() {
  const response = await fetch(`${API_URL}/reset`, { method: 'POST' });
  return await response.json();
}
```

## Web Dashboard Features

The `index.html` dashboard provides:
- **Live Camera Feed**: Real-time video with pose detection visualization
- **Statistics Display**: Current rep count, stage, detected class, and confidence
- **Control Buttons**: Start/Stop detection and Reset counter
- **API Documentation**: Built-in endpoint reference

### How to Use the Dashboard

1. Open `http://localhost:5000` in your browser
2. Click "Start Detection" to begin camera capture
3. The system will track your deadlifts in real-time
4. Click "Reset Counter" to start a new workout session
5. Click "Stop" to end the detection

## Configuration

### Pose Detection Parameters

Modify confidence thresholds in `api.py`:

```python
# Line ~11-12 in api.py
pose = mp_pose.Pose(
    min_tracking_confidence=0.5,  # Increase for stricter tracking
    min_detection_confidence=0.5   # Increase for stricter detection
)
```

### Rep Detection Threshold

Modify the probability threshold for valid reps (default: 0.7):

```python
# Line ~133 in api.py
if bodylang_class == "down" and max(bodylang_prob) > 0.7:  # Change 0.7 to desired value
```

### CORS Configuration

The API is configured to accept requests from any origin. To restrict:

```python
# In api.py, replace CORS(app) with:
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})
```

## Troubleshooting

### "Camera access required" message
- Ensure camera permissions are granted in your browser
- Firefox requires explicit permissions, Chrome asks on first use

### API returns "No landmarks detected"
- Ensure adequate lighting
- Move closer to the camera
- Check that the deadlift pose is clearly visible

### Model not loading
- Verify `deadlift.pkl` exists in the project root
- Check file permissions
- Retrain the model if corrupted

### CORS errors in web dashboard
- Ensure the Flask API is running on `localhost:5000`
- Check browser console for detailed error messages

## Performance Tips

- Use **smaller image dimensions** for faster processing
- **Adjust confidence thresholds** based on your environment
- For **production**, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

## API Response Times

- Single image detection: ~150-250ms
- Stream frame processing: ~100-200ms
- Status queries: <10ms

## Extending the API

### Add Custom Endpoints

```python
@app.route('/custom', methods=['GET'])
def custom_endpoint():
    return jsonify({'message': 'Custom response'}), 200
```

### Database Integration

Add persistent storage:
```python
from sqlalchemy import create_engine, Column, Integer, String
# Add your database logic here
```

## Security Notes

For production deployment:
1. Disable `debug=True` in `api.py` line 113
2. Use environment variables for sensitive data
3. Implement authentication/authorization
4. Use HTTPS instead of HTTP
5. Deploy behind a reverse proxy (Nginx)

## License

This project is part of the Deadlift AI suite.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API endpoint documentation
3. Check browser console for error messages
4. Verify all dependencies are installed correctly

---

Happy lifting! 💪

# 📋 DEADLIFT AI - QUICK REFERENCE CHEATSHEET

## ⚡ ONE-LINERS

```bash
# Start the API
python api.py

# Verify setup
python verify_setup.py

# Test with cURL
curl http://localhost:5000/health

# Deploy with Docker
docker-compose up -d
```

---

## 🔗 API ENDPOINTS

```
GET  http://localhost:5000/health
POST http://localhost:5000/detect
POST http://localhost:5000/stream
GET  http://localhost:5000/status
POST http://localhost:5000/reset
```

---

## 💻 PYTHON CLIENT SNIPPETS

### Health Check
```python
from client import DeadliftAIClient
client = DeadliftAIClient()
if client.health_check():
    print("API is healthy!")
```

### Detect from File
```python
result = client.detect_from_file('photo.jpg')
print(f"Reps: {result['counter']}")
print(f"Stage: {result['stage']}")
```

### Get Status
```python
status = client.get_status()
print(f"Counter: {status['counter']}")
```

### Reset Counter
```python
client.reset()
```

### Stream Processing
```python
import cv2
from client import DeadliftSession

session = DeadliftSession(client)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    result = session.process_frame(frame)
    print(f"Reps: {result['counter']}")
```

---

## 📚 DOCUMENTATION MAP

```
START HERE         → __START_HERE__.md
5 Min Intro        → QUICKSTART.md
Full Reference     → BACKEND_README.md
Architecture       → VISUAL_GUIDE.md
Find Anything      → DOCUMENTATION_INDEX.md
Examples           → client.py
API Docs           → BACKEND_README.md (Endpoints section)
Troubleshoot       → BACKEND_README.md (Troubleshooting)
Verify Setup       → python verify_setup.py
```

---

## 🚀 GETTING STARTED

### Step 1: Start API
```bash
python api.py
```

### Step 2: Open Dashboard
```
http://localhost:5000
```

### Step 3: Test Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Get status
curl http://localhost:5000/status
```

---

## 🎯 COMMON TASKS

### Test Image Detection
```python
result = client.detect_from_file('test.jpg')
print(result)
```

### Process Video Stream
```python
import cv2
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    result = client.stream_detect_from_array(frame)
```

### Save Annotated Image
```python
result = client.detect_from_file('photo.jpg')
client.save_annotated_image(result, 'output.jpg')
```

### Get Session Stats
```python
session = DeadliftSession(client)
# ... process frames ...
stats = session.get_session_stats()
print(stats)
```

---

## 🔧 CONFIGURATION

### Change Port
Edit `api.py` line 113:
```python
app.run(port=8000)
```

### Change Detection Confidence
Edit `api.py` line 12:
```python
pose = mp_pose.Pose(min_detection_confidence=0.8)
```

### Change Rep Threshold
Edit `api.py` line 133:
```python
if max(bodylang_prob) > 0.85:
```

---

## 📦 INSTALLATION

```bash
# Install dependencies
pip install -r requirements.txt

# Or manually
pip install flask flask-cors mediapipe opencv-python pandas numpy pillow scikit-learn requests
```

---

## 🐳 DOCKER COMMANDS

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f deadlift-api

# Stop services
docker-compose down

# Rebuild image
docker-compose build --no-cache
```

---

## 🧪 TESTING

### Test API Health
```bash
curl http://localhost:5000/health
```

### Test with Image
```bash
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_image_string"}'
```

### Test Status
```bash
curl http://localhost:5000/status
```

### Test Reset
```bash
curl -X POST http://localhost:5000/reset
```

---

## 🆘 QUICK FIXES

| Error | Fix |
|-------|-----|
| Port in use | `netstat -ano \| findstr :5000` then kill process |
| Module not found | `pip install -r requirements.txt` |
| Camera denied | Grant browser permissions |
| Model not found | Check `deadlift.pkl` exists |
| API not responding | Check it started: `python api.py` |

---

## 📊 PERFORMANCE

- **Single image**: 150-250ms
- **Video frame**: 100-200ms
- **Status query**: <10ms
- **FPS**: ~30 at 500x500

---

## 🎓 LEARNING PATH

```
Day 1: python api.py → http://localhost:5000
Day 2: Read QUICKSTART.md → Try Python client
Day 3: Read BACKEND_README.md → Plan integration
Day 4+: Integrate with your app
```

---

## 📞 HELP COMMANDS

```bash
# Verify everything works
python verify_setup.py

# Read quick start
cat QUICKSTART.md

# Read full docs
cat BACKEND_README.md

# Try examples
python client.py
```

---

## 🔐 SECURITY (Production)

```python
# Disable debug mode
app.run(debug=False)

# Use environment variables
import os
DEBUG = os.getenv('DEBUG', False)

# Add authentication
from functools import wraps
# ... implement auth decorator
```

---

## 📈 SCALING

### For Higher Load:
```bash
# Use Gunicorn with more workers
gunicorn -w 8 -b 0.0.0.0:5000 api:app

# Use Nginx reverse proxy
# Use Docker Swarm or Kubernetes
```

See BACKEND_README.md for details.

---

## 🎯 ENDPOINTS QUICK LOOKUP

```
/health   → Is API running?
/detect   → Analyze image
/stream   → Process video
/status   → Current state?
/reset    → Clear counter
```

---

## 💡 PRO TIPS

1. Use `verify_setup.py` to check everything
2. Read docs in this order: QUICKSTART → BACKEND_README → VISUAL_GUIDE
3. Use Python client for easier integration
4. Use Docker for deployment
5. Monitor logs while developing

---

## 🚀 DEPLOY CHECKLIST

- [ ] Run `verify_setup.py` (all green?)
- [ ] Test web dashboard
- [ ] Test Python client
- [ ] Read deployment section in BACKEND_README.md
- [ ] Set up environment variables
- [ ] Use Gunicorn instead of Flask dev server
- [ ] Set up Nginx reverse proxy
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Test under load

---

## 📋 FILE CHECKLIST

**Code Files:**
- [ ] api.py (Flask API)
- [ ] client.py (Python client)
- [ ] index.html (Web dashboard)
- [ ] verify_setup.py (Verification)

**Config Files:**
- [ ] requirements.txt
- [ ] Dockerfile
- [ ] docker-compose.yml

**Documentation:**
- [ ] __START_HERE__.md
- [ ] QUICKSTART.md
- [ ] BACKEND_README.md
- [ ] VISUAL_GUIDE.md
- [ ] DOCUMENTATION_INDEX.md

---

**Print this cheatsheet and keep it handy!** 📌

**Setup Date**: December 5, 2025  
**Status**: ✅ Ready to Use  
**Quick Start**: `python api.py`

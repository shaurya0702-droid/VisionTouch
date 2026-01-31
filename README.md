# 🧠 VisionTouch OS — Gesture-Controlled Human–Computer Interface

VisionTouch OS is a **real-time computer vision system** that converts **hand gestures into system-level controls** using a webcam.

It allows users to control a computer **without touching a mouse or keyboard**, demonstrating **Computer Vision**, **Human–Computer Interaction (HCI)**, and **OS-level automation**.

---

## 🎯 What This Project Does

Using live webcam input, VisionTouch OS enables:

- 🖱️ Mouse movement  
- 👆 Left click  
- 👉 Right click  
- 🖐️ Scroll  
- 🔊 System volume control (Windows)

All interactions happen **in real time**, using only **hand gestures**.

---

## 🎥 Demo Video

The demo video is included directly in the repository

---

## 🧠 High-Level Architecture

```
Webcam
  ↓
OpenCV (Frame Capture)
  ↓
MediaPipe Hands (Landmarks + Handedness)
  ↓
Custom Logic Layer
  ├─ Physical Right Hand → Mouse Control
  └─ Physical Left Hand  → Volume Control
  ↓
OS Interaction Layer
  ├─ autopy     (Mouse movement & clicks)
  ├─ pyautogui  (Scrolling)
  └─ pycaw      (System volume)
```

**Hand separation** is the key design choice that keeps the system stable and usable.

---

## 📦 Libraries Used & Why

### 🔍 Core Computer Vision
- **OpenCV (`cv2`)** — webcam input, frame processing, UI overlays
- **MediaPipe Hands** — 21 landmarks, handedness detection

### 🧮 Math & Utilities
- **NumPy** — interpolation, smoothing
- **math.hypot** — distance calculation
- **time** — FPS calculation

### 🖥️ OS-Level Control
- **autopy** — mouse movement & clicks
- **pyautogui** — scrolling
- **pycaw** — system volume control (Windows)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/shaurya0702-droid/VisionTouch.git
cd VisionTouch
```

---

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

`requirements.txt`

```bash
pip install -r requirements.txt
```

---

## ▶️ Run VisionTouch OS

Run the main file from terminal:

```bash
python visiontouch.py
```

Press **`q`** to safely exit.

---

## 📷 Camera & Screen Configuration

```python
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

wScr, hScr = autopy.screen.size()
```

Fixed resolution ensures:
- Predictable hand mapping
- Reduced jitter
- Stable gestures

---

## 🛡️ Gesture Safety & Stability Controls

```python
frameR = 100
PINCH_DISTANCE = 20
RELEASE_DISTANCE = 35
smoothening = 6
```

Why this matters:
- Prevents accidental clicks
- Smooth cursor motion
- Production-level UX safety

---

## 🧩 Hand Detection Engine

### `handDetector` Class

```python
self.handType = handInfo.classification[0].label
```

⚠ MediaPipe feed is **not mirrored**:
- `"Right"` → Physical left hand  
- `"Left"` → Physical right hand  

Handled correctly in logic.

---

## 🔊 Volume Control (Physical LEFT Hand)

```python
pinchDist = hypot(middle - thumb)

if pinchDist < 25:
    volumeActive = True
elif pinchDist > 40:
    volumeActive = False
```

Gesture gating prevents accidental volume change.

```python
length = hypot(index - thumb)
volPer = interp(length, [10, 150], [0, 1])
volume.SetMasterVolumeLevelScalar(volPer, None)
```

Controls **real system volume**.

---

## 🖱️ Mouse Control (Physical RIGHT Hand)

```python
x3 = interp(x1, camera_range, screen_range)
clocX = plocX + (x3 - plocX) / smoothening
```

Low-pass filtering ensures smooth movement.

---

## 👆 Click Gestures

- **Left Click** → Index + Thumb pinch  
- **Right Click** → Middle + Thumb pinch  
- Both are **debounced** to prevent spam clicks

---

## 🖐️ Scroll Mode (Open Palm)

```python
tip_y < knuckle_y
scrollDelta = prevScrollY - index_tip
pyautogui.scroll(-scrollDelta)
```

Continuous gesture-based scrolling.

---

## 🔁 Mode Priority

1. Volume  
2. Scroll  
3. Click  
4. Cursor movement  

Prevents gesture collision.

---

## 📊 Performance Monitoring

```python
fps = 1 / (cTime - pTimeFPS)
```

Ensures real-time inference.

---

## ❌ Exit Handling

```python
if cv2.waitKey(1) & 0xFF == ord('q'):
```

Clean shutdown:
- Camera released
- Windows destroyed
- No memory leak

---

## 🧪 Key Concepts Demonstrated

- Computer Vision  
- Real-time systems  
- Gesture recognition  
- Human–Computer Interaction  
- OS-level automation  
- UX safety mechanisms  

---

## ⭐ Demonstrates: 

- ✅ Advanced CV
- ✅ Real-time interaction
- ✅ OS-level control
- ✅ Clean modular design



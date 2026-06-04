# Enterprise Biometric Kiosk: Native GUI & DeepFace

A real-time, thread-safe biometric attendance solution integrating enterprise-level facial recognition and liveness detection into a standalone native Windows application.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FaceNet](https://img.shields.io/badge/DeepFace-FaceNet-red) ![Tkinter](https://img.shields.io/badge/Tkinter-Native_GUI-green) ![Status](https://img.shields.io/badge/Status-Active-success)

--- 

## Introduction
This project automates the traditional attendance process using state-of-the-art Facial Recognition. Evolving from a web-based Flask backend, this system is now a natively threaded desktop application designed to bypass strict corporate firewalls. It leverages Google's FaceNet architecture via DeepFace for highly accurate recognition and features built-in liveness detection (anti-spoofing) to reject fraudulent check-ins. Attendance is logged instantly to an offline SQLite database and securely exported as Excel (.xlsx) reports.

## Repository Structure
```text
automated-face-attendance/
├── known_faces/              # Database of authorized users (add JPGs here)
├── static/                   # UI assets (e.g., logo.png for watermarking)
├── kiosk_gui.py              # Main application launcher & UI thread
├── attendance_engine.py      # AI core: Detection, Recognition & Anti-Spoofing
├── db_manager.py             # SQLite database handler
├── deploy.prototxt.txt       # Caffe model architecture
├── res10_300x300...model     # Pre-trained face detection weights
├── requirements.txt          # List of dependencies
└── README.md                 # Documentation
```
## Key Features

* **Multi-Threaded Native GUI:** A fully interactive Tkinter desktop interface that separates UI rendering from heavy AI processing, ensuring a buttery-smooth 30 FPS camera feed without freezing.
* **Liveness Detection (Anti-Spoofing):** Utilizes DeepFace's Fasnet model to analyze frame depth, pixel grids, and screen glare, actively rejecting 2D printed photos and digital screens.
* **Hybrid Vision Pipeline:** Employs a lightweight ResNet-10 SSD to rapidly detect faces, passing only validated crops to the heavier FaceNet embedding model to save CPU cycles.
* **Secure Offline Export:** Replaces flat files with an encrypted SQLite database, featuring an admin-only portal to instantly compile and export daily `.xlsx` reports.

## Tech Stack & Methodology

| Component | Technology | Description |
| :--- | :--- | :--- |
| **GUI & State** | Python Tkinter | Single-window state machine bypassing browser restrictions. |
| **Detection** | OpenCV DNN (Caffe) | Single Shot Detector (SSD) framework with ResNet-10 backbone. |
| **Recognition** | DeepFace (FaceNet) | Extracts secure 128D facial embeddings using TensorFlow. |
| **Security** | Fasnet Liveness | Real-time pixel depth and glare analysis to prevent spoofing. |
| **Database** | SQLite3 & OpenPyXL | Local relational logging with automated Excel report generation. |

## Results & Analysis

### 1. Detection Model (SSD)
We utilize a Single Shot Detector (SSD) with a ResNet-10 backbone. This DNN approach is highly robust against:
* Partial occlusions and masks.
* Varying office lighting conditions.
* Side-profile faces.

### 2. Recognition & Security Logic
The system computes a spatial distance between the live 128D FaceNet embedding and the database using Cosine Distance:

$$\text{Distance}(A, B) = 1 - \frac{A \cdot B}{\|A\| \|B\|}$$

* **Security Threshold:** A strict distance cutoff of `0.40` is applied. 
* **Spoof Rejection:** Before embeddings are compared, the full frame undergoes a liveness check. If `is_real == False`, the system immediately flags the attempt as a "SPOOF DETECTED" and halts the database entry.
* **Performance:** Threading ensures the UI never hangs, safely polling the AI background worker 30 times a second for successful matches.

## Installation & Usage

### Step 1: Clone
```bash
git clone [https://github.com/stark-069/automated-face-attendance.git](https://github.com/stark-069/automated-face-attendance.git)
cd automated-face-attendance
```
### Step 2: Install Requirements
*(Ensure you are using a stable release like Python 3.12 or 3.13)*
```bash
pip install -r requirements.txt
```
### Step 3: Add Authorized Users
Add clear, front-facing photos of authorized personnel into the `known_faces/` folder.
* **Filename format:** `firstname_lastname.jpg` (e.g., `abc.jpg`)
* *Note: The system extracts the filename to generate the attendance log.*

### Step 4: Run the Kiosk
Launch the native application:
```bash
python kiosk_gui.py
```
* **To check in/out:** Click the respective UI buttons and face the camera.
* **To export data:** Click "Admin Export", enter the password (`<password>`), and check your Desktop for the generated Excel file.

## Author

**_Abhiroop Gohar_**
* Developed for Mega Healthcare, Lucknow

# Smart Face Attendance System with Flask & OpenCV

A real-time biometric attendance solution that integrates computer vision with a web-based management interface.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-DNN-red) ![Flask](https://img.shields.io/badge/Flask-Backend-green) ![Status](https://img.shields.io/badge/Status-Active-success)
--- 
## Introduction
This project automates the traditional attendance process using Facial Recognition. It leverages a Deep Neural Network (DNN) for robust face detection and a lightweight embedding technique for recognition. The system launches a live camera window to mark attendance and instantly logs the data into a secure Word Document (.docx), accessible via a Flask API.

## Repository Structure
```
automated-face-attendance/
├── known_faces/              # Database of authorized users (add JPGs here)
├── app.py                    # Flask API for triggering the system
├── attendance.py             # Core recognition logic & logging script
├── get.py                    # Helper script to retrieve logs
├── deploy.prototxt.txt       # Caffe model architecture
├── res10_300x300...model     # Pre-trained face detection weights
├── requirements.txt          # List of dependencies
└── README.md                 # Documentation
```
## Key Features

* **Live Recognition Window:** Opens a real-time video feed that detects faces, draws bounding boxes, and displays names with confidence scores.
* **Automated Logging:** Instantly marks attendance in a daily report file (Attendance_Log.docx) with the exact Date and Time.
* **Flask Integration:** Includes a REST API to trigger recognition or fetch attendance records remotely.
* **Hybrid Architecture:** Uses a pre-trained ResNet-10 SSD for high-accuracy detection and a custom pixel-based embedding for lightweight recognition.

## Tech Stack & Methodology

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Detection** | OpenCV DNN (Caffe) | Single Shot Detector (SSD) framework with ResNet-10 backbone. |
| **Recognition** | NumPy & Cosine Similarity | Flattened 100x100 pixel vectors compared using cosine distance. |
| **Backend** | Flask | Exposes endpoints like /record and /attendance. |
| **Reporting** | Python-Docx | Automates MS Word document generation. |

## Results & Analysis

### 1. Detection Model (SSD)
We utilize a Single Shot Detector (SSD) with a ResNet-10 backbone. Unlike Haar Cascades, this DNN approach is robust against:
* Partial occlusions.
* Varying lighting conditions.
* Side-profile faces (up to ~45 degrees).

### 2. Recognition Logic
The system computes a similarity score between the live face and the database using Cosine Similarity:

$$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$

* **Threshold:** A strict confidence threshold of 0.55 is applied.
* **Performance:** Matches are processed in real-time (<100ms latency) on standard CPU hardware without needing a GPU.

## Installation & Usage

### Step 1: Clone
```bash
git clone [https://github.com/stark-069/automated-face-attendance.git](https://github.com/stark-069/automated-face-attendance.git)
cd automated-face-attendance
```
### Step 2: Install requirements
```
pip install -r requirements.txt
```
### Step 3: Add Users
Add clear photos of the people you want to recognize into the `known_faces/` folder.
* **Filename format:** `name.jpg` (e.g., `lab.jpg`)
* *Note: Ensure the face is clearly visible and well-lit.*

### Step 4: Run the System
You can run the system in two modes depending on your needs.

**Option A: Standalone Mode (Terminal)**
Run this command to launch the recognition window immediately:
```bash
python attendance.py
# Press 'q' on your keyboard to quit the camera window
```
**Option B: Web Server Mode (Flask)**
 Run this command to start the web API:
```
python app.py
# Once running, open your browser and go to:
# [http://127.0.0.1:5000/record](http://127.0.0.1:5000/record)
```
## References

1.  **Liu, W., et al. (2016).** SSD: Single Shot MultiBox Detector. *European Conference on Computer Vision (ECCV)*.
2.  **He, K., et al. (2016).** Deep Residual Learning for Image Recognition. *CVPR*.
3.  **OpenCV Documentation.** Deep Learning with OpenCV DNN Module.

## Author

**_Abhiroop Gohar_**
* B.Tech Engineering Physics, IIT Indore

{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\froman\fcharset0 Times-Roman;\f2\froman\fcharset0 Times-Bold;
}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Smart Face Attendance System with Flask & OpenCV\
\
A real-time biometric attendance solution that integrates computer vision with a web-based management interface.\
\
![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-DNN-red) ![Flask](https://img.shields.io/badge/Flask-Backend-green) ![Status](https://img.shields.io/badge/Status-Active-success)\
\
## Introduction\
This project automates the traditional attendance process using Facial Recognition. It leverages a Deep Neural Network (DNN) for robust face detection and a lightweight embedding technique for recognition. The system launches a live camera window to mark attendance and instantly logs the data into a secure Word Document (.docx), accessible via a Flask API.\
\
## Repository Structure\
\
flask-face-attendance/\
\uc0\u9500 \u9472 \u9472  known_faces/              # Database of authorized users (add JPGs here)\
\uc0\u9500 \u9472 \u9472  app.py                    # Flask API for triggering the system\
\uc0\u9500 \u9472 \u9472  attendance.py             # Core recognition logic & logging script\
\uc0\u9500 \u9472 \u9472  get.py                    # Helper script to retrieve logs\
\uc0\u9500 \u9472 \u9472  deploy.prototxt.txt       # Caffe model architecture\
\uc0\u9500 \u9472 \u9472  res10_300x300...model     # Pre-trained face detection weights\
\uc0\u9500 \u9472 \u9472  requirements.txt          # List of dependencies\
\uc0\u9492 \u9472 \u9472  README.md                 # Documentation\
\
## Key Features\
\
* **Live Recognition Window:** Opens a real-time video feed that detects faces, draws bounding boxes, and displays names with confidence scores.\
* **Automated Logging:** Instantly marks attendance in a daily report file (Attendance_Log.docx) with the exact Date and Time.\
* **Flask Integration:** Includes a REST API to trigger recognition or fetch attendance records remotely.\
* **Hybrid Architecture:** Uses a pre-trained ResNet-10 SSD for high-accuracy detection and a custom pixel-based embedding for lightweight recognition.\
\
## Tech Stack & Methodology\
\
| Component | Technology | Description |\
| :--- | :--- | :--- |\
| **Detection** | OpenCV DNN (Caffe) | Single Shot Detector (SSD) framework with ResNet-10 backbone. |\
| **Recognition** | NumPy & Cosine Similarity | Flattened 100x100 pixel vectors compared using cosine distance. |\
| **Backend** | Flask | Exposes endpoints like /record and /attendance. |\
| **Reporting** | Python-Docx | Automates MS Word document generation. |\
\
## Results & Analysis\
\
### 1. Detection Model (SSD)\
We utilize a Single Shot Detector (SSD) with a ResNet-10 backbone. Unlike Haar Cascades, this DNN approach is robust against:\
* Partial occlusions.\
* Varying lighting conditions.\
* Side-profile faces (up to ~45 degrees).\
\
### 2. Recognition Logic\
The system computes a similarity score between the live face and the database using Cosine Similarity:\
\
$$\\text\{Similarity\}(A, B) = \\frac\{A \\cdot B\}\{\\|A\\| \\|B\\|\}$$\
\
* **Threshold:** A strict confidence threshold of 0.55 is applied.\
* **Performance:** Matches are processed in real-time (<100ms latency) on standard CPU hardware without needing a GPU.\
\
## Installation & Usage\
\
### Step 1: Clone & Install\
```bash\
git clone [https://github.com/your-username/flask-face-attendance.git](https://github.com/your-username/flask-face-attendance.git)\
cd flask-face-attendance\
pip install -r requirements.txt\
\
### Step 2: Add Users\
Add clear photos of the people you want to recognize into the `known_faces/` folder.\
* **Filename format:** `name.jpg` (e.g., `abhiroop.jpg`)\
* *Note: Ensure the face is clearly visible and well-lit.*\
\
### Step 3: Run the System\
You can run the system in two modes depending on your needs.\
\
\pard\pardeftab720\partightenfactor0

\f1 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 **Option A: Standalone Mode (Terminal)** \
Run this command to launch the recognition window immediately: \
```bash \
python attendance.py # Press 'q' on your keyboard to quit the camera window\
\
\pard\pardeftab720\partightenfactor0

\f2\b \cf0 \strokec2 **Option B: Web Server Mode (Flask)**\
\pard\pardeftab720\partightenfactor0

\f1\b0 \cf0 \strokec2  Run this command to start the web API
\f0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 python app.py\
# Once running, open your browser and go to:\
# [http://127.0.0.1:5000/record](http://127.0.0.1:5000/record)\
\
## References\
\
1.  **Liu, W., et al. (2016).** SSD: Single Shot MultiBox Detector. *European Conference on Computer Vision (ECCV)*.\
2.  **He, K., et al. (2016).** Deep Residual Learning for Image Recognition. *CVPR*.\
3.  **OpenCV Documentation.** Deep Learning with OpenCV DNN Module.\
\
## Author\
\
**_Abhiroop Gohar_**\
* B.Tech Engineering Physics, IIT Indore\
}
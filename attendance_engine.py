import cv2
import numpy as np
import os
import db_manager
from deepface import DeepFace

# --- CONFIGURATION ---
PROTOTXT = "deploy.prototxt.txt"
CAFFEMODEL = "res10_300x300_ssd_iter_140000.caffemodel"
KNOWN_DIR = "known_faces"

CONF_THRES = 0.80   # Detector confidence
DISTANCE_THRES = 0.40 # Distance for a successful face match

class AttendanceEngine:
    def __init__(self):
        print("[INFO] Loading OpenCV Face Detector...")
        self.detector = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
        self.gallery = {}
        
        print("[INFO] Initializing DeepFace Engine & Anti-Spoofing...")
        try:
            dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
            # Booting up FaceNet and the Fasnet Anti-Spoofing models in memory
            DeepFace.represent(dummy_img, model_name="Facenet", enforce_detection=False, anti_spoofing=True)
        except Exception:
            pass
            
        self.build_gallery()

    def build_gallery(self):
        if not os.path.exists(KNOWN_DIR):
            os.makedirs(KNOWN_DIR)
            print(f"[WARNING] Created {KNOWN_DIR}/ folder. Add employee JPGs!")
            return

        print("[INFO] Building Facial Gallery using Google FaceNet...")
        for f in os.listdir(KNOWN_DIR):
            if not f.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            
            path = os.path.join(KNOWN_DIR, f)
            name = os.path.splitext(f)[0]
            
            try:
                # We do NOT use anti-spoofing here, because the gallery images ARE flat photos
                result = DeepFace.represent(img_path=path, model_name="Facenet", enforce_detection=True)
                if len(result) > 0:
                    self.gallery[name.lower()] = result[0]["embedding"]
                    print(f"[INFO] Loaded secure profile for: {name.title()}")
            except Exception as e:
                print(f"[ERROR] Could not process {f}. Error: {e}")

    def cosine_distance(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def process_frame(self, frame, mode):
        frame_resized = cv2.resize(frame, (640, 480))
        h, w = frame_resized.shape[:2]
        
        # 1. Fast Caffe Detector (ONLY used to draw the box on the UI)
        blob = cv2.dnn.blobFromImage(frame_resized, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False)
        self.detector.setInput(blob)
        detections = self.detector.forward()

        best_conf = 0
        best_box = None

        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf > CONF_THRES and conf > best_conf:
                best_conf = conf
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                best_box = box.astype("int")

        recognized_name = None
        status_msg = ""

        if best_box is not None:
            x1, y1, x2, y2 = best_box
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            try:
                # --- ENTERPRISE FIX ---
                # Pass the ENTIRE uncropped frame to DeepFace so it can see the phone/paper edges.
                # We use detector_backend="opencv" so DeepFace finds the face itself and checks the background context.
                res = DeepFace.represent(
                    img_path=frame_resized, 
                    model_name="Facenet", 
                    detector_backend="opencv", 
                    enforce_detection=True,
                    anti_spoofing=True
                )
                
                emb = res[0]["embedding"]
                is_real = res[0].get("is_real", True) 
                
                # 1. Check Liveness First
                if not is_real:
                    recognized_name = "Unknown"  # Forces UI to show error
                    status_msg = "SPOOF DETECTED: Phone screen or paper found."
                    color = (0, 0, 255) # Red Box
                    cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame_resized, "SPOOF DETECTED", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                # 2. If Real, Check Identity
                else:
                    best_name = "Unknown"
                    best_dist = float("inf")

                    for name, g_emb in self.gallery.items():
                        dist = self.cosine_distance(emb, g_emb)
                        if dist < best_dist:
                            best_dist = dist
                            best_name = name

                    if best_dist < DISTANCE_THRES:
                        recognized_name = best_name.title()
                        color = (0, 255, 0) # Green Box
                        
                        success, db_msg = db_manager.log_attendance(best_name, mode)
                        status_msg = db_msg if success else "Error logging data."
                        
                        cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame_resized, f"{recognized_name} ({best_dist:.2f})", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    else:
                        color = (0, 0, 255) # Red Box
                        cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame_resized, f"Unknown ({best_dist:.2f})", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            except Exception as e:
                # If DeepFace can't find a face in the frame, fail silently and keep trying
                pass 

        return frame_resized, recognized_name, status_msg
"""
Realtime face‑recognition attendance
• OpenCV DNN face detector (SSD)
• Very simple “embedding” = 100×100 flattened pixels
• Logs each recognised person once per day to Word (.docx) 
"""
import cv2, os, numpy as np
from datetime import datetime
from docx import Document    # pip install python-docx

# -------------------- CONFIG --------------------
PROTOTXT   = "deploy.prototxt.txt"
CAFFEMODEL = "res10_300x300_ssd_iter_140000.caffemodel"
KNOWN_DIR  = "known_faces"
EMBED_SIZE = (100, 100)      # width, height of tiny face “embedding”
CONF_THRES = 0.90            # face‑detection confidence
SIM_THRES  = 0.55            # cosine similarity to accept a match
# ------------------------------------------------

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_embedding(img):
    """Detect first face, return flattened 100×100 embedding & box"""
    h, w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0), swapRB=False)
    face_net.setInput(blob)
    dets = face_net.forward()

    for i in range(dets.shape[2]):
        conf = dets[0, 0, i, 2]
        if conf > CONF_THRES:
            x1, y1, x2, y2 = (dets[0, 0, i, 3:7] *
                              np.array([w, h, w, h])).astype(int)
            face = img[max(0,y1):y2, max(0,x1):x2]
            if face.size:
                face = cv2.resize(face, EMBED_SIZE).astype("float32")/255.0
                return face.flatten(), (x1, y1, x2, y2)
    return None, None

# 1️⃣ load detector
face_net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)

# 2️⃣ build gallery
gallery = {}
for f in os.listdir(KNOWN_DIR):
    path = os.path.join(KNOWN_DIR, f)
    img  = cv2.imread(path)
    if img is None: continue
    name = os.path.splitext(f)[0]
    emb, _ = get_embedding(img)
    if emb is not None:
        gallery[name.lower()] = emb
        print(f"[loaded] {name}")

if not gallery:
    print("❌ No faces in known_faces/. Add at least one JPG & restart.")
    exit()

# 3️⃣ Word document for today
# File path for persistent attendance log
filename = "Attendance_Log.docx"

# Create document if it doesn't exist
if not os.path.exists(filename):
    doc = Document()
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Date'
    hdr_cells[1].text = 'Time'
    hdr_cells[2].text = 'Name'
else:
    doc = Document(filename)
    table = doc.tables[0]
logged_today = set() 
def mark_attendance(name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    row_cells = table.add_row().cells
    row_cells[0].text = date_str
    row_cells[1].text = time_str
    row_cells[2].text = name

    doc.save(filename)



# 4️⃣ Camera loop
cap = cv2.VideoCapture(0)
print("▶ Camera running – press q to quit.")
while True:
    ok, frame = cap.read()
    if not ok: break

    emb, box = get_embedding(frame)
    if emb is not None:
        # find best match
        best_name, best_sim = "Unknown", 0
        for name, g_emb in gallery.items():
            sim = cosine(emb, g_emb)
            if sim > best_sim:
                best_name, best_sim = name, sim
        if best_sim > SIM_THRES:
            x1,y1,x2,y2 = box
            colour = (0,255,0); label = best_name
            cv2.putText(frame, f"Attendance Recorded,press q",
                (x2, y2-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
        else:
            colour = (0,0,255); label = "Unknown"

        # draw
        x1,y1,x2,y2 = box
        cv2.rectangle(frame,(x1,y1),(x2,y2),colour,2)
        cv2.putText(frame, f"{label} {best_sim:.2f}",
                    (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
    cv2.imshow("Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
mark_attendance(best_name)
cap.release(); cv2.destroyAllWindows()

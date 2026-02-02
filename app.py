from flask_cors import CORS
from flask import Flask, jsonify
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Face Recognition Attendance System'

@app.route('/record')
def record_attendance():
    try:
        # Call the face recognition script
        subprocess.run(['python3', 'attendance.py'])  # Use 'python' if not using python3
        return jsonify({'status': 'success', 'message': 'Attendance recorded'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
@app.route('/attendance')
def get_attendance():
    try:
        data=get.get_attendance()
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
if __name__ == '__main__':
    app.run(debug=True)

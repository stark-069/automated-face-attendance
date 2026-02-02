from flask import Flask, jsonify
from docx import Document
import os

app = Flask(__name__)

@app.route('/attendance', methods=['GET'])
def get_attendance():
    try:
        doc = Document("Attendance_Log.docx")  # Adjust if needed
        records = []

        # Loop through all tables (in case there’s more than one)
        for table in doc.tables:
            for row in table.rows[1:]:  # Skip header row if there's one
                cells = row.cells
                if len(cells) >= 3:
                    name = cells[0].text.strip()
                    date = cells[1].text.strip()
                    time = cells[2].text.strip()

                    if name and date and time:
                        records.append({
                            "name": name,
                            "date": date,
                            "time": time
                        })

        return jsonify({"status": "success", "records": records})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
if __name__ == "__main__":
    app.run(debug=True)
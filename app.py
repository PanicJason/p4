from flask import Flask, render_template, jsonify, request
import cv2
import numpy as np
import base64
import db_connection
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_result', methods=['GET'])
def get_result():
    data = db_connection.get_data_from_assist_test()
    return jsonify(data)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 4)
    
    _, buffer = cv2.imencode('.jpg', img)
    image_as_text = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'image': f'data:image/jpg;base64,{image_as_text}'})

@app.route('/get_filtered_result', methods=['POST'])
def get_filtered_result():
    try:
        file_name = request.form.get('file_name')
        data = db_connection.get_data_from_assist_test(file_name)

        # Check if data is empty or not found
        if not data:
            return jsonify({'type': ['None']})

        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

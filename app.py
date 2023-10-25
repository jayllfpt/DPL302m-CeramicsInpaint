from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import base64
import datetime
from static.run_model import run

app = Flask(__name__)
# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inpaint', methods=['POST'])
def upload():
    cropped_image_base64 = request.form['croppedImage']
    if cropped_image_base64:
        # Convert the base64 data to binary
        cropped_image_binary = base64.b64decode(cropped_image_base64.split(',')[1])

        filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Save the cropped image as a .png file in the "uploads" folder
        with open(filepath, 'wb') as f:
            f.write(cropped_image_binary)

         # Process the image
        _path_masked = "masked.png"
        _path_result = "inpainted_result.png"
        run(path_org_image=filepath) 

        return render_template("result.html", filename=filename, masked = _path_masked, result = _path_result)   

    return "Cropped image saved successfully!"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()

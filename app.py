from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from static.run_model import run

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/crop')
def crop():
    return render_template('crop.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty part without a filename
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        # Save the uploaded file to the upload folder
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image
        _path_masked = "masked.png"
        _path_result = "inpainted_result.png"
        run(path_org_image=file_path)
        return redirect(url_for('display', filename=filename, masked = _path_masked, result = _path_result))

@app.route('/display/<filename>/<masked>/<result>')
def display(filename, masked, result):
    return render_template('display.html', filename=filename, masked=masked, result = result)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# if __name__ == '__main__':
#     app.run(debug=True)
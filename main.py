from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os
import cv2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Needed to use flash messages

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}")
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    if img is None:
        print("Error: Could not read the image.")
        return None

    new_filename = None
    if operation == "cgray":
        img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        new_filename = f"{filename.split('.')[0]}_gray.png"
        cv2.imwrite(os.path.join('static', new_filename), img_processed)
    elif operation == "cwebp":
        new_filename = f"{filename.split('.')[0]}.webp"
        cv2.imwrite(os.path.join('static', new_filename), img)
    elif operation == "cjpg":
        new_filename = f"{filename.split('.')[0]}.jpg"
        cv2.imwrite(os.path.join('static', new_filename), img)
    elif operation == "cpng":
        new_filename = f"{filename.split('.')[0]}.png"
        cv2.imwrite(os.path.join('static', new_filename), img)

    return os.path.join('static', new_filename) if new_filename else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
    
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("index.html", error="No file part")
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return render_template("index.html", error="No selected file")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            processed_file_path = processImage(filename, operation)
            if processed_file_path:
                flash(f"Your image has been processed and is available <a href='/{processed_file_path}' target='_blank'>here</a>")
                return render_template("index.html", success="File successfully uploaded and processed", image_url=processed_file_path)
            else:
                flash('Image processing failed')
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

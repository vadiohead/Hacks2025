from flask import Flask, render_template, request, redirect, url_for, current_app
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from PIL import Image
from io import BytesIO
import face_recognition
import cv2
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)




# global variable for site to check
url = ''
# global variable the picture path
filepath = ''

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class FakePic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String)

with app.app_context():
    db.create_all()

uploaded_images = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_existing_images():
    global uploaded_images
    uploaded_images = []
    uploads_dir = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            uploaded_images.append({
                'filename': filename,
                'title': os.path.splitext(filename)[0],
                'timestamp': datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(uploads_dir, filename))
                ).strftime("%d/%m/%Y %H:%M")
            })
# Path where feed images are stored

load_existing_images()

FEED_FOLDER = os.path.join('static', 'images')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/images', methods=['GET', 'POST'])
def images():
    if request.method == 'POST':
        file = request.files.get('image')
        title = request.form.get('title')
        if file and allowed_file(file.filename) and title:
            # Get the file extension
            ext = file.filename.rsplit('.', 1)[1].lower()
            # Make the title safe and add extension
            safe_title = secure_filename(title)
            filename = f"{safe_title}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            uploaded_images.insert(0, {
                'filename': filename,
                'title': title,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            return redirect(url_for('images'))

    return render_template('images.html', images=uploaded_images)

@app.route('/videos')
def videos():
    return render_template('videos.html')

@app.route('/audios')
def audios():
    return render_template('audios.html')

@app.route('/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        return 'No file part'

    if request.form['url'] == '':
        return 'no site to search'
    url = request.form['url']
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        imageList = []



        known_image = face_recognition.load_image_file(filepath)
        known_face_encoding = face_recognition.face_encodings(known_image)[0]
        req = requests.get(url)
        soup2 = BeautifulSoup(req.text, "html.parser")

        images = soup2.find_all("img")

        for img in images:

            if test(img.get("src"), known_face_encoding) == True:
                imageList.append(img.get("src"))


        return render_template("index.html", images=imageList)
        



@app.route('/analyze', methods=['POST'])
def analyze():
    imageList = []

    global url
    global filepath


    known_image = face_recognition.load_image_file(filepath)
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    request = requests.get(url)
    soup2 = BeautifulSoup(request.text, "html.parser")

    images = soup2.find_all("img")

    for img in images:

        if test(img.get("src"), known_face_encoding) == True:
            imageList.append(img.get("src"))


    print(imageList)
    return render_template("analyzer.html", images=imageList)

def test(img, enc):
    # Download the image from the URL
    modified_string = img.lstrip(img[0])
    file_path = os.path.join(current_app.root_path, modified_string)

    unknown_image = face_recognition.load_image_file(file_path)
    unknown_face_encoding = face_recognition.face_encodings(unknown_image)
    # no faces found
    if len(unknown_face_encoding) == 0:
        return False


    results = face_recognition.compare_faces([enc], unknown_face_encoding[0])

    return results[0]

if __name__ == '__main__':
    app.run(debug=True)

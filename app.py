from flask import Flask, render_template, request, redirect, url_for, current_app
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

if __name__ == '__main__':
    app.run(debug=True)

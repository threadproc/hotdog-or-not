from flask import Flask, flash, request, redirect, url_for, render_template
import os
import os.path
import pathlib
import time
from flask.helpers import send_from_directory

from werkzeug.utils import secure_filename

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER") or "uploads"
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
HOTDOG_ID = "n07697537"

# some tensorflow config to allow this to work on the jetson nano
gpus = tf.config.list_physical_devices('GPU')
if len(gpus) > 0:
    tf.config.experimental.set_memory_growth(gpus[0], True)
    tf.config.experimental.set_virtual_device_configuration(
        gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=256)])

model = MobileNetV2(weights='imagenet')


def predict_image(filename):
    img = image.load_img(filename, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return decode_predictions(model.predict(x), top=3)[0]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prune_uploads():
    now = time.time()
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        fn = pathlib.Path(os.path.join(app.config['UPLOAD_FOLDER'], f))
        age = now - fn.stat().st_mtime
        if age > 24 * 60 * 60:
            print("Deleting ", f)
            fn.unlink()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        prune_uploads()

        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('predicted_file', filename=filename))

    return render_template('home.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/predict/<filename>')
def predicted_file(filename):

    base_fn = filename

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filename):
        return redirect('/')

    preds = predict_image(filename)

    is_hotdog = len(preds) >= 1 and preds[0][0] == HOTDOG_ID

    print(preds)
    return render_template('prediction.html', predictions=preds, is_hotdog=is_hotdog, filename=base_fn)

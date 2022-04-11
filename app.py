from flask import Flask, render_template, request, redirect, url_for
from os.path import join, dirname, realpath
from glob import glob
import numpy as np
import os
import cv2,imutils
import tensorflow as tf

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/videos')
FRAMES_PATH = "video_frames"
RESIZED_FRAMES_PATH = join(dirname(realpath(__file__)), 'static/resized_frames')

app = Flask(__name__, template_folder='template')
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        os.makedirs(UPLOADS_PATH)
        if request.files:
            video = request.files['video']
            video.save(os.path.join(UPLOADS_PATH, video.filename))
            os.makedirs(FRAMES_PATH)
            return redirect(url_for('frames'))
    return render_template('index.html')

@app.route('/frames')
def frames():
    os.makedirs(RESIZED_FRAMES_PATH)
    def save_frame(video_path, gap):
        images_array = []
        name = video_path.split("\\")[1].split(".")[0]
        cap = cv2.VideoCapture(video_path)
        idx = 0

        while True:
            ret, frame = cap.read()
            if ret == False:
                cap.release()
                break
            if frame is None:
                break
            else:
                if idx == 0:
                    images_array.append(frame)
                    cv2.imwrite(f"video_frames/{idx}.jpeg", frame)
                else:
                    if idx % gap == 0:
                        images_array.append(frame)
                        cv2.imwrite(f"video_frames/{idx}.jpeg", frame)
            idx += 1
        return np.array(images_array)

    video_paths = glob("static/uploads/videos/*")
    for path in video_paths:
        array_of_images = save_frame(path, gap=10)
        return redirect(url_for('resize'))

    return render_template('frames.html')

@app.route('/resize')
def resize():  
    def resize_frames():
        frame_paths = glob(f"video_frames/*.jpeg")
        index = 0
        width, height = (299, 299)

        for frame in frame_paths:
            image = cv2.imread(frame)
            imgResized = cv2.resize(image, (299, 299))
            cv2.imwrite("static/resized_frames/%i.jpeg"%index, imgResized)
            
            index += 1   
    resize_frames()
    return redirect(url_for('index'))

@app.route('/delete')
def delete():
    videos = glob('static/uploads/videos/*')
    for video in videos:
        os.remove(video)

    frames = glob('video_frames/*.jpeg')
    for frame in frames:
        os.remove(frame)

    resized_frames = glob('static/resized_frames/*.jpeg')
    for resized_frame in resized_frames:
        os.remove(resized_frame)

    if os.path.exists('static/uploads/videos'):
        os.rmdir('static/uploads/videos')

    if os.path.exists('static/uploads'):
        os.rmdir('static/uploads')

    if os.path.exists(FRAMES_PATH):
        os.rmdir(FRAMES_PATH)
    
    if os.path.exists(RESIZED_FRAMES_PATH):
        os.rmdir(RESIZED_FRAMES_PATH)

    return redirect(url_for('index'))

@app.route('/predict', methods=['POST','GET'])
def predict():
    def fetch_frames():
        frame_paths = glob(f"static/resized_frames/*.jpeg")
        query_frames_array = []

        for frame in frame_paths:
            image = cv2.imread(frame)
            query_frames_array.append(image)
        return np.array(query_frames_array)

    query_frames_array = fetch_frames()
    video_frame_classifier = tf.keras.models.load_model('saved_model/frame_classifier')
    query_results = video_frame_classifier.predict(query_frames_array)
    decoded_query_results = tf.keras.applications.inception_v3.decode_predictions(query_results, top=5)

    def showResults(images_array, decoded_response):
        search_query_value = request.form['search_query']
        for i in range(len(decoded_response)):
            class_tupple = decoded_response[i]
            _id, frame_class, frame_prob = class_tupple[0]
            image_index = i
            if search_query_value == '':
                pass
            elif search_query_value == frame_class:
                image_index = i
                break
        return i, frame_class
    image_index, frame_class = showResults(query_frames_array,decoded_query_results)
    return render_template('index.html',index=image_index, class_name=frame_class)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as server:
        print('serving on port 8000...')
        server.serve_forever()
    
    

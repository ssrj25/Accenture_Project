# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask import Flask
bp = Blueprint('main', __name__)

import os
import time

import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 

from tqdm import tqdm 

from skimage.io import imread, imshow
from skimage.transform import resize

from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = Flask(__name__, template_folder='templates',static_folder='static')

# Define a global variable to hold the loaded model
cnn_model = None

def load_cnn_model():
    
    global cnn_model
    if cnn_model is None:
        #app\Backend
        model_path = 'app/Backend/tf_model_2.h5'
        # model_path = 'C:\\Users\\Hriday Desai\\Downloads\\Accenture-main\\Accenture-main\\Accenture\\Backend\\tf_model_2.h5'  # Replace with the actual path to your model file
        try:
            cnn_model = tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"Error loading model: {str(e)}")

load_cnn_model()

def process_image_with_cnn(model, image_path):
    
    imgPath=image_path
    img = load_img(imgPath, target_size=(128,128))
    img = img_to_array(img)
    img = img / 255
    # imshow(img)
    # plt.axis('off')

    img = np.expand_dims(img,axis=0)

    # Use the loaded model to make predictions
    # predictions = model.predict(img)
    predict_prob=model.predict(img)

    predict_classes=np.argmax(predict_prob,axis=1)
    
    
    if predict_prob[0][0] > 0.5:
        predictions="The image belongs to Recycle waste category"
    else:
        predictions="The image belongs to Organic waste category "
    return str(predictions)

# Define the quiz data as mentioned in Step 1
quiz_data = [
    {
        'question': 'Question 1?',
        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
        'correct_answer': 'Option A',
    },
    {
        'question': 'Question 2?',
        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
        'correct_answer': 'Option B',
    },{
        'question': 'Question 3?',
        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
        'correct_answer': 'Option C',
    },
    # Add more questions here...
]

# Define the correct answers for each question (assuming the same order as quiz_data)
correct_answers = [question['correct_answer'] for question in quiz_data]

@bp.route('/')
def home():
    return render_template('home.html')



@bp.route('/camsort/')
def camsort():
    return render_template('Camscan.html')


@bp.route('/process_image', methods=['POST'])
def process_image():
    global cnn_model

    if cnn_model is None:
        return jsonify(error='Error: Model not loaded')

    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            try:
                # Save the uploaded image to a temporary file
                image_path = 'temp_image.jpg'
                image.save(image_path)

                # Perform image processing using the loaded CNN model
                result = process_image_with_cnn(cnn_model, image_path)

                # Delete the temporarily saved image
                os.remove(image_path)

                # Return the processing result as a JSON response
                return result
            except Exception as e:
                print(f"Error processing image: {str(e)}")
    
    # If no image was uploaded or an error occurred, return an error message
    return jsonify(error='Error: Image processing failed')




@bp.route('/carbon_footprint')
def carbon_footprint():
    return render_template('carbon_footprint.html')

@bp.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')    

@bp.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        session['score'] = 0  # Initialize the score
        session['question_number'] = 0  # Initialize the question number
        return redirect(url_for('main.quiz_question', question_number=0))

    return render_template('quiz.html')

@bp.route('/quiz/question/<int:question_number>', methods=['GET', 'POST'])
def quiz_question(question_number):
    if 'score' not in session:
        return redirect(url_for('main.quiz'))

    if question_number >= len(quiz_data):
        return redirect(url_for('main.quiz_result'))

    question_info = quiz_data[question_number]
    question = question_info['question']
    options = question_info['options']

    if request.method == 'POST':
        selected_option = request.form.get('answer')
        correct_answer = question_info['correct_answer']

        if selected_option == correct_answer:
            session['score'] += 1

        action = request.form.get('action')

        if action == 'next':
            session['question_number'] += 1
            return redirect(url_for('main.quiz_question', question_number=question_number + 1))

    return render_template('question.html', question_number=question_number, question=question, options=options)

@bp.route('/quiz/result', methods=['GET'])
def quiz_result():
    if 'score' not in session:
        return redirect(url_for('main.quiz'))

    score = session['score']
    session.pop('score', None)
    session.pop('question_number', None)
    return render_template('result.html', score=score)

@bp.route('/show_correct_answers', methods=['POST'])
def show_correct_answers():
    # Enumerate the quiz data along with indices
    enumerated_quiz_data = list(enumerate(quiz_data, start=1))

    return render_template('correct_answers.html', enumerated_quiz_data=enumerated_quiz_data, correct_answers=correct_answers)

@bp.route('/play_again', methods=['POST'])
def play_again():
    session.pop('score', None)
    session.pop('question_number', None)
    return redirect(url_for('main.home'))


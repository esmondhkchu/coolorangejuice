import os
from flask import Flask, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename

import pickle

import pandas as pd
import numpy as np

app = Flask(__name__)

global model
model = pickle.load(open('./model_rf.sav', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))
        return redirect(url_for('prediction', filename=filename))
    return render_template('index.html')

@app.route('/prediction/<filename>')
def prediction(filename):

    data = pd.read_excel(os.path.join('uploads', filename))

    # probabilities
    probabilities = model.predict_proba(data)[:,1]

    # sort
    sorted_prob = np.sort(probabilities)[::-1]
    sorted_hor_num = np.argsort(probabilities)[::-1] + 1

    # make prediction dictionary
    predictions = {i:'{}%'.format(round(j*100, 2)) for i,j in zip(sorted_hor_num, sorted_prob)}

    # append to 14
    append_total = (14-len(sorted_prob))
    append_stuffs = ['NA']*append_total

    # append to 14 to final result
    for i,j in zip(range(len(sorted_prob)+1, 15), append_stuffs):
        predictions[i] = j

    df = pd.DataFrame({'horse':list(predictions.keys()), 'probability':list(predictions.values())})
    df_html = df.to_html(index=False, classes='data')

    return render_template('predict.html', tables=[df_html], predictions=predictions)

app.run(host='0.0.0.0', port=80)

##

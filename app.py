import pymysql
import pymysql.cursors
from flask import Flask, render_template, url_for, redirect, session, request
from dotenv import dotenv_values
import csv
import random
import pickle
import os

config = dotenv_values(".env")
app = Flask(__name__)

# Secret key
app.secret_key = config['SECRET_KEY']

# Read the pid file to get the last assigned pid
with open('pid.txt', 'r') as f:
    PID = int(f.readline())
    PID += 1

SAMPLES = {}
with open('samples.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, quotechar='"')
    for row in reader:
        SAMPLES[row['id']] = row['text']

@app.route('/', methods=["GET"])
def index(pid = PID):
    # Create session data
    if 'participant' not in session:
        session['participant'] = pid
        pid += 1
        # store new pid
        with open('pid.txt', 'w') as f:
            f.write(f"{pid}")

    return render_template('index.jinja')

@app.route('/research', methods=["GET", "POST"])
def research():
    if request.method == "GET":
        # Load 2 samples
        samples = []
        idx_1 = random.randint(0, 25)
        idx_2 = random.randint(0, 25)
        while idx_2 == idx_1:
            idx_2 = random.randint(0, 25)
        # Store these values
        session['idx_1'] = idx_1
        session['idx_2'] = idx_2
        for idx in [idx_1, idx_2]:
            samples.append(SAMPLES[str(idx)])
        return render_template('research.jinja', samples=samples)

    if request.method == "POST":
        # Parse form response
        result = request.form['ident']
        # record data
        with open('results.csv', 'a', newline='') as csvfile:
            fieldnames = ['id1', 'id2', 'result']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'id1': session['idx_1'], 'id2': session['idx_2'], 'result': result})
        # redirect to self for next fp1
        return redirect(url_for('research'))

if __name__ == "__main__":
    app.run(debug=True)
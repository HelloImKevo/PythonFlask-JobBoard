#!/usr/bin/env python3

from flask import Flask
from flask import render_template

app: Flask = Flask(__name__)


@app.route('/')
@app.route('/jobs')
def jobs():
    return render_template('index.html')

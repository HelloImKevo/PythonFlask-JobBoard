#!/usr/bin/env python3

import datetime
import sqlite3
from flask import g
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

PATH = 'db/jobs.sqlite'

app: Flask = Flask(__name__)


def open_connection() -> sqlite3.Connection:
    connection = getattr(g, '_connection', None)
    if connection is None:
        connection = g._connection = sqlite3.connect(PATH)
    connection.row_factory = sqlite3.Row
    return connection


def execute_sql(sql: str, values: tuple = (),
                commit: bool = False, single: bool = False):
    connection = open_connection()
    cursor = connection.execute(sql, values)
    if commit is True:
        results = connection.commit()
    else:
        results = cursor.fetchone() if single else cursor.fetchall()

    cursor.close()
    return results


@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, '_connection', None)
    if connection is not None:
        connection.close()


@app.route('/')
@app.route('/jobs')
def jobs():
    query = ("SELECT job.id, job.title, job.description, job.salary, " +
             "employer.id as employer_id, employer.name as employer_name " +
             "FROM job " +
             "JOIN employer ON employer.id = job.employer_id")
    jobs = execute_sql(query)
    return render_template('index.html', jobs=jobs)


@app.route('/job/<job_id>')
def job(job_id):
    query = ("SELECT job.id, job.title, job.description, job.salary, "
             "employer.id as employer_id, employer.name as employer_name "
             "FROM job "
             "JOIN employer ON employer.id = job.employer_id "
             "WHERE job.id = ?")
    job = execute_sql(query, job_id, single=True)
    return render_template('job.html', job=job)


@app.route('/employer/<employer_id>')
def employer(employer_id):
    # Debugging code
    print(type(employer_id), employer_id)
    print(type(request.data), request.data)
    for argument in request.args:
        print(type(argument), argument)

    # SQL parameter bindings must be a tuple (iterable) - input parameter is a string
    employer_id: tuple = (employer_id,)
    employer = execute_sql('SELECT * FROM employer WHERE id = ?', employer_id, single=True)
    jobs_query = ("SELECT job.id, job.title, job.description, job.salary " +
                  "FROM job " +
                  "JOIN employer ON employer.id = job.employer_id " +
                  "WHERE employer.id = ?")
    jobs = execute_sql(jobs_query, employer_id)
    reviews_query = ("SELECT review, rating, title, date, status " +
                     "FROM review " +
                     "JOIN employer ON employer.id = review.employer_id " +
                     "WHERE employer.id = ?")
    reviews = execute_sql(reviews_query, employer_id)
    return render_template('employer.html', employer=employer, jobs=jobs, reviews=reviews)


@app.route('/employer/<employer_id>/review', methods=('GET', 'POST'))
def review(employer_id):
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        title = request.form['title']
        status = request.form['status']

        date = datetime.datetime.now().strftime("%m/%d/%Y")
        execute_sql('INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)',
                    (review, rating, title, date, status, employer_id), commit=True)

        return redirect(url_for('employer', employer_id=employer_id))

    return render_template('review.html', employer_id=employer_id)

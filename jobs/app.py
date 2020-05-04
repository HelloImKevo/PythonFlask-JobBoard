#!/usr/bin/env python3

import sqlite3
from flask import g
from flask import Flask
from flask import render_template

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

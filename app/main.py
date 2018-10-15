import json
import web3
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db
from web3 import Web3, HTTPProvider

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    questions = db.execute(
        'SELECT q.id, title, body, created, user_id, username'
        ' FROM question q JOIN user u ON q.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('question/index.html', questions=questions)

@bp.route('/question/create', methods=('GET', 'POST'))
@login_required
def question_create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        price = request.form['price']
        error = None

        if not title:
            error = 'Title is required.'
        elif not price:
            error = 'Price is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO question (title, body, price, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, price, g.user['id'])
            )
            db.commit()
            return redirect(url_for('main.index'))

    return render_template('question/create.html')

@bp.route('/question/<int:question_id>/answer')
def answer_index(question_id):
    db = get_db()
    question = db.execute(
        'SELECT id, title, body, created, user_id'
        ' FROM question'
        ' WHERE id = (?)',
        (str(question_id))
    ).fetchone()
    answers = db.execute(
        'SELECT id, body, created, user_id'
        ' FROM answer'
        ' WHERE answer.question_id = (?)',
        (str(question_id))
    ).fetchall()
    return render_template('answer/index.html', question=question, answers=answers)

@bp.route('/question/<int:question_id>/answer/create', methods=('GET', 'POST'))
@login_required
def answer_create(question_id):
    db = get_db()

    question = db.execute(
        'SELECT id, price, user_id'
        ' FROM question'
        ' WHERE id = (?)',
        (str(question_id),)
    ).fetchone()

    if g.user['id'] != question['user_id']:
        if request.method == 'POST':
            body = request.form['body']
            error = None

            if not body:
                error = 'Body is required.'

            if error is not None:
                flash(error)
            else:
                db.execute(
                    'INSERT INTO answer (body, question_id, user_id)'
                    ' VALUES (?, ?, ?)',
                    (body, str(question_id), g.user['id'])
                )
                db.commit()
                return redirect(url_for('main.answer_index', question_id=str(question_id)))

        return render_template('answer/create.html')
    else:
        error = 'Invalid Access'
        flash(error)
        return redirect(url_for('main.answer_index', question_id=str(question_id)))

@bp.route('/question/<int:question_id>/answer/<int:answer_id>/reward')
@login_required
def reward(question_id, answer_id):
    db = get_db()
    error = None

    question = db.execute(
        'SELECT id, price, user_id'
        ' FROM question'
        ' WHERE id = (?)',
        (str(question_id),)
    ).fetchone()
    answer = db.execute(
        'SELECT id, user_id'
        ' FROM answer'
        ' WHERE id = (?)',
        (str(answer_id),)
    ).fetchone()
    answerer = db.execute(
        'SELECT id, eth_address'
        ' FROM user'
        ' WHERE id = (?)',
        (str(answer['user_id']),)
    ).fetchone()

    if g.user['id'] == question['user_id']:
        web3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
        to_address = web3.toChecksumAddress(str(answerer['eth_address']))

        data = '0xa9059cbb000000000000000000000000' + to_address[2:] + '{0:064x}'.format(question['price'])
        transaction = {
            'from': web3.toChecksumAddress(os.environ['OWNER_ADDRESS']),
            'to': web3.toChecksumAddress(os.environ['CONTRACT_ADDRESS']),
            'value': '0x0',
            'data': data
        }
        web3.personal.sendTransaction(transaction, os.environ['OWNER_ADDRESS_PASSWORD'])
    else:
        error = 'Invalid Access'
        flash(error)

    return redirect(url_for('main.answer_index', question_id=str(question_id)))

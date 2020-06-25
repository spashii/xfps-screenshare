import os
import logging
from flask import (Flask, render_template, flash,
                   redirect, url_for, request)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'extremely cryptic'

app = Flask(__name__, static_folder='temp')
app.config.from_object(Config)
# disable logging
log = logging.getLogger('werkzeug')
log.disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

timeout = 1500

class StreamForm(FlaskForm):
    session_id = StringField('session id', validators=[DataRequired(),
                                                      Length(24, 24)])
    submit = SubmitField('submit', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = StreamForm()
    if form.is_submitted():
        return redirect(url_for('stream', session_id=form.session_id.data))
    return render_template('home.html', form=form)

@app.route('/stream/<session_id>', methods=['GET', 'POST'])
def stream(session_id):
    if session_id != current_session_id:
        flash('invalid session id', category='danger') 
        return redirect(url_for('home'))
    current_img_path = os.path.join(session_id, 'current.png')
    return render_template('stream.html', current_img_path=current_img_path,
           timeout=timeout)

import random
import string

import pyscreenshot

temp_path = os.path.join(os.path.curdir, 'temp')
if not os.path.exists(temp_path):
    os.mkdir(temp_path)

def generate_session_id():
    return ''.join(random.choices(
           string.ascii_uppercase + string.digits, k=24))

def get_session_path(session_id):
    session_path = os.path.join(temp_path, session_id)
    os.mkdir(session_path)
    return session_path


def take_screenshot(session_id, session_path):
    save_path = os.path.join(session_path, 'current.png')
    if os.path.exists(save_path):
        os.rename(save_path,
                  os.path.join(session_path,
                  datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')+'.png'))
    img = pyscreenshot.grab()
    img.save(save_path, quality=65, optimize=True)

# todo graceful threading
import threading

def f(f_stop):
    take_screenshot(current_session_id, current_session_path)
    if not f_stop.is_set():
        threading.Timer(timeout/1000, f, [f_stop]).start()

f_stop = threading.Event()

if __name__ == '__main__':
    current_session_id = generate_session_id()
    current_session_path = get_session_path(current_session_id)
    print(f'\nsession id : { current_session_id }')
    f(f_stop)
    # app.run(host='0.0.0.0', port=8080)
    app.run()
    f_stop.set()

    


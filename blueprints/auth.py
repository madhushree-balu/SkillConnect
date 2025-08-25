from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, redirect
)
from handler import models, db, utils


auth = Blueprint('auth', __name__, url_prefix='/auth')

userHandler = db.UserHandler()
sessionHandler = db.SessionHandler()

@auth.get('/login')
def login():
    return render_template('auth/login.html')


@auth.post('/login')
def login_post():
    form = request.form

    username = form.get('username', "").lower()
    password = form.get('password', "-")

    user = userHandler.get_user(username=username)

    if user is None:
        flash('Username not found!', 'error')
        return redirect(url_for('auth.login'))

    if not userHandler.match_password(user.userId, password):
        flash('Incorrect password!', 'error')
        return redirect(url_for('auth.login'))

    sessionId = utils.hash_password(str(user.userId) + str(request.remote_addr))

    sessionHandler.create_session(
        models.Session(userId=user.userId, sessionId=sessionId)
    )
    session['userId'] = user.userId
    session['username'] = user.username
    session['sessionId'] = sessionId

    return redirect(url_for('index'))


@auth.get('/signup')
def signup():
    return render_template('auth/signup.html')


@auth.post('/signup')
def signup_post():
    form = request.form

    username = form.get('username')
    email = form.get('email')
    password = form.get('password')
    userType = form.get('userType')
    
    if username is None or username == "":
        flash('Username is required', 'error')
        return redirect(url_for('auth.signup'))

    if email is None or email == "":
        flash('Email is required', 'error')
        return redirect(url_for('auth.signup'))

    if password is None or password == "":
        flash('Password is required', 'error')
        return redirect(url_for('auth.signup'))

    user = models.User(
        username=username.strip().lower(),
        email=email.strip(),
        password= utils.hash_password(password)
    )

    if userHandler.get_user_id(email=email) is not None:
        flash('Email already exists', 'error')
        return redirect(url_for('auth.signup'))
    
    if userHandler.get_user_id(username=username) is not None:
        flash('Email already exists', 'error')
        return redirect(url_for('auth.signup'))

    user = userHandler.create_user(user)
    
    if not user:
        flash('Failed to create user', 'error')
        return redirect(url_for('auth.signup'))

    sessionId = utils.hash_password(str(user.userId) + str(request.remote_addr))
    sessionHandler.create_session(
        models.Session(userId=user.userId, sessionId=sessionId)
    )
    session['userId'] = user.userId
    session['username'] = user.username
    session['sessionId'] = sessionId

    return redirect(url_for('auth.login'))


@auth.get('/logout')
def logout():
    sessionHandler.delete_session(session['sessionId'])
    session.clear()
    return redirect(url_for('auth.login'))
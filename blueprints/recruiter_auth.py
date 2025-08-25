from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, redirect
)
from handler import models, db, utils


recruiter_auth = Blueprint('recruiter_auth', __name__, url_prefix='/recruiter/auth')

recruiterHandler = db.RecruiterHandler()
recruiterSessionHandler = db.RecruiterSessionHandler()

@recruiter_auth.get('/login')
def login():
    return render_template('recruiter/auth/login.html')


@recruiter_auth.post('/login')
def login_post():
    form = request.form

    email = form.get('email', "").lower()
    password = form.get('password', "-")

    recruiter = recruiterHandler.get_recruiter(email=email)

    if recruiter is None:
        flash('Email not found!', 'error')
        return redirect(url_for('recruiter_auth.login'))

    if not recruiterHandler.match_password(recruiter.recruiterId, password):
        flash('Incorrect password!', 'error')
        return redirect(url_for('recruiter_auth.login'))

    sessionId = utils.hash_password(str(recruiter.recruiterId) + str(request.remote_addr) + "recruiter")

    recruiterSessionHandler.create_session(
        models.RecruiterSession(recruiterId=recruiter.recruiterId, sessionId=sessionId)
    )
    session['recruiterId'] = recruiter.recruiterId
    session['recruiterName'] = recruiter.name
    session['recruiterEmail'] = recruiter.email
    session['recruiterSessionId'] = sessionId

    return redirect(url_for('recruiter_dashboard'))


@recruiter_auth.get('/signup')
def signup():
    return render_template('recruiter/auth/signup.html')


@recruiter_auth.post('/signup')
def signup_post():
    form = request.form

    name = form.get('name')
    email = form.get('email')
    password = form.get('password')
    company = form.get('company', '')
    location = form.get('location', '')
    website = form.get('website', '')
    contact_email = form.get('contact_email', '')
    contact_number = form.get('contact_number', '')
    
    if name is None or name == "":
        flash('Name is required', 'error')
        return redirect(url_for('recruiter_auth.signup'))

    if email is None or email == "":
        flash('Email is required', 'error')
        return redirect(url_for('recruiter_auth.signup'))

    if password is None or password == "":
        flash('Password is required', 'error')
        return redirect(url_for('recruiter_auth.signup'))

    recruiter = models.Recruiter(
        name=name.strip(),
        email=email.strip().lower(),
        password=utils.hash_password(password),
        company=company.strip() if company else '',
        location=location.strip() if location else '',
        website=website.strip() if website else '',
        contact_email=contact_email.strip() if contact_email else '',
        contact_number=contact_number.strip() if contact_number else ''
    )

    if recruiterHandler.get_recruiter_id(email) is not None:
        flash('Email already exists', 'error')
        return redirect(url_for('recruiter_auth.signup'))

    recruiter = recruiterHandler.create_recruiter(recruiter)
    
    if not recruiter:
        flash('Failed to create recruiter account', 'error')
        return redirect(url_for('recruiter_auth.signup'))

    flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('recruiter_auth.login'))


@recruiter_auth.get('/logout')
def logout():
    if 'recruiterSessionId' in session:
        recruiterSessionHandler.delete_session(session['recruiterSessionId'])
    session.clear()
    return redirect(url_for('recruiter_auth.login'))


# Decorator to require recruiter authentication
def recruiter_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'recruiterId' not in session or 'recruiterSessionId' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('recruiter_auth.login'))
        
        # Verify session exists in database
        recruiter_session = recruiterSessionHandler.get_session(session['recruiterSessionId'])
        if not recruiter_session or recruiter_session.recruiterId != session['recruiterId']:
            session.clear()
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('recruiter_auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function
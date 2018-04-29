from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import User, Request, Client
from app.forms import LoginForm, RequestForm
from werkzeug.urls import url_parse
from sqlalchemy import exc

@app.route('/')
@app.route('/index')
@login_required
def index():
    requests = Request.query.filter_by(author=current_user).all()
    form = RequestForm()
    return render_template('index.html', title='Home', requests=requests, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        flash('Logged in user {}'.format(form.username.data))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/req', methods=['GET'])
@login_required
def req_get():
    requests = Request.query.filter_by(author=current_user).all()
    return jsonify([ request.as_dict() for request in requests])

@app.route('/req', methods=['POST'])
@login_required
def req_post():
    form = RequestForm()
    if form.validate_on_submit():
        success = Request.query.filter(Request.client == Client(form.client.data), 
            Request.priority == form.priority.data).update({'title': form.title.data, 
            'description': form.description.data, 'client': form.client.data, 
            'priority': form.priority.data, 'target_date': form.target_date.data, 
            'product_area': form.product_area.data})
        if not success:
            request = Request(title=form.title.data, description=form.description.data, 
                client=form.client.data, priority=form.priority.data, 
                target_date=form.target_date.data, product_area=form.product_area.data,
                author=current_user)
            db.session.add(request)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            Request.query.filter(Request.client == Client(form.client.data), 
                Request.priority >= form.priority.data).update({'priority': Request.priority + 1})
            db.session.add(request)
            db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify(form.errors)
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import User, Request
from app.forms import LoginForm, RequestForm
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    requests = Request.query.filter_by(author=current_user).all()
    return render_template('index.html', title='Home', requests=requests)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        flash('Logged in user {}'.format(form.username.data))
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
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

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RequestForm()
    if form.validate_on_submit():
        request = Request(title=form.title.data, description=form.description.data, 
            client=form.client.data, priority=form.priority.data, 
            target_date=form.target_date.data, product_area=form.product_area.data,
            author=current_user)
        db.session.add(request)
        db.session.commit()
        flash('Your request has been added')
        return redirect(url_for('index'))
    return render_template('create.html', title='Create Request', form=form)


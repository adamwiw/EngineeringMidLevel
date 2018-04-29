from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Request, Client
from app.main.forms import LoginForm, RequestForm, RegistrationForm
from werkzeug.urls import url_parse
from sqlalchemy import exc
from app.main import bp
    
def update_priority(client, priority):
    request = Request.query.filter((Request.client == client) & 
        (Request.priority == priority)).first()
    if request is not None:
        update_priority(request.client, request.priority + 1)
        request.priority += 1
        
@bp.route('/')
@bp.route('/index')
@login_required
def index():
    requests = Request.query.filter_by(author=current_user).all()
    form = RequestForm()
    return render_template('index.html', title='Home', requests=requests, form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        flash('Logged in user {}'.format(form.username.data))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    
@bp.route('/req', methods=['GET'])
@login_required
def req_get():
    requests = Request.query.filter_by(author=current_user).all()
    return jsonify([ request.as_dict() for request in requests])

@bp.route('/req', methods=['POST'])
@login_required
def req_post():
    form = RequestForm()
    if form.validate_on_submit():
        update_priority(form.client.data, form.priority.data)
        request = Request.query.filter_by(id=form.id.data).first()
        if request is not None:
            request.title = form.title.data
            request.description = form.description.data
            request.client = form.client.data
            request.priority = form.priority.data
            request.target_date = form.target_date.data
            request.product_area = form.product_area.data
        else:
            request = Request(title=form.title.data, description=form.description.data, 
                client=form.client.data, priority=form.priority.data, 
                target_date=form.target_date.data, product_area=form.product_area.data,
                author=current_user)
            db.session.add(request)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify(form.errors)
        
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

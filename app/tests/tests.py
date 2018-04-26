import unittest
import flask_testing
from flask import Flask, Response
from flask_testing import TestCase, LiveServerTestCase
from app import app, db
from datetime import datetime
import os
from urllib.request import urlopen
from app.models import User, Request, Area, Client
from app.config import TestConfig
from sqlalchemy import exc
from bs4 import BeautifulSoup
import random
import string

class ServerTest(LiveServerTestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        app.config['LIVESERVER_PORT'] = 0
        app.config['TESTING'] = True
        return app

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)
        
class BaseTest(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        app.config['TESTING'] = True
        return app
        
    def setUp(self):
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
        user = User(username='test', email='test@example.com')
        user.set_password('asd')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
class LoggedInTest(BaseTest):
    def setUp(self):
        super(LoggedInTest, self).setUp()
        response = self.client.get('/login')
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf = soup.find('input', {'id' : 'csrf_token'}).get('value')
        data = dict(
            csrf_token=csrf,
            username='test',
            password='asd'
        )
        self.client.post('/login?next=%2F', data=data, follow_redirects=True)
        
class UserTest(BaseTest):
    def test_user(self):
        user = user = User.query.filter_by(username='test').first()
        assert user in db.session

    def test_duplicate_username(self):
        user = User(username='test', email='a@example.com')
        db.session.add(user)
        try:
            db.session.commit()
        except exc.IntegrityError:
            assert user not in db.session
        
    def test_duplicate_email(self):
        user = User(username='test2', email='test@example.com')
        db.session.add(user)
        try:
            db.session.commit()
        except exc.IntegrityError:
            assert user not in db.session
        
    def test_user_password(self):
        user = User.query.filter_by(username='test').first()
        assert user.check_password('asd')

class RequestTest(BaseTest):
    def test_request(self):
        user = User.query.filter_by(username='test').first()
        request = Request(title="title", description="description", 
            client=Client.CLIENT_A, priority=0,
            target_date=datetime.now(), product_area=Area.BILLING,
            author=user)
        db.session.add(request)
        db.session.commit()
        assert request in db.session
                
    def test_duplicate_request(self):
        user = User.query.filter_by(username='test').first()
        request = Request(title="title", description="description", 
            client=Client.CLIENT_A, priority=0,
            target_date=datetime.now(), product_area=Area.BILLING,
            author=user)
        db.session.add(request)
        db.session.commit()
        db.session.add(request)
        try:
            db.session.commit()
        except exc.IntegrityError:
            assert request not in db.session

class TestLogin(BaseTest):
    def test_log_in_template(self):
        self.client.get('/login')
        self.assert_template_used('login.html')
        
    def test_index_not_logged_in(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=%2F')
        
    def test_log_in_unsuccessful(self):
        response = self.client.get('/login')
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf = soup.find('input', {'id' : 'csrf_token'}).get('value')
        data = dict(
            csrf_token=csrf,
            username='test',
            password='asdf'
        )
        response = self.client.post('/login?next=%2F', data=data, follow_redirects=True)
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=%2F')
        
    def test_log_in_no_csrf(self):
        data = dict(
            username='test',
            password='asd'
        )
        response = self.client.post('/login?next=%2F', data=data, follow_redirects=True)
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=%2F')
        
class TestViews(LoggedInTest):
    def test_log_in_successful(self):
        response = self.client.get('/login')
        self.assertRedirects(response, '/index')
        
    def test_index_template_used(self):
        self.client.get('/')
        self.assert_template_used('index.html')
        
    def test_create_template_used(self):
        self.client.get('/create')
        self.assert_template_used('create.html')
        
    def test_create_request(self):
        response = self.client.get('/create')
        soup = BeautifulSoup(response.data, 'html.parser')
        csrf = soup.find('input', {'id' : 'csrf_token'}).get('value')
        title = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        data = dict(
            csrf_token=csrf,
            title=title,
            description='test',
            client='Client A',
            priority='1',
            target_date=datetime.now().strftime('%Y-%m-%d'),
            product_area='Billing'
        )
        response = self.client.post('/create', data=data, follow_redirects=True)
        assert Request.query.filter_by(title=title).first() is not None
        
    def test_log_out(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, '/index')
        
if __name__ == '__main__':
    unittest.main()
    

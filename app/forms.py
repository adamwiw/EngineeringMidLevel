from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Request, Client, Area
from flask.ext.admin.form.widgets import DatePickerWidget

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RequestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    client = SelectField('Client', choices = Client.choices(), 
        coerce = Client.coerce, validators=[DataRequired()])
    priority = IntegerField('Priority', validators=[DataRequired()])
    target_date = DateField('Target Date', format='%Y-%m-%d', widget=DatePickerWidget())
    product_area = SelectField('Product Area', choices = Area.choices(), 
        coerce = Area.coerce, validators=[DataRequired()])
    submit = SubmitField('Submit')

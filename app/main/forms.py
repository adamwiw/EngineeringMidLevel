from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DateField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Request, Client, Area

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RequestForm(FlaskForm):
    id = HiddenField()
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    client = SelectField('Client', choices = Client.choices(), 
        coerce = Client.coerce, validators=[DataRequired()])
    priority = IntegerField('Priority', validators=[DataRequired()])
    target_date = DateField('Target Date', format='%Y-%m-%d', 
        validators=[DataRequired()])
    product_area = SelectField('Product Area', choices = Area.choices(), 
        coerce = Area.coerce, validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField

class SignUp(FlaskForm):
    """Forms for user to register for an account"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("EmailField", validators=[InputRequired()])
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])


class Login(FlaskForm):
    """Form for user to login, provided the correct username and password"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class AddFeedback(FlaskForm):

    title=StringField("Title", validators=[InputRequired()])
    content=StringField("Content", validators=[InputRequired()])
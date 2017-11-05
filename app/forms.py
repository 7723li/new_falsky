from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('emain', validators=[DataRequired(), Email()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(FlaskForm) :
	email = StringField('emain', validators=[DataRequired(), Email()])
	nickname = StringField('nickname', validators=[DataRequired()])
	confirm = SubmitField('confirm')

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

class PostForm(FlaskForm):
    post = TextAreaField('post', validators=[DataRequired()])    

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
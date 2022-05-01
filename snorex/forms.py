# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email',
                validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email',
                validators=[DataRequired(), Email(),
                    EqualTo('email_confirmation',
                        message='Emails must match!')])
    email_confirmation = StringField('Confirm Email',
                validators=[DataRequired(), Email()])
    username = StringField('Username',
                validators=[DataRequired()])
    password = PasswordField('Password',
                validators=[DataRequired(),
                    EqualTo('password_confirmation',
                        message='Passwords must match!')])
    password_confirmation = PasswordField('Confirm Password',
                validators=[DataRequired()])

    submit = SubmitField('Register')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has already been registered!')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken!')

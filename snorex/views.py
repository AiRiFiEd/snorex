# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""
from flask import render_template, redirect, request, url_for, flash, abort, Blueprint
from flask_login import login_user, login_required, logout_user

from snorex import db
from snorex.models import User
from snorex.forms import RegistrationForm, LoginForm

main_blueprints = Blueprint('main', __name__)

@main_blueprints.route('/')
def home():
    return render_template('home.html')

@main_blueprints.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

@main_blueprints.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!')
    return redirect(url_for('main.login'))

@main_blueprints.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash('Logged in successfully!')

            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('main.welcome')

            return redirect(next)
    return render_template('login.html', form=form)

@main_blueprints.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration completed!')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

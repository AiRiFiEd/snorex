# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, SelectField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, NumberRange

class DataRequestForm(FlaskForm):
    underlying = StringField('Underlying',
                    validators=[DataRequired()])
    resolution = SelectField(u'Resolution',
                    default=86400,
                    choices=[(15, '15 seconds'),
                                (60, '1 minute'),
                                (300, '5 minutes'),
                                (900, '15 minutes'),
                                (3600, '1 hour'),
                                (14400, '4 hours'),
                                (86400, '1 day'),
                                (5*86400, '5 days'),
                                (7*86400, '7 days'),
                                (20*86400, '20 days'),
                                (30*86400, '30 days')])
    rolling_window_1 = IntegerField('Window 1',
                        default=30,
                        validators=[DataRequired(),
                                    NumberRange()])
    rolling_window_2 = IntegerField('Window 2',
                        default=90,
                        validators=[DataRequired(),
                                    NumberRange()])
    rolling_window_3 = IntegerField('Window 3',
                        default=180,
                        validators=[DataRequired(),
                                    NumberRange()])
    start_date = DateField('Start Date',
                    validators=[DataRequired()],
                    format='%Y-%m-%d')
    end_date = DateField('End Date',
                    validators=[DataRequired()],
                    format='%Y-%m-%d')
    submit = SubmitField('Submit')

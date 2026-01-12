# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[DataRequired(message='用户名不能为空'), Length(3, 64, message='用户名长度需在3-64位之间')]
    )
    password = PasswordField(
        '密码',
        validators=[DataRequired(message='密码不能为空'), Length(6, 128, message='密码长度需在6-128位之间')]
    )
    submit = SubmitField('立即登录')
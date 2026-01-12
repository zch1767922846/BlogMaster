from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email, ValidationError,Optional

from app.models.user import User


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    nickname = StringField('Nickname', validators=[DataRequired(), Length(min=2, max=30)])
    # 密码字段设置为可选，不修改时可以为空
    password = PasswordField('Password', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    status = IntegerField('Status', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    nickname = StringField('用户昵称', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 128)])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 16)])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(),
        Length(6, 16),
        EqualTo('password', message='密码和确认密码不匹配')
    ])
    submit = SubmitField('注册')

# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models.tag import Tag


class TagForm(FlaskForm):
    name = StringField('标签名', validators=[
        DataRequired(message='标签名不能为空'),
        Length(min=1, max=32, message='标签名长度为1-32位')
    ])
    submit = SubmitField('提交')

    def validate_name(self, field):
        if Tag.query.filter_by(name=field.data).first():
            raise ValidationError('该标签已存在')
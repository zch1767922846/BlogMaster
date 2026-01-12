# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(1, 64)])
    slug = StringField('分类别名', validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField('分类描述', validators=[Length(0, 200)])
    submit = SubmitField('提交')
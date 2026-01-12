from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField, TextAreaField, RadioField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

from app.models.post import Category


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 64)])
    slug = StringField('别名', validators=[DataRequired(), Length(1, 64)])
    excerpt = TextAreaField('摘要', validators=[Optional()])
    content = TextAreaField('内容', validators=[DataRequired()])
    categoryid = SelectField('分类', coerce=int)
    # 多媒体文件上传
    media_files = FileField('上传多媒体文件', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'zip', 'rar', '7z', 'tar', 'gz', 'bz2'], '只支持图片、文档、视频、音频和压缩包格式!')
    ])
    # 移除状态字段的表单显示，由按钮控制
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.categoryid.choices = [(category.id, category.name)
                                   for category in Category.query.order_by(Category.name).all()]
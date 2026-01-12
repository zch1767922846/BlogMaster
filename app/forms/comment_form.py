from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    content = TextAreaField('内容', validators=[DataRequired(message='内容不能为空')])
    status = RadioField('状态', choices=[(True, '启用'), (False, '禁用')], default=True, validators=[DataRequired()])
    # 多媒体文件上传
    media_files = FileField('上传多媒体文件', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'zip', 'rar', '7z', 'tar', 'gz', 'bz2'], '只支持图片、文档、视频、音频和压缩包格式!')
    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
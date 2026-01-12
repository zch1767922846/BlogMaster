import os
import enum
from datetime import datetime

from app import db


class MediaType(enum.Enum):
    image = 'image'
    document = 'document'
    video = 'video'
    audio = 'audio'
    archive = 'archive'


class Media(db.Model):
    __tablename__ = 't_media'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    filepath = db.Column(db.String(500), nullable=False, comment='存储路径')
    file_type = db.Column(db.Enum(MediaType), nullable=False, comment='文件类型')
    file_size = db.Column(db.Integer, comment='文件大小(字节)')
    mime_type = db.Column(db.String(100), comment='MIME类型')
    upload_time = db.Column(db.DateTime, server_default=db.func.now(), comment='上传时间')
    uploader_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), comment='上传者ID')
    description = db.Column(db.Text, comment='文件描述')
    
    # 关联关系
    post_medias = db.relationship('PostMedia', backref=db.backref('media', overlaps='medias,post_medias'), lazy='dynamic')
    comment_medias = db.relationship('CommentMedia', backref=db.backref('media', overlaps='medias,comment_medias'), lazy='dynamic')
    
    def __repr__(self):
        return f'<Media {self.filename}>'
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        return os.path.splitext(self.filename)[1].lower()
    
    @property
    def is_image(self):
        """判断是否为图片"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return self.file_extension in image_extensions
    
    @property
    def is_video(self):
        """判断是否为视频"""
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
        return self.file_extension in video_extensions
    
    @property
    def is_audio(self):
        """判断是否为音频"""
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        return self.file_extension in audio_extensions
    
    @property
    def is_document(self):
        """判断是否为文档"""
        document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        return self.file_extension in document_extensions
    
    @property
    def is_archive(self):
        """判断是否为压缩包"""
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
        return self.file_extension in archive_extensions


class PostMedia(db.Model):
    """文章与媒体文件的关联表"""
    __tablename__ = 't_post_media'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('t_post.id'), nullable=False, comment='文章ID')
    media_id = db.Column(db.Integer, db.ForeignKey('t_media.id'), nullable=False, comment='媒体文件ID')
    upload_time = db.Column(db.DateTime, server_default=db.func.now(), comment='关联时间')


class CommentMedia(db.Model):
    """评论与媒体文件的关联表"""
    __tablename__ = 't_comment_media'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('t_comment.id'), nullable=False, comment='评论ID')
    media_id = db.Column(db.Integer, db.ForeignKey('t_media.id'), nullable=False, comment='媒体文件ID')
    upload_time = db.Column(db.DateTime, server_default=db.func.now(), comment='关联时间')
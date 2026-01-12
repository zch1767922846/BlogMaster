import os
import uuid
from datetime import datetime

from flask import request, current_app, jsonify, url_for
from werkzeug.utils import secure_filename

from app import db
from app.models.media import Media, MediaType, PostMedia, CommentMedia
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.utils import query_to_dict


# 文件类型配置
ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'},
    'audio': {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'},
    'archive': {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}
}

UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return True
    return False


def get_file_type(filename):
    """根据文件扩展名确定文件类型"""
    if '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None


def upload_media():
    """上传媒体文件的通用函数"""
    f = request.files.get('file') or request.files.get('upload')
    
    if not f or not f.filename:
        return jsonify(code=ResponseCode.FILE_UPLOAD_FAILED, message='No file selected!')
    
    # 验证文件类型
    if not allowed_file(f.filename):
        return jsonify(code=ResponseCode.FILE_UPLOAD_FAILED, message='File type not allowed!')
    
    # 验证文件大小
    f.seek(0, os.SEEK_END)  # 移动到文件末尾
    file_size = f.tell()  # 获取当前位置（文件大小）
    f.seek(0)  # 重置到文件开头
    
    if file_size > MAX_FILE_SIZE:
        return jsonify(code=ResponseCode.FILE_UPLOAD_FAILED, message='File too large! Maximum size is 50MB')
    
    # 安全处理文件名
    filename = secure_filename(f.filename)
    
    # 创建上传目录
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(upload_path, unique_filename)
    
    # 保存文件
    f.save(file_path)
    
    # 获取文件类型
    file_type = get_file_type(f.filename)
    media_type = MediaType[file_type] if file_type else MediaType.document
    
    # 创建媒体记录
    media = Media(
        filename=filename,
        filepath=os.path.join(UPLOAD_FOLDER, unique_filename),
        file_type=media_type,
        file_size=file_size,
        mime_type=f.content_type
    )
    
    # 如果用户已登录，记录上传者
    from flask_login import current_user
    if current_user.is_authenticated:
        media.uploader_id = current_user.id
    
    db.session.add(media)
    db.session.commit()
    
    # 生成访问URL
    file_url = url_for('bp_admin.uploaded_files', filename=unique_filename)
    
    return jsonify({
        'code': ResponseCode.SUCCESS,
        'message': ResponseMessage.SUCCESS,
        'data': {
            'id': media.id,
            'filename': media.filename,
            'url': file_url,
            'file_type': media.file_type.value,
            'file_size': media.file_size,
            'is_image': media.is_image,
            'is_video': media.is_video,
            'is_audio': media.is_audio,
            'is_document': media.is_document,
            'is_archive': media.is_archive
        }
    })


def get_media_by_id(media_id):
    """根据ID获取媒体文件信息"""
    media = Media.query.get_or_404(media_id)
    return jsonify({
        'code': ResponseCode.SUCCESS,
        'message': ResponseMessage.SUCCESS,
        'data': {
            'id': media.id,
            'filename': media.filename,
            'url': url_for('bp_admin.uploaded_files', filename=os.path.basename(media.filepath)),
            'file_type': media.file_type.value,
            'file_size': media.file_size,
            'upload_time': media.upload_time.isoformat() if media.upload_time else None,
            'is_image': media.is_image,
            'is_video': media.is_video,
            'is_audio': media.is_audio,
            'is_document': media.is_document,
            'is_archive': media.is_archive
        }
    })
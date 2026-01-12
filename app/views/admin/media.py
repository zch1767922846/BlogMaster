import os
import uuid
from datetime import datetime

from flask import send_from_directory, request, url_for, render_template, current_app, jsonify
from flask_ckeditor import upload_fail, upload_success
from werkzeug.utils import secure_filename

from app import db
from app.views.admin import bp_admin
from app.models.media import Media, MediaType

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


@bp_admin.route('/media/picture/list')
def admin_media_picture_view():
    return render_template('admin/media/picture.html')


@bp_admin.route('/media/video/list')
def admin_media_video_view():
    return render_template('admin/media/video.html')


@bp_admin.route('/media/document/list')
def admin_media_document_view():
    return render_template('admin/media/document.html')


@bp_admin.route('admin/pictures')
def get_pictures():
    pass


@bp_admin.route('admin/videos')
def get_videos():
    pass


@bp_admin.route('admin/documents')
def get_documents():
    pass


@bp_admin.route('/media/files/<path:filename>')
def uploaded_files(filename):
    # 如果filename包含路径信息，只取文件名部分
    import os
    path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    # 确保filename是安全的，防止路径遍历攻击
    filename = os.path.basename(filename)
    return send_from_directory(path, filename)


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


@bp_admin.route('/media/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    if not f or not f.filename:
        return upload_fail(message='No file selected!')
    
    # 验证文件类型
    if not allowed_file(f.filename):
        return upload_fail(message='File type not allowed!')
    
    # 验证文件大小
    # 为了检查大小，我们需要临时读取文件
    f.seek(0, os.SEEK_END)  # 移动到文件末尾
    file_size = f.tell()  # 获取当前位置（文件大小）
    f.seek(0)  # 重置到文件开头
    
    if file_size > MAX_FILE_SIZE:
        return upload_fail(message='File too large! Maximum size is 50MB')
    
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
    url = url_for('bp_admin.uploaded_files', filename=unique_filename)
    return upload_success(url=url)

# def gen_rnd_filename():
#     filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#     return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))
#
#
# @bp_admin.route('/upload/', methods=['POST'])
# def ckupload():
#     """CKEditor file upload"""
#     error = ''
#     url = ''
#     callback = request.args.get("CKEditorFuncNum")
#     if request.method == 'POST' and 'upload' in request.files:
#         fileobj = request.files['upload']
#         fname, fext = os.path.splitext(fileobj.filename)
#         rnd_name = '%s%s' % (gen_rnd_filename(), fext)
#         filepath = os.path.join(app.static_folder, 'upload', rnd_name)
#         # 检查路径是否存在，不存在则创建
#         dirname = os.path.dirname(filepath)
#         if not os.path.exists(dirname):
#             try:
#                 os.makedirs(dirname)
#             except:
#                 error = 'ERROR_CREATE_DIR'
#         elif not os.access(dirname, os.W_OK):
#             error = 'ERROR_DIR_NOT_WRITEABLE'
#         if not error:
#             fileobj.save(filepath)
#             url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
#     else:
#         error = 'post error'
#     res = """<script type="text/javascript">
#   window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
# </script>""" % (callback, url, error)
#     response = make_response(res)
#     response.headers["Content-Type"] = "text/html"
#     return response

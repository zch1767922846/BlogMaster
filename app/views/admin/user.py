from flask import flash, redirect, url_for, render_template, current_app, jsonify, request
from flask_login import login_user, login_required, logout_user, current_user

import os
import uuid

from flask import send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename

from app import db
from app.errors.errorcode import ResponseCode
from app.models.user import User
from app.views.admin import bp_admin
from app import login_manager
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.forms.user_form import LoginForm, RegisterForm, UserForm
from app.models.user import User
from app.utils import query_to_dict
from app.views.admin import bp_admin


@bp_admin.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = get_user_info(register_form)
        if User.query.filter_by(username=user.username).count() > 0:
            flash('Username has exist.', 'failed')
            current_app.logger.debug("%s has exist.", user.username)
            return render_template('admin/register.html', register_form=register_form)
        elif User.query.filter_by(email=user.email).count() > 0:
            flash('Email has exist.', 'failed')
            current_app.logger.debug("%s has exist.", user.email)
            return render_template('admin/register.html', register_form=register_form)
        else:
            db.session.add(user)
            db.session.commit()
            flash('register success!')
            current_app.logger.debug("register success.")
            return redirect(url_for('bp_admin.index'))

    return render_template('admin/register.html', register_form=register_form)


@bp_admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            current_app.logger.debug("Login success.")
            return redirect(url_for('bp_admin.index'))
        else:
            current_app.logger.debug("Login failed.")
            return redirect(url_for('bp_admin.login'))
    return render_template('admin/login.html', login_form=login_form)


@bp_admin.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()  # 登出用户
    current_app.logger.debug("Logout.")
    return redirect(url_for('bp_blog.index'))  # 重定向回首页


@bp_admin.route('/user/list', methods=['GET'])
def admin_users_view():
    """用户列表页面（查看所有用户）"""
    return render_template('admin/user/user-list.html')  # 不传递表单，避免与添加页冲突


@bp_admin.route('/user', methods=['GET', 'POST'])
def create_user():
    user_form = UserForm()
    if user_form.validate_on_submit():
        user = get_user_info(user_form)
        # 设置用户状态
        user.status = user_form.status.data

        db.session.add(user)
        db.session.commit()
        flash('用户创建成功', 'success')
        return redirect(url_for('bp_admin.admin_users_view'))
    return render_template('admin/user/user.html', user_form=user_form)


@bp_admin.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.with_entities(
            User.id,
            User.username,
            User.nickname,
            User.email,
            User.registertime,
            User.status
        ).all()

        user_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email,
                'registertime': user.registertime.isoformat() if user.registertime else None,
                'status': bool(user.status)
            }
            user_list.append(user_dict)

        return jsonify({
            "code": ResponseCode.SUCCESS,
            "message": ResponseMessage.SUCCESS,
            "data": user_list,
            "count": len(user_list)
        })

    except Exception as e:
        current_app.logger.error(f"查询用户失败: {str(e)}", exc_info=True)
        return jsonify(
            code=ResponseCode.QUERY_DB_FAILED,
            message=f"{ResponseMessage.QUERY_DB_FAILED}: {str(e)}",
            data=[],
            count=0
        )


@bp_admin.route('/user/<string:username>', methods=['GET'])
def get_user_by_name(username):
    try:
        user = User.query.with_entities(
            User.id,
            User.username,
            User.nickname,
            User.email,
            User.registertime,
            User.status
        ).filter(User.username == username).first()
    except Exception as e:
        current_app.logger.error(f"查询用户失败: {str(e)}")
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)

    if user is None:
        return jsonify(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

    data = dict(
        code=ResponseCode.SUCCESS,
        message=ResponseMessage.SUCCESS,
        data=query_to_dict(user)
    )
    current_app.logger.debug("data: %s", data)
    return jsonify(data)


@bp_admin.route('/user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(f"查询用户失败: {str(e)}")
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)

    if user is None:
        return jsonify(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

    # 获取表单数据
    username = request.form.get('username')
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    status = request.form.get('status')
    password = request.form.get('password')

    # 更新用户信息
    user.username = username
    user.nickname = nickname
    user.email = email
    user.status = int(status)

    # 只有当密码不为空时才更新密码
    if password and password.strip():
        user.password = password

    db.session.commit()

    # 检查是否是AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(code=ResponseCode.UPDATE_USER_SUCCESS, message=ResponseMessage.UPDATE_USER_SUCCESS)
    else:
        flash('用户更新成功', 'success')
        return jsonify({
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": query_to_dict(user)
            })


@bp_admin.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(f"查询用户失败: {str(e)}")
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)

    if user is None:
        return jsonify(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

    db.session.delete(user)
    db.session.commit()
    return jsonify(code=ResponseCode.DELETE_USER_SUCCESS, message=ResponseMessage.DELETE_USER_SUCCESS)


def get_user_info(form):
    username = form.username.data
    nickname = form.nickname.data
    password = form.password.data
    email = form.email.data
    user = User(
        username=username,
        nickname=nickname,
        password=password,
        email=email,
    )
    return user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@bp_admin.route('/user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(f"查询用户失败: {str(e)}")
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)

    if user is None:
        return jsonify(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

    user_form = UserForm()
    user_form.username.data = user.username
    user_form.nickname.data = user.nickname
    user_form.email.data = user.email
    user_form.status.data = user.status
    return render_template('admin/user/user-edit.html', user_form=user_form, user_id=user_id)


@bp_admin.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = current_user
    if request.method == 'POST':
        # 更新基本资料
        user.nickname = request.form.get('nickname')
        user.email = request.form.get('email')
        
        db.session.commit()
        flash('基本资料更新成功', 'success')
        return redirect(url_for('bp_admin.user_profile'))
    
    return render_template('admin/user/profile.html', user=user)


@bp_admin.route('/user/security', methods=['GET', 'POST'])
@login_required
def user_security():
    user = current_user
    if request.method == 'POST':
        # 更新安全设置
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证原密码
        if not user.check_password(old_password):
            flash('原密码错误', 'error')
            return render_template('admin/user/security.html', user=user)
        
        # 验证新密码确认
        if new_password != confirm_password:
            flash('新密码与确认密码不一致', 'error')
            return render_template('admin/user/security.html', user=user)
        
        # 更新密码
        user.password = new_password
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('bp_admin.user_security'))
    
    return render_template('admin/user/security.html', user=user)


# 文件类型配置
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
UPLOAD_FOLDER = 'uploads/avatars'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@bp_admin.route('/upload/avatar', methods=['POST'])
@login_required
def upload_avatar():
    user = current_user
    
    if 'file' not in request.files:
        return jsonify({'code': 1, 'msg': '没有选择文件'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'code': 1, 'msg': '没有选择文件'})
    
    if file and allowed_file(file.filename):
        # 验证文件大小
        file.seek(0, os.SEEK_END)  # 移动到文件末尾
        file_size = file.tell()  # 获取文件大小
        file.seek(0)  # 重置到文件开头
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'code': 1, 'msg': '文件太大，最大支持5MB'})
        
        # 创建上传目录
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_path, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 删除旧头像文件
        if user.avatar:
            old_avatar_path = os.path.join(current_app.root_path, user.avatar)
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)
        
        # 更新用户头像路径
        user.avatar = f"{UPLOAD_FOLDER}{unique_filename}"
        db.session.commit()
        
        # 返回成功响应
        avatar_url = url_for('static', filename=f"{UPLOAD_FOLDER}{unique_filename}")
        return jsonify({'code': 0, 'msg': '上传成功', 'data': {'src': avatar_url}})
    else:
        return jsonify({'code': 1, 'msg': '不支持的文件类型'})


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
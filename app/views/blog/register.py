from flask import render_template, request, redirect, url_for, flash, current_app
from app.forms.user_form import RegisterForm
from app.models.user import User
from app import db
# 从 __init__.py 导入 bp_blog 蓝图
from app.views.blog import bp_blog

@bp_blog.route('/register', methods=['GET', 'POST'])  # 添加POST方法支持
def blog_register():
    register_form = RegisterForm()
    # 如果是POST请求并且表单验证通过
    if request.method == 'POST' and register_form.validate_on_submit():
        # 检查用户名是否已存在
        if User.query.filter_by(username=register_form.username.data).first():
            flash('用户名已存在', 'danger')
            return render_template('blog/register.html', register_form=register_form)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=register_form.email.data).first():
            flash('邮箱已被注册', 'danger')
            return render_template('blog/register.html', register_form=register_form)

        # 创建新用户
        new_user = User(
            username=register_form.username.data,
            nickname=register_form.nickname.data,
            password=register_form.password.data,
            email=register_form.email.data
        )

        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        current_app.logger.debug("User registered successfully: %s", new_user.username)
        return redirect(url_for('bp_blog.login'))  # 先跳转到登录页

    # GET请求或者表单验证失败时，返回注册页面
    return render_template('blog/register.html', register_form=register_form)
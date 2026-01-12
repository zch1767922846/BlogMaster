# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user
from app import db
from app.forms.login_form import LoginForm
from app.models.user import User
# 从 __init__.py 导入 bp_blog 蓝图
from app.views.blog import bp_blog

@bp_blog.route('/login', methods=['GET', 'POST'])
def login():
    # 若已登录，直接跳转（避免重复登录）
    if current_user.is_authenticated:
        if current_user.is_admin_user:
            return redirect(url_for('bp_admin.index'))
        else:
            # 修复路由端点名称，应该是 bp_blog.user_home 而不是 bp_blog.home
            return redirect(url_for('bp_blog.user_home'))

    form = LoginForm()
    if form.validate_on_submit():
        # 查询用户
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('bp_blog.login'))

        # 登录用户（remember=True可添加"记住我"功能，此处简化）
        login_user(user, remember=True)

        # 处理跳转（区分admin和普通用户）
        if user.is_admin_user:
            flash('管理员登录成功', 'success')
            return redirect(url_for('bp_admin.index'))  # admin跳转到/admin/
        else:
            flash('登录成功', 'success')
            # 修复路由端点名称，应该是 bp_blog.user_home 而不是 bp_blog.home
            return redirect(url_for('bp_blog.user_home'))  # 普通用户跳转到已登录首页

    return render_template('blog/login.html', form=form)
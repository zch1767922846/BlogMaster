from flask import render_template, redirect, url_for, flash
from app.models.user import User
from app.models.post import Post
from app.models.page import Page
from app.models.comment import Comment
from app.views.admin import bp_admin
from flask_login import login_required, current_user


@bp_admin.route('/')
# @login_required()
def index():
    # 检查用户是否已认证并且是管理员
    if not hasattr(current_user, 'is_admin_user') or not current_user.is_admin_user:
        flash('您没有管理员权限', 'danger')
        return redirect(url_for('bp_blog.user_home'))
    return render_template('admin/index.html', user=current_user)


@bp_admin.route('/dashboard')
def dashboard():
    # 获取统计数据
    user_count = User.query.count()
    post_count = Post.query.count()
    page_count = Page.query.count()
    comment_count = Comment.query.count()

    # 获取最近5个用户（修复查询方式并限制数量）
    recent_users = User.query.order_by(User.registertime.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        user_count=user_count,
        post_count=post_count,
        page_count=page_count,
        comment_count=comment_count,
        recent_users=recent_users
    )
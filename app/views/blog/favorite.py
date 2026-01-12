from flask import jsonify, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app import db
from app.models.post import Post
from app.views.blog import bp_blog


@bp_blog.route('/post/<int:post_id>/favorite', methods=['POST'])
@login_required
def favorite_post(post_id):
    """收藏文章"""
    post = Post.query.get_or_404(post_id)
    
    # 检查文章是否已收藏
    if current_user.has_favorited(post):
        flash('您已经收藏过这篇文章了', 'info')
    else:
        current_user.favorite_post(post)
        db.session.commit()
        flash('文章收藏成功', 'success')
        
    # 重定向回文章详情页
    return redirect(url_for('bp_blog.post_detail', slug=post.slug))


@bp_blog.route('/post/<int:post_id>/unfavorite', methods=['POST'])
@login_required
def unfavorite_post(post_id):
    """取消收藏文章"""
    post = Post.query.get_or_404(post_id)
    
    # 检查文章是否已收藏
    if not current_user.has_favorited(post):
        flash('您还没有收藏这篇文章', 'info')
    else:
        current_user.unfavorite_post(post)
        db.session.commit()
        flash('已取消收藏', 'success')
        
    # 重定向回文章详情页
    return redirect(url_for('bp_blog.post_detail', slug=post.slug))


@bp_blog.route('/user/favorites')
@login_required
def user_favorites():
    """用户收藏的文章列表"""
    # 获取当前用户收藏的文章
    from app.models.favorite import Favorite
    favorites = Favorite.query.filter_by(user_id=current_user.id)\
                              .order_by(Favorite.created_at.desc())\
                              .all()
    
    # 提取文章对象
    posts = [fav.post for fav in favorites]
    
    return render_template('blog/user_favorites.html', posts=posts)

from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app.models.post import Post, t_post_tag
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.media import Media, CommentMedia
from app.forms.post_form import PostForm
from app.forms.comment_form import CommentForm
from app.views.admin import generate_unique_slug
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from app import db
# 从 __init__.py 导入 bp_blog 蓝图
from app.views.blog import bp_blog

@bp_blog.route('/post/<string:slug>', methods=['GET', 'POST'])
def post_detail(slug):
    """
    显示文章详情
    :param slug: 文章slug
    :return: 渲染post.html页面
    """
    post = Post.query.filter_by(slug=slug, status=1).first_or_404()

    # 增加阅读计数
    post.counter = (post.counter or 0) + 1
    db.session.commit()

    # 获取分类名称
    category = Category.query.get(post.categoryid)

    # 获取标签列表
    tags = post.tag.all() if post.tag else []

    # 获取作者信息
    author = User.query.get(post.authorid)

    # 获取评论列表
    comments = Comment.query.filter_by(postid=post.id, status=True).order_by(Comment.date.desc()).all()

    # 处理评论表单
    form = CommentForm()
    # 设置RadioField的选项
    form.status.choices = [(True, '启用'), (False, '禁用')]
    if form.validate_on_submit():
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            flash('请先登录后再发表评论', 'warning')
            return redirect(url_for('bp_blog.login'))

        comment = Comment(
            postid=post.id,
            content=form.content.data,
            author=current_user.username,  # 使用登录用户的用户名
            author_email="",  # 暂时不收集邮箱
            author_IP=request.remote_addr,
            status=True
        )
        db.session.add(comment)
        db.session.flush()  # 获取评论ID
        
        # 处理多媒体文件上传
        media_files = request.files.getlist('media_files')
        for media_file in media_files:
            if media_file and media_file.filename:
                # 验证文件类型
                from app.views.common.media_resource import allowed_file, get_file_type, UPLOAD_FOLDER, MAX_FILE_SIZE
                if not allowed_file(media_file.filename):
                    current_app.logger.warning(f"上传文件类型不支持: {media_file.filename}")
                    continue
                
                # 检查文件大小
                media_file.seek(0, 2)  # 移动到文件末尾
                file_size = media_file.tell()  # 获取文件大小
                media_file.seek(0)  # 重置到文件开头
                
                if file_size > MAX_FILE_SIZE:
                    current_app.logger.warning(f"上传文件过大: {media_file.filename}")
                    continue
                
                # 生成唯一文件名
                import os
                import uuid
                filename = media_file.filename
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # 创建上传目录
                upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                os.makedirs(upload_path, exist_ok=True)
                
                # 保存文件
                file_path = os.path.join(upload_path, unique_filename)
                media_file.save(file_path)
                
                # 获取文件类型
                file_type = get_file_type(filename)
                from app.models.media import MediaType
                media_type = MediaType[file_type] if file_type else MediaType.document
                
                # 创建媒体记录
                media = Media(
                    filename=filename,
                    filepath=os.path.join(UPLOAD_FOLDER, unique_filename),
                    file_type=media_type,
                    file_size=file_size,
                    mime_type=media_file.content_type
                )
                
                # 如果用户已登录，记录上传者
                if current_user.is_authenticated:
                    media.uploader_id = current_user.id
                
                db.session.add(media)
                db.session.flush()  # 获取ID
                
                # 创建评论与媒体的关联
                comment_media = CommentMedia(comment_id=comment.id, media_id=media.id)
                db.session.add(comment_media)

        db.session.commit()
        flash('评论发表成功', 'success')
        return redirect(url_for('bp_blog.post_detail', slug=slug))

    return render_template('blog/post.html',
                           post=post,
                           title=post.title,
                           category=category,
                           tags=tags,
                           author=author,
                           comments=comments,
                           form=form)


# 添加用户文章列表路由（展示指定用户的所有已发布文章）
@bp_blog.route('/user/<int:user_id>/posts')
def user_posts(user_id):
    """
    展示指定用户的已发布文章列表
    :param user_id: 用户ID
    :return: 渲染user_posts.html页面
    """
    # 1. 查询用户信息（不存在则返回404）
    user = User.query.get_or_404(user_id)
    author_name = user.nickname or user.username  # 优先显示昵称，无则显示用户名

    # 2. 处理分页参数
    page = request.args.get('page', 1, type=int)

    # 3. 查询该用户的已发布文章（status=1 表示已发布），按发布时间倒序
    pagination = Post.query.filter_by(
        authorid=user_id,
        status=1  # 仅显示已发布文章，与草稿区分
    ).order_by(Post.publishtime.desc()).paginate(
        page=page,
        per_page=10,  # 每页10篇文章
        error_out=False  # 页码超出范围时返回空列表而非404
    )
    posts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    # 4. 处理文章的分类、标签数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        category = Category.query.get(post.categoryid)
        category_name = category.name if category else '未分类'

        # 获取标签列表
        tags = post.tag.all() if post.tag else []
        tag_names = [tag.name for tag in tags]

        # 获取作者信息（冗余处理，确保模板能拿到author字段）
        author = User.query.get(post.authorid)
        author_username = author.username if author else '未知作者'

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'category': category_name,
            'tags': tag_names,
            'publishtime': post.publishtime,
            'author': author_username,
            'author_id': post.authorid,  # 用于分页链接的user_id参数
            'slug': post.slug,  # 添加slug字段用于URL构建
            'counter': post.counter or 0,  # 添加阅读计数
            'favorites_count': post.favorites_count  # 添加收藏数
        })

    # 5. 渲染模板，传递必要参数
    return render_template(
        'blog/user_posts.html',
        posts=processed_posts,
        pagination=pagination,
        author_name=author_name,
        user_id=user_id,  # 传递user_id，确保分页链接正常
        categories=categories,
        tags=tags
    )


# 可选：添加编辑已发布文章的路由（适配模板中的编辑按钮）
@bp_blog.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    编辑已发布的文章
    :param post_id: 文章ID
    :return: 渲染编辑页面或重定向
    """
    # 1. 仅允许文章作者或管理员编辑
    post = Post.query.get_or_404(post_id)
    if post.authorid != current_user.id and not current_user.is_admin_user:
        abort(403)  # 权限不足

    # 2. 初始化表单
    form = PostForm(obj=post)

    # 3. 加载分类选项
    categories = Category.query.all()
    form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]

    # 4. 加载标签列表和当前文章的标签
    tags = Tag.query.all()
    post_tags = [tag.id for tag in post.tag.all()] if post.tag else []

    # 5. 表单提交处理
    if form.validate_on_submit():
        try:
            # 处理slug（如果修改了slug则重新生成唯一值）
            new_slug = form.slug.data.strip() if form.slug.data else ""
            if new_slug != post.slug:
                new_slug = generate_unique_slug(new_slug)

            # 为了避免basedpyright(reportCallIssue)错误，我们使用逐步赋值的方式更新Post对象
            post.title = form.title.data.strip() if form.title.data else ""
            post.slug = new_slug
            post.excerpt = form.excerpt.data.strip() if form.excerpt.data else ''
            post.content = form.content.data.strip() if form.content.data else ""
            post.categoryid = form.categoryid.data
            post.updatetime = datetime.now()

            # 处理标签关联
            tag_ids = request.form.getlist('tag_ids')
            # 清空现有标签关系 - 从关联表中删除相关记录
            from app.models.post import t_post_tag
            db.session.execute(t_post_tag.delete().where(t_post_tag.c.postid == post.id))
            if tag_ids:
                selected_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in selected_tags:
                    post.tag.append(tag)  # 添加新标签

            db.session.commit()
            flash('文章编辑成功', 'success')
            return redirect(url_for('bp_blog.post_detail', slug=post.slug))  # 使用slug参数跳转

        except Exception as e:
            db.session.rollback()
            flash(f'编辑失败: {str(e)}', 'danger')

    # 6. 渲染编辑页面（复用创建文章的模板）
    return render_template('blog/create_post.html', form=form, tags=tags, post_tags=post_tags, is_edit=True)


# 添加创建文章路由
@bp_blog.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """用户创建文章"""
    form = PostForm()
    
    # 加载分类
    categories = Category.query.all()
    form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]
    
    # 加载标签
    tags = Tag.query.all()
    
    if form.validate_on_submit():
        try:
            # 确定状态：发布=1，草稿=0
            status = 1 if request.form.get('action') == 'publish' else 0
            
            # 处理slug
            base_slug = (form.slug.data.strip() if form.slug.data else "") or (form.title.data.strip() if form.title.data else "")
            unique_slug = generate_unique_slug(base_slug)  # 复用admin中的函数
            
            # 为了避免basedpyright(reportCallIssue)错误，我们使用逐步赋值的方式创建Post对象
            post = Post()
            post.title = form.title.data.strip() if form.title.data else ""
            post.slug = unique_slug
            post.authorid = current_user.id
            post.excerpt = form.excerpt.data.strip() if form.excerpt.data else ''
            post.content = form.content.data.strip() if form.content.data else ""
            post.categoryid = form.categoryid.data or None
            post.counter = 0
            post.status = bool(status)
            post.publishtime = datetime.now() if status == 1 else None
            post.updatetime = datetime.now()
            
            db.session.add(post)
            db.session.flush()  # 先flush获取post.id，但不提交
            
            # 处理标签 - 需要在post被添加到session并flush后进行
            tag_ids = request.form.getlist('tag_ids')
            if tag_ids:
                selected_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in selected_tags:
                    post.tag.append(tag)  # 添加新标签
            
            db.session.commit()
            
            if status == 1:
                flash('文章发布成功', 'success')
                return redirect(url_for('bp_blog.post_detail', slug=unique_slug))
            else:
                flash('草稿保存成功', 'info')
                return redirect(url_for('bp_blog.drafts'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'操作失败: {str(e)}', 'danger')
    
    return render_template('blog/create_post.html', form=form, tags=tags)


# 添加草稿列表路由
@bp_blog.route('/drafts')
@login_required
def drafts():
    """用户草稿列表"""
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(authorid=current_user.id, status=False) \
        .order_by(Post.updatetime.desc()) \
        .paginate(page=page, per_page=10)
    drafts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    return render_template('blog/drafts.html',
                           drafts=drafts,
                           pagination=pagination,
                           categories=categories,
                           tags=tags)


# 添加标签文章列表路由
@bp_blog.route('/tag/<int:tag_id>')
def tag_posts(tag_id):
    """
    展示指定标签的文章列表
    :param tag_id: 标签ID
    :return: 渲染标签文章列表页面
    """
    # 1. 查询标签信息（不存在则返回404）
    tag = Tag.query.get_or_404(tag_id)

    # 2. 处理分页参数
    page = request.args.get('page', 1, type=int)

    # 3. 查询该标签的文章（仅显示已发布文章），按发布时间倒序
    # 使用关联表进行连接查询
    pagination = Post.query.join(t_post_tag, Post.id == t_post_tag.c.postid) \
        .filter(
            Post.status == 1,  # 仅显示已发布文章
            t_post_tag.c.tagid == tag_id
        ).order_by(Post.publishtime.desc()).paginate(
            page=page,
            per_page=10,
            error_out=False
        )
    posts = pagination.items

    # 4. 处理文章数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        category = Category.query.get(post.categoryid)
        category_name = category.name if category else '未分类'

        # 获取标签列表
        tags = post.tag.all() if post.tag else []
        # 修复标签数据结构，保持标签对象而不是仅名称
        tag_objects = tags

        # 获取作者信息
        author = User.query.get(post.authorid)
        author_username = author.nickname if author and author.nickname else (author.username if author else '未知作者')

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'category': category_name,
            'tags': tag_objects,  # 使用标签对象而不是名称列表
            'publishtime': post.publishtime,
            'author': author_username,
            'author_id': post.authorid,
            'slug': post.slug,
            'counter': post.counter or 0,
            'favorites_count': post.favorites_count
        })

    # 5. 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    # 6. 渲染模板，传递必要参数
    return render_template(
        'blog/tag_posts.html',
        posts=processed_posts,
        pagination=pagination,
        tag=tag,
        categories=categories,
        tags=tags
    )

# 添加编辑草稿路由
@bp_blog.route('/drafts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_draft(post_id):
    """编辑草稿"""
    post = Post.query.filter_by(id=post_id, authorid=current_user.id, status=False).first_or_404()
    form = PostForm(obj=post)
    
    # 加载分类
    categories = Category.query.all()
    form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]
    
    # 加载标签
    tags = Tag.query.all()
    post_tags = [tag.id for tag in post.tag.all()] if post.tag else []
    
    if form.validate_on_submit():
        try:
            # 确定状态：发布=1，草稿=0
            status = 1 if request.form.get('action') == 'publish' else 0
            
            # 处理slug
            new_slug = form.slug.data.strip() if form.slug.data else ""
            if new_slug != post.slug:
                new_slug = generate_unique_slug(new_slug)
            
            # 为了避免basedpyright(reportCallIssue)错误，我们使用逐步赋值的方式更新Post对象
            post.title = form.title.data.strip() if form.title.data else ""
            post.slug = new_slug
            post.excerpt = form.excerpt.data.strip() if form.excerpt.data else ''
            post.content = form.content.data.strip() if form.content.data else ""
            post.categoryid = form.categoryid.data
            post.status = status
            post.updatetime = datetime.now()
            
            # 如果是发布，设置发布时间
            if status == 1 and not post.publishtime:
                post.publishtime = datetime.now()
            
            # 处理标签 - 清空现有标签关系并添加新标签
            tag_ids = request.form.getlist('tag_ids')
            # 清空现有标签关系 - 从关联表中删除相关记录
            from app.models.post import t_post_tag
            db.session.execute(t_post_tag.delete().where(t_post_tag.c.postid == post.id))
            if tag_ids:
                selected_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in selected_tags:
                    post.tag.append(tag)  # 添加新标签
            
            db.session.commit()
            
            if status == 1:
                flash('文章发布成功', 'success')
                return redirect(url_for('bp_blog.post_detail', slug=new_slug))
            else:
                flash('草稿更新成功', 'info')
                return redirect(url_for('bp_blog.drafts'))
        except Exception as e:
            db.session.rollback()
            flash(f'操作失败: {str(e)}', 'danger')
    
    return render_template('blog/create_post.html', form=form, tags=tags, post_tags=post_tags)


# 添加发布草稿路由
@bp_blog.route('/drafts/<int:post_id>/publish')
@login_required
def publish_draft(post_id):
    """发布草稿"""
    post = Post.query.filter_by(id=post_id, authorid=current_user.id, status=False).first_or_404()

    try:
        post.status = True
        post.publishtime = datetime.now()
        post.updatetime = datetime.now()
        db.session.commit()
        flash('草稿发布成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'发布失败: {str(e)}', 'danger')

    return redirect(url_for('bp_blog.post_detail', slug=post.slug))


@bp_blog.route('/upload/image', methods=['POST'])
@login_required
def upload_image():
    """处理CKEditor上传的图片"""
    # Flask-CKEditor上传图片
    f = request.files.get('upload')
    if not f or not f.filename:
        from flask_ckeditor import upload_fail
        return upload_fail(message='No file selected!')
    
    # 验证文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    filename = secure_filename(f.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        from flask_ckeditor import upload_fail
        return upload_fail(message='File type not allowed!')
    
    try:
        # 验证文件大小
        f.seek(0, os.SEEK_END)  # 移动到文件末尾
        file_size = f.tell()  # 获取当前位置（文件大小）
        f.seek(0)  # 重置到文件开头
        
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        if file_size > MAX_FILE_SIZE:
            from flask_ckeditor import upload_fail
            return upload_fail(message='File too large! Maximum size is 50MB')
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 创建上传目录
        upload_path = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_path, unique_filename)
        f.save(file_path)
        
        # 返回CKEditor期望的格式
        image_url = url_for('bp_admin.uploaded_files', filename=unique_filename, _external=True)
        print(f"上传成功，图片URL: {image_url}")  # 调试信息
        from flask_ckeditor import upload_success
        return upload_success(url=image_url)
    except Exception as e:
        current_app.logger.error(f"上传图片失败: {str(e)}")
        from flask_ckeditor import upload_fail
        return upload_fail(message='Upload failed')

from flask import render_template, jsonify, current_app, request
from flask_login import current_user
from datetime import datetime
from app import db
from app.forms.post_form import PostForm
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.media import Media, PostMedia
from app.views.admin import bp_admin
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.views.common.post_resource import PostResource
import re
import uuid


@bp_admin.route('/post/list', methods=['GET'])
def admin_posts_view():
    return render_template('admin/post/post.html')


@bp_admin.route('/posts', methods=['GET'])
def get_posts():
    """文章列表接口"""
    try:
        result = PostResource.query_posts()
        if result['code'] == ResponseCode.SUCCESS:
            result['code'] = 20000000  # 与前端table的statusCode一致
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"获取文章列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 50000001,
            "message": f"服务器错误: {str(e)}",
            "count": 0,
            "data": []
        })


def generate_unique_slug(base_slug):
    """生成唯一slug，处理重复问题"""
    if not base_slug:
        return f"post-{uuid.uuid4().hex[:8]}"

    # 清理特殊字符
    slug = re.sub(r'[^\w\s-]', '', base_slug).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)

    # 检查是否已存在
    existing = Post.query.filter_by(slug=slug).first()
    if not existing:
        return slug

    # 若存在则添加随机字符串
    return f"{slug}-{uuid.uuid4().hex[:8]}"


@bp_admin.route('/post', methods=['GET', 'POST'])
def create_post():
    current_app.logger.debug("进入文章创建函数")
    form = PostForm()

    # 加载分类数据
    categories = Category.query.all()
    form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]

    if request.method == 'POST':
        # 验证表单
        if not form.validate():
            current_app.logger.debug(f"表单验证错误: {form.errors}")
            return jsonify({
                "code": 40000001,
                "message": f"表单验证失败: {form.errors}",
                "count": 0,
                "data": {}
            })

        try:
            # 获取状态值：发布=1，草稿=0
            status = int(request.form.get('status', 0))  # 确保是整数类型

            # 处理slug唯一性
            base_slug = form.slug.data.strip() or form.title.data.strip()
            unique_slug = generate_unique_slug(base_slug)

            post = Post(
                title=form.title.data.strip(),
                slug=unique_slug,
                authorid=current_user.id if current_user.is_authenticated else 0,
                excerpt=form.excerpt.data.strip() if form.excerpt.data else '',
                content=form.content.data.strip(),
                categoryid=form.categoryid.data,
                counter=0,
                status=status,  # 关键：使用获取到的状态值
                publishtime=datetime.now(),
                updatetime=datetime.now()
            )

            db.session.add(post)
            db.session.flush()

            # 处理标签
            tag_ids = request.form.getlist('tag_ids')
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                post.tag = tags
            
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
                    
                    # 创建文章与媒体的关联
                    post_media = PostMedia(post_id=post.id, media_id=media.id)
                    db.session.add(post_media)

            db.session.commit()
            current_app.logger.debug(f"文章创建成功，状态: {'已发布' if status else '草稿'}")

            return jsonify({
                "code": 20000000,
                "message": "创建成功",
                "count": 1,
                "data": {"id": post.id, "title": post.title, "status": status}
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"文章创建失败: {str(e)}", exc_info=True)
            # 针对slug重复的特殊提示
            if "UNIQUE constraint failed: t_post.slug" in str(e):
                return jsonify({
                    "code": 50000002,
                    "message": "创建失败：文章别名已存在，请修改后重试",
                    "count": 0,
                    "data": {}
                })
            return jsonify({
                "code": 50000002,
                "message": f"创建失败: {str(e)}",
                "count": 0,
                "data": {}
            })

    # 加载所有标签
    tags = Tag.query.all()
    return render_template('admin/post/post-new.html', post_form=form, tags=tags)


@bp_admin.route('/post/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_post(post_id):
    if request.method == 'GET':
        post = Post.query.get_or_404(post_id)
        form = PostForm(obj=post)

        # 加载分类
        categories = Category.query.all()
        form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]

        # 加载所有标签和当前文章的标签
        tags = Tag.query.all()
        post_tags = post.tag.all() if post.tag else []

        return render_template('admin/post/post-edit.html', post_form=form, post_id=post_id, tags=tags,
                               post_tags=post_tags)

    elif request.method == 'PUT':
        post = Post.query.get_or_404(post_id)
        form = PostForm(obj=post)

        categories = Category.query.all()
        form.categoryid.choices = [(c.id, c.name) for c in categories] if categories else [(0, '未分类')]

        if form.validate_on_submit():
            try:
                # 获取状态值
                status = int(request.form.get('status', 0))

                # 处理slug唯一性（更新时）
                new_slug = form.slug.data.strip()
                if new_slug != post.slug:
                    new_slug = generate_unique_slug(new_slug)

                post.title = form.title.data.strip()
                post.slug = new_slug
                post.excerpt = form.excerpt.data.strip() if form.excerpt.data else ''
                post.content = form.content.data.strip()
                post.categoryid = form.categoryid.data
                post.status = status  # 关键：更新状态值
                post.updatetime = datetime.now()

                # 处理标签
                tag_ids = request.form.getlist('tag_ids')
                if tag_ids:
                    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                    post.tag = tags
                else:
                    post.tag = []
                
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
                        
                        # 创建文章与媒体的关联
                        post_media = PostMedia(post_id=post.id, media_id=media.id)
                        db.session.add(post_media)

                db.session.commit()
                return jsonify({
                    "code": 20000000,
                    "message": "更新成功",
                    "count": 1,
                    "data": {"id": post.id, "status": status}
                })
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"文章更新失败: {str(e)}", exc_info=True)
                return jsonify({
                    "code": 50000002,
                    "message": f"更新失败: {str(e)}",
                    "count": 0,
                    "data": {}
                })

        return jsonify({
            "code": 40000001,
            "message": f"表单验证失败: {form.errors}",
            "count": 0,
            "data": {}
        })

    elif request.method == 'DELETE':
        try:
            post = Post.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            return jsonify({
                "code": 20000000,
                "message": "删除成功",
                "count": 0,
                "data": {}
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"文章删除失败: {str(e)}", exc_info=True)
            return jsonify({
                "code": 50000002,
                "message": f"删除失败: {str(e)}",
                "count": 0,
                "data": {}
            })
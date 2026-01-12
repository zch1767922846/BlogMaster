from flask import render_template, request
from flask_login import login_required, current_user
from app.models.post import Post
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app import db
# 从 __init__.py 导入 bp_blog 蓝图，而不是创建一个新的
from app.views.blog import bp_blog


@bp_blog.route('/')
def index():
    """
    博客首页，显示最新文章
    :return: 渲染index.html页面
    """
    # 处理分页参数
    page = request.args.get('page', 1, type=int)

    # 查询已发布的文章（status=True 表示已发布），按发布时间倒序
    pagination = Post.query.filter_by(status=True).order_by(Post.publishtime.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    posts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    # 处理文章的分类、标签和作者数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        category = Category.query.get(post.categoryid)

        # 获取标签列表
        tags = post.tag.all() if post.tag else []

        # 获取作者信息
        author = User.query.get(post.authorid)
        author_name = author.nickname if author and author.nickname else (author.username if author else '未知作者')
        # 确保author_id有值，默认为0
        author_id = post.authorid if post.authorid else 0

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'content': post.content,
            'category': category,
            'tags': tags,
            'publishtime': post.publishtime,
            'author': author_name,
            'slug': post.slug,  # 添加slug字段用于URL构建
            'author_id': author_id,  # 确保author_id字段存在且有效
            'counter': post.counter or 0,  # 添加阅读计数
            'favorites_count': post.favorites_count  # 添加收藏数
        })

    # 渲染模板
    return render_template('blog/index.html',
                           posts=processed_posts,
                           pagination=pagination,
                           categories=categories,
                           tags=tags)


# 添加home路由别名，以兼容旧的路由引用
@bp_blog.route('/home')
def home():
    """
    博客首页别名，重定向到主首页
    """
    from flask import redirect, url_for
    return redirect(url_for('bp_blog.index'))


@bp_blog.route('/user/home')
def user_home():
    """
    用户主页，显示所有已发布的文章
    :return: 渲染user_home.html页面
    """
    # 处理分页参数
    page = request.args.get('page', 1, type=int)

    # 查询已发布的文章（status=True 表示已发布），按发布时间倒序
    pagination = Post.query.filter_by(status=True).order_by(Post.publishtime.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    posts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    # 处理文章的分类、作者数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        category = Category.query.get(post.categoryid)

        # 获取作者信息
        author = User.query.get(post.authorid)
        author_name = author.nickname if author and author.nickname else (author.username if author else '未知作者')
        # 确保author_id有值，默认为0
        author_id = post.authorid if post.authorid else 0

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'category': category,
            'publishtime': post.publishtime,
            'author': author_name,
            'authorid': post.authorid,
            'author_id': author_id,  # 确保author_id字段存在且有效
            'slug': post.slug,  # 添加slug字段用于URL构建
            'counter': post.counter or 0,  # 添加阅读计数
            'favorites_count': post.favorites_count  # 添加收藏数
        })

    # 渲染模板，传递必要参数
    return render_template('blog/user_home.html',
                           posts=processed_posts,
                           pagination=pagination,
                           categories=categories,
                           tags=tags)


@bp_blog.route('/category/<int:category_id>')
def posts_by_category(category_id):
    """
    显示指定分类下的所有文章
    :param category_id: 分类ID
    :return: 渲染user_home.html页面，但只显示指定分类的文章
    """
    # 获取分类信息
    category = Category.query.get_or_404(category_id)
    
    # 处理分页参数
    page = request.args.get('page', 1, type=int)

    # 查询已发布的文章（status=True 表示已发布），按发布时间倒序，并限定分类
    pagination = Post.query.filter_by(status=True, categoryid=category_id).order_by(Post.publishtime.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    posts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for cat in categories:
        cat.post_count = Post.query.filter_by(categoryid=cat.id, status=True).count()

    tags = Tag.query.all()

    # 处理文章的分类、作者数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        post_category = Category.query.get(post.categoryid)

        # 获取作者信息
        author = User.query.get(post.authorid)
        author_name = author.nickname if author and author.nickname else (author.username if author else '未知作者')
        # 确保author_id有值，默认为0
        author_id = post.authorid if post.authorid else 0

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'category': post_category,
            'publishtime': post.publishtime,
            'author': author_name,
            'authorid': post.authorid,
            'author_id': author_id,  # 确保author_id字段存在且有效
            'slug': post.slug,  # 添加slug字段用于URL构建
            'counter': post.counter or 0,  # 添加阅读计数
            'favorites_count': post.favorites_count  # 添加收藏数
        })

    # 渲染模板，传递必要参数，同时传递当前分类信息
    return render_template('blog/user_home.html',
                           posts=processed_posts,
                           pagination=pagination,
                           categories=categories,
                           tags=tags,
                           current_category=category)


@bp_blog.route('/my/posts')
@login_required
def my_posts():
    """
    当前登录用户的文章列表
    :return: 渲染user_posts.html页面
    """
    # 处理分页参数
    page = request.args.get('page', 1, type=int)
    
    # 查询当前用户已发布的文章，按发布时间倒序
    pagination = Post.query.filter_by(
        authorid=current_user.id,
        status=True
    ).order_by(Post.publishtime.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    posts = pagination.items

    # 获取分类和标签数据用于侧边栏
    categories = Category.query.all()
    # 为每个分类添加文章数量
    for category in categories:
        category.post_count = Post.query.filter_by(categoryid=category.id, status=True).count()

    tags = Tag.query.all()

    # 处理文章的分类、标签数据（适配模板展示）
    processed_posts = []
    for post in posts:
        # 获取分类名称
        category = Category.query.get(post.categoryid)
        category_name = category.name if category else '未分类'

        # 获取标签列表
        tags = post.tag.all() if post.tag else []
        # 修复标签数据结构，保持标签对象而不是仅名称
        tag_objects = tags

        processed_posts.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'category': category_name,
            'tags': tag_objects,  # 使用标签对象而不是名称列表
            'publishtime': post.publishtime,
            'author': current_user.nickname or current_user.username,
            'author_id': post.authorid,
            'slug': post.slug,
            'counter': post.counter or 0,  # 添加阅读计数
            'favorites_count': post.favorites_count  # 添加收藏数
        })

    # 渲染模板，传递必要参数
    return render_template(
        'blog/user_posts.html',
        posts=processed_posts,
        pagination=pagination,
        author_name=current_user.nickname or current_user.username,
        user_id=current_user.id,
        categories=categories,
        tags=tags
    )
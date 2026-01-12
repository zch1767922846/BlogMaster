from flask import render_template
# 从 __init__.py 导入 bp_blog 蓝图
from app.views.blog import bp_blog

@bp_blog.route('/category')
def blog_category():
    return render_template('blog/category.html')
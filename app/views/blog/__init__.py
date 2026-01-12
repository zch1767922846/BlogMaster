from flask import Blueprint

bp_blog = Blueprint('bp_blog', __name__)

# 修复导入顺序，确保所有视图都被正确导入，特别是index模块
# 确保post模块也被正确导入以注册user_posts路由
from app.views.blog import index, category, page, login, register, post, favorite
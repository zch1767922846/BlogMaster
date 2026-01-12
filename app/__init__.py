import logging
import logging.config
from typing import TYPE_CHECKING

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config, config

if TYPE_CHECKING:
    from flask_login import LoginManager as _LoginManager
    login_manager: _LoginManager
else:
    login_manager = LoginManager()

db = SQLAlchemy()
mail = Mail()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 如果没有提供配置名称，则从环境变量获取或使用默认值
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG') or 'default'
    
    # 如果传入的是配置类实例，则直接使用；否则从配置字典中获取
    if isinstance(config_name, str):
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config_name)
    
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # 设置登录视图
    if TYPE_CHECKING:
        # 在类型检查时忽略类型错误
        pass
    else:
        login_manager.login_view = 'bp_blog.login'
    login_manager.login_message = '请先登录以访问此页面。'
    login_manager.login_message_category = 'info'
    
    # 设置用户加载函数
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from app.views.blog import bp_blog
    from app.views.admin import bp_admin
    
    app.register_blueprint(bp_blog)
    app.register_blueprint(bp_admin, url_prefix='/admin')
    
    # 添加根路径重定向到博客首页
    @app.route('/')
    def index_redirect():
        from flask import redirect, url_for
        # 确保 bp_blog.index 端点已正确注册
        return redirect(url_for('bp_blog.index'))
    
    return app


# 注册插件扩展
def register_plugins(app):
    mail.init_app(app)
    db.init_app(app)


# 注册日志处理函数
def register_logging(app):
    pass


# 注册蓝图 - 已在 create_app 中注册，此处无需重复注册
def register_blueprints(app: Flask):
    pass


# 注册restful API
def register_restful_apis(app):
    from app.api.v1 import api, registerResources
    registerResources()
    api.init_app(app)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        from app.models.category import Category
        from app.models.comment import Comment
        from app.models.page import Page
        from app.models.post import Post
        from app.models.site import Site
        from app.models.tag import Tag
        from app.models.user import User, Role
        return dict(app=app, db=db, User=User, Role=Role, Post=Post, Category=Category, Page=Page, Tag=Tag,
                    Comment=Comment, Site=Site)


# 模板上下文处理函数
def register_template_context(app):
    pass
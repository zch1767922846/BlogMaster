# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models.user import User
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.page import Page
from app.models.site import Site
from app.models.media import Media, PostMedia, CommentMedia
from flask.cli import with_appcontext
import click

# 设置默认配置
os.environ.setdefault('FLASK_CONFIG', 'development')

def create_app_instance():
    return create_app()


app = create_app_instance()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post, Category=Category, Tag=Tag, Comment=Comment, Page=Page, Site=Site, Media=Media, PostMedia=PostMedia, CommentMedia=CommentMedia)

@app.cli.command()
@with_appcontext
def init_db():
    """初始化数据库"""
    db.create_all()
    click.echo('数据库已初始化')

if __name__ == '__main__':
    app.run(debug=True)
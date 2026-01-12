# -*- coding: utf-8 -*-
# File: comment_resource.py
# Author: Zhangzhijun
# Date: 2021/2/13 17:25

from flask import current_app
from app.models.comment import Comment
from app.models.post import Post
from app.errors.errorcode import ResponseCode, ResponseMessage


class CommentResource:
    @staticmethod
    def query_comments():
        try:
            comments = Comment.query.all()
            comment_list = []
            for comment in comments:
                # 获取文章标题
                post = Post.query.get(comment.postid)
                post_title = post.title if post else '未知文章'
                
                comment_dict = {
                    'id': comment.id,
                    'post_title': post_title,
                    'author': comment.author,
                    'content': comment.content,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M:%S') if comment.date else '',
                    'status': comment.status
                }
                comment_list.append(comment_dict)
            
            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": len(comment_list),
                "data": comment_list
            }
        except Exception as e:
            current_app.logger.error("查询评论失败: %s", str(e))
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": ResponseMessage.QUERY_DB_FAILED,
                "count": 0,
                "data": []
            }
    
    @staticmethod
    def query_comment_by_id(comment_id):
        try:
            comment = Comment.query.filter_by(id=comment_id).first()
            if comment is None:
                return {
                    "code": ResponseCode.COMMENT_NOT_EXIST,
                    "message": ResponseMessage.COMMENT_NOT_EXIST,
                    "count": 0,
                    "data": {}
                }
            # 获取文章标题
            post = Post.query.get(comment.postid)
            post_title = post.title if post else '未知文章'
            
            comment_data = {
                'id': comment.id,
                'post_title': post_title,
                'author': comment.author,
                'content': comment.content,
                'date': comment.date.strftime('%Y-%m-%d %H:%M:%S') if comment.date else '',
                'status': comment.status
            }
            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": comment_data
            }
        except Exception as e:
            current_app.logger.error("查询评论失败: %s", str(e))
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": ResponseMessage.QUERY_DB_FAILED,
                "count": 0,
                "data": {}
            }
    
    @staticmethod
    def query_comment_by_title(comment_title):
        # 标题查询方法，这里可能需要调整逻辑
        try:
            comments = Comment.query.filter(Comment.author.like(f'%{comment_title}%')).all()
            comment_list = []
            for comment in comments:
                # 获取文章标题
                post = Post.query.get(comment.postid)
                post_title = post.title if post else '未知文章'
                
                comment_dict = {
                    'id': comment.id,
                    'post_title': post_title,
                    'author': comment.author,
                    'content': comment.content,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M:%S') if comment.date else '',
                    'status': comment.status
                }
                comment_list.append(comment_dict)
            
            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": len(comment_list),
                "data": comment_list
            }
        except Exception as e:
            current_app.logger.error("查询评论失败: %s", str(e))
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": ResponseMessage.QUERY_DB_FAILED,
                "count": 0,
                "data": []
            }

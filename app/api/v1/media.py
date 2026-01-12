from flask import request, jsonify
from flask_restful import Resource

from app.views.common.media_resource import upload_media, get_media_by_id
from app.models.post import Post
from app.models.comment import Comment
from app.models.media import PostMedia, CommentMedia
from app import db
from app.errors.errorcode import ResponseCode, ResponseMessage


class MediaUploadResource(Resource):
    def post(self):
        """上传媒体文件"""
        return upload_media()


class MediaResource(Resource):
    def get(self, media_id):
        """获取媒体文件信息"""
        return get_media_by_id(media_id)


class PostMediaResource(Resource):
    def post(self, post_id):
        """为文章关联媒体文件"""
        post = Post.query.get_or_404(post_id)
        data = request.get_json()
        media_id = data.get('media_id')
        
        if not media_id:
            return {'code': ResponseCode.PARAM_ERROR, 'message': 'Media ID is required'}, 400
        
        # 检查媒体文件是否存在
        from app.models.media import Media
        media = Media.query.get_or_404(media_id)
        
        # 检查是否已经关联
        existing = PostMedia.query.filter_by(post_id=post_id, media_id=media_id).first()
        if existing:
            return {'code': ResponseCode.SUCCESS, 'message': 'Media already associated with post'}, 200
        
        # 创建关联
        post_media = PostMedia(post_id=post_id, media_id=media_id)
        db.session.add(post_media)
        db.session.commit()
        
        return {
            'code': ResponseCode.SUCCESS,
            'message': ResponseMessage.SUCCESS,
            'data': {
                'post_id': post_id,
                'media_id': media_id
            }
        }
    
    def delete(self, post_id):
        """取消文章与媒体文件的关联"""
        data = request.get_json()
        media_id = data.get('media_id')
        
        if not media_id:
            return {'code': ResponseCode.PARAM_ERROR, 'message': 'Media ID is required'}, 400
        
        post_media = PostMedia.query.filter_by(post_id=post_id, media_id=media_id).first()
        if not post_media:
            return {'code': ResponseCode.DATA_NOT_EXIST, 'message': 'Association not found'}, 404
        
        db.session.delete(post_media)
        db.session.commit()
        
        return {
            'code': ResponseCode.SUCCESS,
            'message': ResponseMessage.SUCCESS
        }


class CommentMediaResource(Resource):
    def post(self, comment_id):
        """为评论关联媒体文件"""
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        media_id = data.get('media_id')
        
        if not media_id:
            return {'code': ResponseCode.PARAM_ERROR, 'message': 'Media ID is required'}, 400
        
        # 检查媒体文件是否存在
        from app.models.media import Media
        media = Media.query.get_or_404(media_id)
        
        # 检查是否已经关联
        existing = CommentMedia.query.filter_by(comment_id=comment_id, media_id=media_id).first()
        if existing:
            return {'code': ResponseCode.SUCCESS, 'message': 'Media already associated with comment'}, 200
        
        # 创建关联
        comment_media = CommentMedia(comment_id=comment_id, media_id=media_id)
        db.session.add(comment_media)
        db.session.commit()
        
        return {
            'code': ResponseCode.SUCCESS,
            'message': ResponseMessage.SUCCESS,
            'data': {
                'comment_id': comment_id,
                'media_id': media_id
            }
        }
    
    def delete(self, comment_id):
        """取消评论与媒体文件的关联"""
        data = request.get_json()
        media_id = data.get('media_id')
        
        if not media_id:
            return {'code': ResponseCode.PARAM_ERROR, 'message': 'Media ID is required'}, 400
        
        comment_media = CommentMedia.query.filter_by(comment_id=comment_id, media_id=media_id).first()
        if not comment_media:
            return {'code': ResponseCode.DATA_NOT_EXIST, 'message': 'Association not found'}, 404
        
        db.session.delete(comment_media)
        db.session.commit()
        
        return {
            'code': ResponseCode.SUCCESS,
            'message': ResponseMessage.SUCCESS
        }
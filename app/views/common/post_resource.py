from flask import current_app
from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.user import User
from app.models.tag import Tag
from app.errors.errorcode import ResponseCode, ResponseMessage


class PostResource:
    @staticmethod
    def query_posts():
        """查询所有文章（简化版，先保证基础数据显示）"""
        current_app.logger.debug("Enter query_posts function!")
        try:
            # 先查询Post表的基础字段，暂时去掉复杂关联（逐步添加）
            posts = Post.query.order_by(Post.publishtime.desc()).all()

            post_list = []
            for post in posts:
                # 手动构建字典，只处理Post表自身字段（先保证显示）
                post_dict = {
                    'id': post.id,
                    'title': post.title or '',
                    'slug': post.slug or '',
                    'authorid': post.authorid or 0,
                    'author_name': '',  # 先留空，后续补充分类/作者关联
                    'excerpt': post.excerpt or '',
                    'content': post.content or '',
                    'categoryid': post.categoryid or 0,
                    'category_name': '',  # 先留空
                    'image': post.image or '',
                    'counter': post.counter or 0,
                    'status': bool(post.status) if post.status is not None else False,
                    'publishtime': post.publishtime.strftime('%Y-%m-%d %H:%M:%S') if post.publishtime else '',
                    'updatetime': post.updatetime.strftime('%Y-%m-%d %H:%M:%S') if post.updatetime else '',
                    'tag_names': []  # 先留空
                }

                # 补充分类名称（单独查询，避免关联查询出错）
                if post.categoryid:
                    category = Category.query.get(post.categoryid)
                    post_dict['category_name'] = category.name if category else ''

                # 补充作者名称（单独查询）
                if post.authorid:
                    user = User.query.get(post.authorid)
                    post_dict['author_name'] = user.username if user else ''

                # 补充标签名称（单独查询）
                if post.tag:  # 假设Post模型的tag是关联属性（多对多）
                    post_dict['tag_names'] = [tag.name for tag in post.tag.all()]

                post_list.append(post_dict)

            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": len(post_list),
                "data": post_list
            }
        except Exception as e:
            current_app.logger.error(f"查询文章失败: {str(e)}", exc_info=True)  # 打印完整堆栈
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": f"查询失败: {str(e)}",
                "count": 0,
                "data": []
            }

    @staticmethod
    def query_post_by_id(post_id):
        """按ID查询单篇文章（简化版）"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return {
                    "code": ResponseCode.POST_NOT_EXIST,
                    "message": ResponseMessage.POST_NOT_EXIST,
                    "count": 0,
                    "data": {}
                }

            post_data = {
                'id': post.id,
                'title': post.title or '',
                'slug': post.slug or '',
                'authorid': post.authorid or 0,
                'author_name': '',
                'excerpt': post.excerpt or '',
                'content': post.content or '',
                'categoryid': post.categoryid or 0,
                'category_name': '',
                'image': post.image or '',
                'counter': post.counter or 0,
                'status': bool(post.status) if post.status is not None else False,
                'publishtime': post.publishtime.strftime('%Y-%m-%d %H:%M:%S') if post.publishtime else '',
                'updatetime': post.updatetime.strftime('%Y-%m-%d %H:%M:%S') if post.updatetime else '',
                'tag_names': []
            }

            # 补充分类名称
            if post.categoryid:
                category = Category.query.get(post.categoryid)
                post_data['category_name'] = category.name if category else ''

            # 补充作者名称
            if post.authorid:
                user = User.query.get(post.authorid)
                post_data['author_name'] = user.username if user else ''

            # 补充标签名称
            if post.tag:
                post_data['tag_names'] = [tag.name for tag in post.tag.all()]

            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": post_data
            }
        except Exception as e:
            current_app.logger.error(f"查询文章失败: {str(e)}", exc_info=True)
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": ResponseMessage.QUERY_DB_FAILED,
                "count": 0,
                "data": {}
            }

    @staticmethod
    def query_post_by_title(post_title):
        """按标题查询文章（简化版）"""
        try:
            post = Post.query.filter_by(title=post_title).first()
            if not post:
                return {
                    "code": ResponseCode.POST_NOT_EXIST,
                    "message": ResponseMessage.POST_NOT_EXIST,
                    "count": 0,
                    "data": {}
                }

            post_data = {
                'id': post.id,
                'title': post.title or '',
                'slug': post.slug or '',
                'authorid': post.authorid or 0,
                'author_name': '',
                'excerpt': post.excerpt or '',
                'content': post.content or '',
                'categoryid': post.categoryid or 0,
                'category_name': '',
                # 'image': post.image or '',
                'counter': post.counter or 0,
                'status': bool(post.status) if post.status is not None else False,
                'publishtime': post.publishtime.strftime('%Y-%m-%d %H:%M:%S') if post.publishtime else '',
                'updatetime': post.updatetime.strftime('%Y-%m-%d %H:%M:%S') if post.updatetime else '',
                'tag_names': []
            }

            # 补充分类名称
            if post.categoryid:
                category = Category.query.get(post.categoryid)
                post_data['category_name'] = category.name if category else ''

            # 补充作者名称
            if post.authorid:
                user = User.query.get(post.authorid)
                post_data['author_name'] = user.username if user else ''

            # 补充标签名称
            if post.tag:
                post_data['tag_names'] = [tag.name for tag in post.tag.all()]

            return {
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": post_data
            }
        except Exception as e:
            current_app.logger.error(f"查询文章失败: {str(e)}", exc_info=True)
            return {
                "code": ResponseCode.QUERY_DB_FAILED,
                "message": ResponseMessage.QUERY_DB_FAILED,
                "count": 0,
                "data": {}
            }
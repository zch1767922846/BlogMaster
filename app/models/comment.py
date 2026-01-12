from app import db
from app.models.media import CommentMedia


class Comment(db.Model):
    __tablename__ = 't_comment'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    postid = db.Column(db.Integer, db.ForeignKey('t_post.id'), comment='文章id')
    content = db.Column(db.Text, comment='评论内容')
    # userid = db.Column(db.Integer, db.ForeignKey('t_user.id'), comment='用户id')
    # no need to login when publish a comment.
    author = db.Column(db.String(64), nullable=False, comment='用户昵称')
    author_email = db.Column(db.String(128), nullable=False, comment='邮箱')
    author_IP = db.Column(db.String(128), nullable=False, comment='IP')
    date = db.Column(db.DateTime, server_default=db.func.now(), comment='发表时间')
    parentid = db.Column(db.Integer, db.ForeignKey("t_comment.id"), comment='父评论id')
    status = db.Column(db.Boolean, default=True, comment='评论状态')

    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)

    # 关联关系
    medias = db.relationship('Media', secondary='t_comment_media', backref=db.backref('comments', overlaps='comment_medias,media'), lazy='dynamic', overlaps='post')
    
    def __repr__(self):
        return '<Model Comment `{}`>'.format(self.author)
from flask_login import current_user

from app import db
from app.models.category import Category
from app.models.media import PostMedia


t_post_tag = db.Table('t_post_tag',
                      db.Column('id', db.Integer, autoincrement=True, primary_key=True),
                      db.Column('tagid', db.Integer, db.ForeignKey('t_tag.id'), index=True),
                      db.Column('postid', db.Integer, db.ForeignKey('t_post.id'), index=True)
                      )


class Post(db.Model):
    __tablename__ = 't_post'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False, index=True, comment='文章标题')
    slug = db.Column(db.String(64), nullable=False, unique=True, comment='标题别名')
    authorid = db.Column(db.Integer, db.ForeignKey('t_user.id'), comment='作者ID')
    excerpt = db.Column(db.Text, comment='摘要')
    content = db.Column(db.Text, comment='内容')
    categoryid = db.Column(db.Integer, db.ForeignKey('t_category.id'), comment='分类ID')
    publishtime = db.Column(db.DateTime, nullable=True, comment='发布时间')
    updatetime = db.Column(db.DateTime, nullable=True, comment='修改时间')
    counter = db.Column(db.Integer, default=0, comment='阅读计数')
    status = db.Column(db.Boolean, default=True, comment='文章状态')
    image = db.Column(db.String(500), nullable=True, comment='标签')
    # 关联关系
    tag = db.relationship('Tag', secondary='t_post_tag', backref=db.backref('posts'), lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    medias = db.relationship('Media', secondary='t_post_media', backref=db.backref('posts', overlaps='post_medias,media'), lazy='dynamic', overlaps='tag,comments')
    
    @property
    def favorites_count(self):
        """获取文章被收藏的数量"""
        from app.models.favorite import Favorite
        return Favorite.query.filter_by(post_id=self.id).count()

    def __repr__(self):
        return '<Post %r>' % self.title
import enum

from flask_login import UserMixin
from sqlalchemy import text

from app import db


class UserStatus(enum.Enum):
    normal = 0
    frozen = 1


t_role_permission = db.Table('t_role_permission',
                             db.Column('id', db.Integer, autoincrement=True, primary_key=True),
                             db.Column('roleid', db.Integer, db.ForeignKey('t_role.id'), index=True),
                             db.Column('permissionid', db.Integer, db.ForeignKey('t_permission.id'), index=True)
                             )


class Permission(db.Model):
    __tablename__ = 't_permission'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(21), unique=True)
    description = db.Column(db.String(64), nullable=True)
    role = db.relationship('Role', secondary='t_role_permission', backref=db.backref('t_role'), lazy='dynamic')


t_user_role = db.Table('t_user_role',
                       db.Column('id', db.Integer, autoincrement=True, primary_key=True),
                       db.Column('userid', db.Integer, db.ForeignKey('t_user.id'), index=True),
                       db.Column('roleid', db.Integer, db.ForeignKey('t_role.id'), index=True)
                       )


class Role(db.Model):
    __tablename__ = 't_role'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(21), unique=True)
    description = db.Column(db.String(64), nullable=True)
    permission = db.relationship('Permission', secondary='t_role_permission', backref=db.backref('t_permission'),
                                 lazy='dynamic')
    user = db.relationship('User', secondary='t_user_role', backref=db.backref('t_user'), lazy='dynamic')


class User(db.Model, UserMixin):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, comment='登录名')
    nickname = db.Column(db.String(64), nullable=False, unique=True, comment='用户昵称')
    password = db.Column(db.String(256), nullable=False, comment='密码')
    email = db.Column(db.String(128), nullable=False, unique=True, comment='邮箱')
    roleid = db.Column(db.Integer, db.ForeignKey('t_role.id'), comment='角色ID')
    registertime = db.Column(db.DateTime, server_default=db.func.now(), comment='创建时间')
    status = db.Column(db.Boolean, server_default=text('True'), comment='用户状态')
    avatar = db.Column(db.String(256), comment='头像路径')
    post = db.relationship('Post', backref=db.backref('t_user'), lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)



    def set_password(self, password):
        """用来设置密码的方法，接受密码作为参数,将生成的密码保持到对应字段"""
        self.password = password

    def validate_password(self, password):
        """用于验证密码的方法，接受密码作为参数, 返回布尔值"""
        return self.password == password

    def set_role(self):
        """为用户设置角色,默认为user"""
        if self.role is None:
            role = Role.query.filter_by(code='subscriber').first()
            self.role = role
            db.session.commit()

    @property
    def get_status(self):
        return self.status

    def check_password(self, password):
        # 直接比较明文密码
        return self.password == password

    @property
    def is_admin_user(self):
        return self.username == 'admin'

    def __repr__(self):
        return '<User %r>' % self.username

    # 收藏功能相关方法
    def favorite_post(self, post):
        """收藏文章"""
        if not self.has_favorited(post):
            from app.models.favorite import Favorite
            favorite = Favorite(user_id=self.id, post_id=post.id)
            db.session.add(favorite)

    def unfavorite_post(self, post):
        """取消收藏文章"""
        from app.models.favorite import Favorite
        favorite = Favorite.query.filter_by(user_id=self.id, post_id=post.id).first()
        if favorite:
            db.session.delete(favorite)

    def has_favorited(self, post):
        """检查是否已收藏文章"""
        from app.models.favorite import Favorite
        return Favorite.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

    def favorite_posts(self):
        """获取用户收藏的所有文章"""
        from app.models.favorite import Favorite
        from app.models.post import Post
        return Post.query.join(Favorite).filter(Favorite.user_id == self.id)
from app import db


class Favorite(db.Model):
    __tablename__ = 't_user_favorite'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('t_post.id'), index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 关系定义
    user = db.relationship('User', backref=db.backref('favorites', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('favorited_by', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        super(Favorite, self).__init__(**kwargs)
        
    def __repr__(self):
        return '<Favorite user_id={}, post_id={}>'.format(self.user_id, self.post_id)

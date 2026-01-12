from flask import flash, jsonify, current_app
from flask_login import login_required

from app import db
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.models.user import User, Role
from app.utils import query_to_dict


class UserResource():
    @staticmethod
    def query_users(self):
        try:
            users = User.query(User.id, User.username, User.nickname, Role.code, User.email, User.registertime,
                               User.status) \
                .filter(User.roleid == Role.id) \
                .all()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if users is None:
            return dict(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(users))
        current_app.logger.debug("data: %s", data)
        return data

    @staticmethod
    def query_user_by_name(self, username):
        try:
            user = User.query(User.id, User.username, User.nickname, Role.code, User.email, User.registertime,
                              User.status) \
                .filter(User.username == username) \
                .filter(User.roleid == Role.id) \
                .first()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if user is None:
            return dict(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)
        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(user))
        current_app.logger.debug("data: %s", data)
        return jsonify(data)

    @login_required
    def update_user(self, user):

        try:
            u = User.query.filter_by(username=user.username).first()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if u is None:
            return dict(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

        u.username = user.username,
        u.nickname = user.nickname,
        u.email = user.email

        db.session.commit()
        data = dict(code=ResponseCode.UPDATE_USER_SUCCESS, message=ResponseMessage.UPDATE_USER_SUCCESS)
        return jsonify(data)

    @login_required
    def delete_user(self, username):
        try:
            user = User.query.filter_by(username=username).first()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if user is None:
            return dict(code=ResponseCode.USER_NOT_EXIST, message=ResponseMessage.USER_NOT_EXIST)

        db.session.delete(user)
        db.session.commit()
        flash('Category deleted.', 'success')

        date = dict(code=ResponseCode.DELETE_USER_SUCCESS, message=ResponseMessage.DELETE_USER_SUCCESS)
        return jsonify(date)

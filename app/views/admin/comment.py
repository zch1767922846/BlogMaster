from flask import render_template, flash, redirect, url_for, jsonify

from app import db
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.forms.comment_form import CommentForm
from app.models.comment import Comment
from app.views.admin import bp_admin
from app.views.common.comment_resource import CommentResource


@bp_admin.route('/comment/list', methods=['GET'])
def admin_comments_view():
    return render_template('admin/comment/comment.html')


@bp_admin.route('/comment', methods=['GET', 'Post'])
def create_comment():
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = get_comment_info(comment_form)
        db.session.add(comment)
        db.session.commit()
        flash('Comment created.', 'success')
        return redirect(url_for('bp_admin.admin_comments_view'))
    return render_template('admin/comment/comment-new.html', comment_form=comment_form)


@bp_admin.route('/comments', methods=['GET'])
def get_comments():
    data = CommentResource.query_comments()
    return jsonify(data)


@bp_admin.route('/comment/<int:comment_id>', methods=['GET'])
def get_comment_by_id(comment_id):
    data = CommentResource.query_comment_by_id(comment_id)
    return jsonify(data)


@bp_admin.route('/comment/<string:comment_title>', methods=['GET'])
def get_comment_by_title(comment_title):
    data = CommentResource.query_comment_by_title(comment_title)
    return jsonify(data)


@bp_admin.route('/comment/<string:comment_author>', methods=['GET'])
def get_comment_by_author(comment_author):
    data = CommentResource.query_comment_by_title(comment_author)
    return jsonify(data)


@bp_admin.route('/comment/<int:comment_id>', methods=['GET', 'PUT'])
def update_comment(comment_id):
    comment_form = CommentForm()
    try:
        comment = Comment.query.filter_by(id=comment_id).first()
    except:
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
    if comment is None:
        return jsonify(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)

    if comment_form.validate_on_submit():
        comment = get_comment_info(comment_form)
        db.session.add(comment)
        db.session.commit()
        flash('comment updated.', 'success')
        return redirect(url_for('admin.comment'))
    comment_form.title.data = comment.title
    comment_form.slug.data = comment.slug
    comment_form.excerpt.data = comment.excerpt
    comment_form.content.data = comment.content
    comment_form.categoryid.data = comment.categoryid
    comment_form.status.data = comment.status
    return render_template('admin/comment/comment-edit.html', comment_form=comment_form)


@bp_admin.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        comment = Comment.query.filter_by(id=comment_id).first()
    except:
        return jsonify(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
    if comment is None:
        return jsonify(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('bp_admin.get_comments'))


# 从表单中获取Comment信息
def get_comment_info(form):
    comment = Comment()
    comment.title = form.title.data
    comment.authorid = form.authorid.data
    comment.content = form.content.data
    return comment

from flask import render_template, redirect, url_for, flash, current_app, jsonify
from app import db
from app.forms.tag_form import TagForm
from app.models.tag import Tag
from app.errors.errorcode import ResponseCode, ResponseMessage
from app.utils import query_to_dict
from app.views.admin import bp_admin


# 标签列表页（仅渲染模板）
@bp_admin.route('/tag/list', methods=['GET'])
def admin_tag_view():
    return render_template('admin/post/tag.html')


# 标签列表接口（对接前端表格，与分类列表格式一致）
@bp_admin.route('/tags', methods=['GET'])
def get_tags():
    """查询所有标签，返回规范格式（与分类列表一致）"""
    try:
        # 查询t_tag表所有字段
        tags = Tag.query.order_by(Tag.id.desc()).all()

        # 转换为字典列表
        tag_list = []
        for tag in tags:
            tag_dict = query_to_dict(tag)
            tag_list.append(tag_dict)

        # 规范返回格式（与分类列表一致）
        return jsonify({
            "code": ResponseCode.SUCCESS,
            "message": ResponseMessage.SUCCESS,
            "count": len(tag_list),
            "data": tag_list
        })
    except Exception as e:
        current_app.logger.error(f"查询标签失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.QUERY_DB_FAILED,
            "message": ResponseMessage.QUERY_DB_FAILED,
            "count": 0,
            "data": []
        })


# 创建标签
@bp_admin.route('/tag', methods=['GET', 'POST'])
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        # 检查标签是否已存在
        existing_tag = Tag.query.filter_by(name=form.name.data).first()
        if existing_tag:
            return jsonify({
                "code": ResponseCode.TAG_ALREADY_EXIST,
                "message": ResponseMessage.TAG_ALREADY_EXIST,
                "count": 0,
                "data": {}
            })
        try:
            # 保存t_tag表字段
            tag = Tag(name=form.name.data)
            db.session.add(tag)
            db.session.commit()
            flash('标签创建成功', 'success')

            return jsonify({
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": query_to_dict(tag)
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建标签失败: {str(e)}")
            return jsonify({
                "code": ResponseCode.DB_OPERATION_FAILED,
                "message": ResponseMessage.DB_OPERATION_FAILED,
                "count": 0,
                "data": {}
            })
    # GET请求返回创建页面
    return render_template('admin/post/tag-new.html', form=form)


# 编辑标签
@bp_admin.route('/tag/<int:tag_id>', methods=['GET', 'POST'])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        # 检查标签名重复
        existing_tag = Tag.query.filter(Tag.name == form.name.data, Tag.id != tag_id).first()
        if existing_tag:
            return jsonify({
                "code": ResponseCode.TAG_ALREADY_EXIST,
                "message": ResponseMessage.TAG_ALREADY_EXIST,
                "count": 0,
                "data": {}
            })
        try:
            # 更新t_tag表字段
            tag.name = form.name.data
            db.session.commit()
            return jsonify({
                "code": ResponseCode.SUCCESS,
                "message": ResponseMessage.SUCCESS,
                "count": 1,
                "data": query_to_dict(tag)
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"编辑标签失败: {str(e)}")
            return jsonify({
                "code": ResponseCode.DB_OPERATION_FAILED,
                "message": ResponseMessage.DB_OPERATION_FAILED,
                "count": 0,
                "data": {}
            })
    return render_template('admin/post/tag-edit.html', form=form, tag_id=tag_id)


# 删除标签
@bp_admin.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    try:
        tag = Tag.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return jsonify({
            "code": ResponseCode.SUCCESS,
            "message": ResponseMessage.SUCCESS,
            "count": 0,
            "data": {}
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除标签失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.DB_OPERATION_FAILED,
            "message": ResponseMessage.DB_OPERATION_FAILED,
            "count": 0,
            "data": {}
        })
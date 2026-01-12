from flask import render_template, redirect, url_for, flash, jsonify, request
from app import db
from app.models.category import Category
from app.forms.category_form import CategoryForm
from app.errors.errorcode import ResponseCode, ResponseMessage
from . import bp_admin


@bp_admin.route('/category/list', methods=['GET'])
def admin_categories_view():
    return render_template('admin/category/category.html')


@bp_admin.route('/category/new', methods=['GET'])
def new_category_view():
    form = CategoryForm()
    return render_template('admin/category/category-new.html', form=form)


@bp_admin.route('/category/edit/<int:category_id>', methods=['GET'])
def edit_category_view(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    form.name.data = category.name
    form.description.data = category.description
    return render_template('admin/category/category-edit.html', form=form, category=category)


@bp_admin.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    data = []
    for category in categories:
        category_dict = {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
        data.append(category_dict)
    return jsonify(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=data)


@bp_admin.route('/category', methods=['POST'])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('分类创建成功', 'success')
        return jsonify(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS)
    return jsonify(code=ResponseCode.FORM_VALIDATE_ERROR, message=form.errors)


@bp_admin.route('/category/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    category = Category.query.get_or_404(category_id)
    data = {
        'id': category.id,
        'name': category.name,
        'description': category.description
    }
    return jsonify(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=data)


@bp_admin.route('/category/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()

    if 'name' in data:
        category.name = data['name']
    if 'slug' in data:
        category.slug = data['slug']
    if 'description' in data:
        category.description = data['description']

    db.session.commit()
    return jsonify(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS)


@bp_admin.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS)
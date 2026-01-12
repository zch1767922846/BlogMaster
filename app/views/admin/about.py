from flask import render_template

from app.views.admin import bp_admin


@bp_admin.route('/about', methods=['GET'])
def admin_about_view():
    return render_template('admin/about.html')

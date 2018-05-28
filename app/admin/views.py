from . import admin
from .. import db
from flask_login import current_user, login_required, login_user
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from ..models import ApplyForBestPost, SystemMessage, Post, User
from ..decorators import admin_required, permission_required
from .forms import LoginForm


# TODO  处理管理员和协管员的登录
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(email=data['email']).first()
        if user is not None and user.verify_password(data['password']):
            login_user(user, remember=data['rememble_me'])
            next = request.args.get('next')
            if next is None or next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('无效的用户名或密码')

    return render_template('admin/login.html', form=form)


@admin.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/admin_info.html')


@admin.route('/best-post-applys')
@login_required
@admin_required
def best_post_applys():
    page = request.args.get('page', 1, type=int)
    pagination = ApplyForBestPost.query.order_by(ApplyForBestPost.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    best_post_applys = pagination.items
    return render_template('admin/best_post_applys.html', best_post_applys=best_post_applys, pagination=pagination)


@admin.route('/accept-best-post-apply/<int:id>')
@login_required
@admin_required
def accept_best_post_apply(id):
    post = Post.query.get_or_404(id)
    post.is_best = 1
    system_message = SystemMessage(
        body="你的帖子“" + post.title + "”已通过加精申请",
        to_user=post.user
    )
    db.session.add_all([post, system_message])
    db.session.commit()
    return redirect(url_for('main.best_post_applys'))



@admin.route('/refuse-best-post-apply/<int:id>')
@login_required
#注意添加管理员权限访问
def refuse_best_post_apply(id):
    post = Post.query.get_or_404(id)
    system_message = SystemMessage(
        body="很抱歉，你的帖子“" + post.title + "”未通过加精申请",
        to_user=post.user
    )
    db.session.add_all([post, system_message])
    db.session.delete(post.apply_for_best)
    db.session.commit()
    return redirect(url_for('main.best_post_applys'))
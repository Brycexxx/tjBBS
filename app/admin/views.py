from . import admin
from .. import db
from flask_login import current_user, login_required, login_user,logout_user
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from ..models import ApplyForBestPost, SystemMessage, Post, User, Permission
from ..decorators import admin_required, permission_required
from .forms import LoginForm, AdminDetailForm, PwdForm, AddModeratorForm, BulletinBoardForm
from werkzeug.utils import secure_filename
from app.main.views import change_filename
from werkzeug.security import generate_password_hash
import os


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(email=data['email']).first()
        if user.can(Permission.MODERATE):
            if user is not None and user.verify_password(data['password']):
                login_user(user)
                next = request.args.get('next')
                if next is None or next.startswith('/'):
                    next = url_for('admin.index')
                return redirect(next)
            else:
                flash("无效的账户或密码")
        else:
            flash('你没有登录权限')

    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin.route('/')
@login_required
@permission_required(Permission.MODERATE)
def index():
    form = AdminDetailForm()
    form.avatar.validators = []
    if request.method == 'GET':
        # 显示用户原本的信息
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.location.data = current_user.location
        form.info.data = current_user.about_me
    if form.validate_on_submit():
        data = form.data
        if form.avatar.data != "":
            file_avatar = secure_filename(form.avatar.data.filename)
            if not os.path.exists(current_app.config['FC_DIR']):
                os.mkdir(current_app.config['FC_DIR'])
                os.chmod(current_app.config['FC_DIR'])
            current_user.avatar = change_filename(file_avatar)
            form.avatar.data.save(current_app.config['FC_DIR'] + current_user.avatar)

        username_count = User.query.filter_by(username=data['username']).count()
        if data['username'] != current_user.username and username_count == 1:
            flash("昵称已经存在！")
            return redirect(url_for('admin.userinfo'))

        # 保存
        current_user.username = data['username']
        current_user.email = data['email']
        current_user.about_me = data['info']
        current_user.location = data['location']
        db.session.add(current_user)
        db.session.commit()
        flash("修改成功！")
        return redirect(url_for('admin.userinfo'))
    return render_template('admin/admin_info.html', form=form)


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
    return redirect(url_for('admin.best_post_applys'))



@admin.route('/refuse-best-post-apply/<int:id>')
@login_required
@admin_required
def refuse_best_post_apply(id):
    post = Post.query.get_or_404(id)
    system_message = SystemMessage(
        body="很抱歉，你的帖子“" + post.title + "”未通过加精申请",
        to_user=post.user
    )
    db.session.add_all([post, system_message])
    db.session.delete(post.apply_for_best)
    db.session.commit()
    return redirect(url_for('admin.best_post_applys'))

@admin.route('/edit-pwd/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def edit_pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        if not current_user.verify_password(data['old_pwd']):
            flash("旧密码错误！")
            return redirect(url_for('main.edit_pwd'))
        current_user.password_hash = generate_password_hash(data['new_pwd'])
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("密码修改成功，请重新登录！")
        return redirect(url_for('auth.logout'))
    return render_template('admin/edit_pwd.html', form=form)


@admin.route('/add-moderator', methods=['GET', 'POST'])
@login_required
@admin_required
def add_moderator():
    form = AddModeratorForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("该用户不存在，请重新输入帐号")
            return redirect(url_for('admin.add_moderator'))
        user.role_id = 3
        db.session.add(user)
        db.session.commit()
        flash("添加成功")
        return redirect(url_for('admin.add_moderator'))
    return render_template('admin/add_moderator.html', form=form)

@admin.route('/verify-post')
@login_required
@permission_required(Permission.MODERATE)
def verify_post():
    return render_template('admin/verify_post.html')

@admin.route('/post-bulletin', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def post_bulletin():
    form = BulletinBoardForm()
    if form.validate_on_submit():
        bulletin = SystemMessage(body=form.message.data)
        db.session.add(bulletin)
        db.session.commit()
        flash("公告发布成功")
        return redirect(url_for('admin.post_bulletin'))
    return render_template('admin/post_bulletin.html', form=form)



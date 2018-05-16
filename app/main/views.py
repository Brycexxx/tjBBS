from . import main
from .. import db
from ..models import User, Category, IdleItems, Comment, ReplyToComment, Collection
from .forms import PostForm, SearchForm, ReplyToCommentForm, UserDetailForm, PwdForm
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from uuid import uuid4
from sqlalchemy import or_
import json, re, os


def drop_html(html_body):
    pattern = re.compile(r'<[^>]+>', re.S)
    body = pattern.sub('', html_body)
    return body

def change_filename(filename):
    fileinfo = os.path.split(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + \
                str(uuid4().hex) + fileinfo[-1]
    return filename


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = IdleItems.query.order_by(IdleItems.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', pagination=pagination, posts=posts)

@main.route('/user/<int:id>')
def user(id):
    user = User.query.get_or_404(id)
    return render_template('user.html', user=user)

@main.route('/userinfo/', methods=['GET', 'POST'])
@login_required
def userinfo():
    form = UserDetailForm()
    form.avatar.validators = []
    if request.method == 'GET':
        # 显示用户原本的信息
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.info.data = current_user.about_me
    if form.validate_on_submit():
        data = form.data
        if form.avatar.data != "":
            file_avatar = secure_filename(form.avatar.data.filename)
            if not os.path.exists(current_app.config['FC_DIR']):
                os.mkdir(current_app.config['FC_DIR'])
                os.chmod(current_app.config['FC_DIR'])
            user.avatar = change_filename(file_avatar)
            form.avatar.data.save(current_app.config['FC_DIR'] + user.avatar)

        username_count = User.query.filter_by(username=data['username']).count()
        if data['username'] != user.username and username_count == 1:
            flash("昵称已经存在！")
            return redirect(url_for('main.userinfo'))

        # 保存
        current_user.username = data['username']
        current_user.email = data['email']
        current_user.about_me = data['info']
        flash("修改成功！")
        return redirect(url_for('main.userinfo'))
    return render_template('users/userinfo.html', form=form)

@main.route('/edit-pwd/', methods=['GET', 'POST'])
@login_required
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
    return render_template('users/edit_pwd.html', form=form)


@main.route('/follows')
@login_required
def follows():
    return


@main.route('/posts')
@login_required
def idle_items():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.idle_items.order_by(IdleItems.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    idle_items = pagination.items
    return render_template('users/idle_items.html', posts=idle_items, pagination=pagination)

@main.route('/collected-posts')
@login_required
def collected_idle_items():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.collections.order_by(Collection.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    collected_idle_items = pagination.items
    return render_template('users/collected_idle_items.html', posts=collected_idle_items, pagination=pagination)


@main.route('/post', methods=['GET', 'POST'])
@login_required
def post_idle_item():
    form = PostForm()
    if form.validate_on_submit():
        data = form.data
        idle_item = IdleItems(
            title=data['title'],
            descriptions=drop_html(request.form['content']),
            category=Category.query.get(data['category']),
            user=current_user
        )
        db.session.add(idle_item)
        db.session.commit()
        flash("您的帖子已发布！")
        return redirect(url_for('main.index'))
    return render_template('post.html', form=form)


@main.route('/search/<int:page>/')
def search(page):
    args = eval(json.dumps(request.args))
    if args['object'] == '帖子':
        idle_items_count = IdleItems.query.filter(
            or_(IdleItems.title.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '',
                IdleItems.descriptions.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '')
        ).count()
        pagination = IdleItems.query.filter(
            or_(IdleItems.title.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '',
                IdleItems.descriptions.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '')
        ).order_by(IdleItems.add_time.desc()).paginate(page=page, per_page=current_app.config['PER_PAGE'],
                                                       error_out=False)
        posts = pagination.items
        return render_template('search.html', idle_items_count=idle_items_count, pagination=pagination, posts=posts,
                               args=args)
    else:
        users_count = User.query.filter(User.username.ilike('%' + args['keyword'] + '%')).count()
        pagination = User.query.filter(User.username.ilike('%' + args['keyword'] + '%')). \
            order_by(User.last_seen.desc()).paginate(page=page, per_page=current_app.config['PER_PAGE'],
                                                     error_out=False)
        posts = pagination.items
        return render_template('search.html', users_count=users_count, args=args, pagination=pagination, posts=posts)


@main.route('/post/<int:id>/', methods=['GET', 'POST'])
def idle_item(id):
    form = ReplyToCommentForm()
    idle_item = IdleItems.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    if request.args.get('reply_comment_id', None):
        reply_comment_id = request.args.get('reply_comment_id')
        reply_comment = Comment.query.get_or_404(reply_comment_id)
    idle_item.view_times += 1
    db.session.add(idle_item)
    db.session.commit()
    if request.method == 'POST' and 'reply_comment_id' not in request.args:
        comment_body = drop_html(request.form['content'])
        if comment_body:
            comment = Comment(body=comment_body, idle_item=idle_item, user=current_user._get_current_object())
            db.session.add(comment)
            db.session.commit()
            flash("您的评论已发布")
            return redirect(url_for('main.idle_item', id=idle_item.id, page=-1))
        else:
            flash("请输入描述内容！")
    if form.validate_on_submit():
        data = form.data
        reply_to_comment = ReplyToComment(body=data['reply'], comment=reply_comment,
                                          user=current_user._get_current_object())
        db.session.add(reply_to_comment)
        db.session.commit()
        return redirect(url_for('main.idle_item', id=idle_item.id, page=page))
    if page == -1:
        page = (idle_item.comments.count() - 1) // current_app.config['PER_PAGE'] + 1
    pagination = idle_item.comments.order_by(Comment.add_time.asc()).paginate(
        page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    comments = pagination.items
    length = len(comments)
    return render_template('post_details.html', post=idle_item, comments=comments,
                           pagination=pagination, length=length, form=form, page=page)


@main.route('/follow/<username>')
@login_required
def follow(username):
    return


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    return


@main.route('/add/<username>')
@login_required
def add_friends(username):
    return


@main.route('/collect/<int:id>')
@login_required
def collect(id):
    idle_item = IdleItems.query.get_or_404(id)
    current_user.collect(idle_item)
    db.session.commit()
    flash("您已经成功收藏该帖！")
    return redirect(url_for('main.idle_item', id=idle_item.id))


@main.route('/uncollect/<int:id>')
@login_required
def cancel_collect(id):
    idle_item = IdleItems.query.get_or_404(id)
    current_user.cancel_collect(idle_item)
    db.session.commit()
    flash("您已经取消收藏！")
    return redirect(url_for('main.idle_item', id=idle_item.id))


@main.route('/del-post/<int:id>')
@login_required
def del_post(id):
    idle_item = IdleItems.query.get_or_404(id)
    db.session.delete(idle_item)
    db.session.commit()
    return redirect(url_for('main.idle_items'))

@main.route('/del-collected-post/<int:id>')
@login_required
def del_collected_post(id):
    collected_idle_item = Collection.query.filter_by(collected_idle_item_id=id).first()
    db.session.delete(collected_idle_item)
    db.session.commit()
    return redirect(url_for('main.collected_idle_items'))

@main.route('/del-comment/<int:id>')
@login_required
def del_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = request.args.get('post_id')
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.idle_item', id=post_id))


@main.route('/del-replycomment/<int:id>')
@login_required
def del_rep_comment(id):
    reply_comment = ReplyToComment.query.get_or_404(id)
    post_id = request.args.get('post_id')
    db.session.delete(reply_comment)
    db.session.commit()
    return redirect(url_for('main.idle_item', id=post_id))

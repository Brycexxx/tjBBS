from . import main
from .. import db
from ..models import User, Category, Post, Comment, ReplyToComment, Collection, Follow
from .forms import PostForm, ReplyToCommentForm, UserDetailForm, PwdForm
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['IMAGE_EXTENSIONS']

def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.utcnow().strftime("%Y%m%d%H%M%S") + \
                str(uuid4().hex) + fileinfo[-1]
    return filename

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', pagination=pagination, posts=posts)

@main.route('/user/<int:id>')
def user(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)

@main.route('/userinfo/', methods=['GET', 'POST'])
@login_required
def userinfo():
    form = UserDetailForm()
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
            return redirect(url_for('main.userinfo'))

        # 保存
        current_user.username = data['username']
        current_user.email = data['email']
        current_user.about_me = data['info']
        current_user.location = data['location']
        db.session.add(current_user)
        db.session.commit()
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



@main.route('/posts')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.posts.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('users/posts.html', posts=posts, pagination=pagination)

@main.route('/collected-posts')
@login_required
def collected_posts():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.collections.order_by(Collection.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    collected_posts = pagination.items
    return render_template('users/collected_posts.html', posts=collected_posts, pagination=pagination)

@main.route('/upload-image', methods=['GET', 'POST'])
@login_required
def upload_image():
    image = request.files['file']
    if image and allowed_file(image.filename):
        image_name = secure_filename(image.filename)
        secure_imgname = change_filename(image_name)
        success = '{"error": false, "url":"http:\/\/localhost:5000\/static\/uploads\/posts\/' + secure_imgname + '"}'
        image.save(os.path.join(current_app.config['POST_DIR'], secure_imgname))
        return success
    else:
        error = '{"error": true}'
        return error

@main.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        data = form.data
        post = Post(
            title=data['title'],
            descriptions=request.form['content'],
            category=Category.query.get(data['category']),
            user=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("您的帖子已发布！")
        return redirect(url_for('main.index'))
    return render_template('post.html', form=form)


@main.route('/search/<int:page>/')
def search(page):
    args = eval(json.dumps(request.args))
    if args['object'] == 'post':
        posts_count = Post.query.filter(
            or_(Post.title.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '',
                Post.descriptions.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '')
        ).count()
        pagination = Post.query.filter(
            or_(Post.title.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '',
                Post.descriptions.ilike('%' + args['keyword'] + '%') if args['keyword'] is not None else '')
        ).order_by(Post.add_time.desc()).paginate(page=page, per_page=current_app.config['PER_PAGE'],
                                                   error_out=False)
        posts = pagination.items
        return render_template('search.html', counts=posts_count, pagination=pagination, posts=posts,
                               args=args)
    else:
        users_count = User.query.filter(User.username.ilike('%' + args['keyword'] + '%')).count()
        pagination = User.query.filter(User.username.ilike('%' + args['keyword'] + '%')). \
            order_by(User.last_seen.desc()).paginate(page=page, per_page=current_app.config['PER_PAGE'],
                                                     error_out=False)
        posts = pagination.items
        return render_template('search.html', counts=users_count, args=args, pagination=pagination, posts=posts)


@main.route('/post-detail/<int:id>/', methods=['GET', 'POST'])
def post_detail(id):
    form = ReplyToCommentForm()
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    if request.args.get('reply_comment_id', None):
        reply_comment_id = request.args.get('reply_comment_id')
        reply_comment = Comment.query.get_or_404(reply_comment_id)
    post.view_times += 1
    db.session.add(post)
    db.session.commit()
    if request.method == 'POST' and 'reply_comment_id' not in request.args:
        comment_body = request.form['content']
        if comment_body:
            comment = Comment(body=comment_body, post=post, user=current_user._get_current_object())
            db.session.add(comment)
            db.session.commit()
            flash("您的评论已发布")
            return redirect(url_for('main.post_detail', id=post.id, page=-1))
        else:
            flash("请输入描述内容！")
    if form.validate_on_submit():
        data = form.data
        reply_to_comment = ReplyToComment(body=data['reply'], comment=reply_comment,
                                          user=current_user._get_current_object())
        db.session.add(reply_to_comment)
        db.session.commit()
        return redirect(url_for('main.post_detail', id=post.id, page=page))
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.add_time.asc()).paginate(
        page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    comments = pagination.items
    length = len(comments)
    return render_template('post_details.html', post=post, comments=comments,
                           pagination=pagination, length=length, form=form, page=page)


@main.route('/follow/<int:id>')
@login_required
def follow(id):
    user = User.query.get_or_404(id)
    if current_user.is_following(user):
        flash("您已经关注该用户了")
        return redirect(url_for('main.user', id=id))
    current_user.follow(user)
    flash("您成功地关注了%s" % user.username)
    return redirect(url_for('main.user', id=id))


@main.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user = User.query.get_or_404(id)
    if not current_user.is_following(user):
        flash("您还没关注该用户")
        return redirect(url_for('main.user', id=id))
    current_user.unfollow(user)
    flash("您取消了关注%s" % user.username)
    return redirect(url_for('main.user', id=id))


@main.route('/followers/<int:id>')
@login_required
def followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    follows = [{'user': item.followed, 'add_time': item.add_time}
               for item in pagination.items]
    if current_user == user:
        template_html = 'users/follows.html'
    else:
        template_html = 'follows.html'
    return render_template(template_html, user=user, pagination=pagination,
                           follows=follows, title='关注了谁', endpoint='main.followers')

@main.route('/followed_by/<int:id>')
@login_required
def followed_by(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    follows = [{'user': item.follower, 'add_time': item.add_time}
               for item in pagination.items]
    if current_user == user:
        template_html = 'users/follows.html'
    else:
        template_html = 'follows.html'
    return render_template(template_html, user=user, pagination=pagination,
                           follows=follows, title='的粉丝',endpoint='main.followed_by')

@main.route('/collect/<int:id>')
@login_required
def collect(id):
    post = Post.query.get_or_404(id)
    current_user.collect(post)
    db.session.commit()
    flash("您已经成功收藏该帖！")
    return redirect(url_for('main.post_detail', id=post.id))


@main.route('/uncollect/<int:id>')
@login_required
def cancel_collect(id):
    post = Post.query.get_or_404(id)
    current_user.cancel_collect(post)
    db.session.commit()
    flash("您已经取消收藏！")
    return redirect(url_for('main.idle_item', id=post.id))


@main.route('/del-post/<int:id>')
@login_required
def del_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('main.posts'))

@main.route('/del-collected-post/<int:id>')
@login_required
def del_collected_post(id):
    collected_post = Collection.query.filter_by(collected_post_id=id).first()
    db.session.delete(collected_post)
    db.session.commit()
    return redirect(url_for('main.collected_posts'))

@main.route('/del-comment/<int:id>')
@login_required
def del_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = request.args.get('post_id')
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.post_detail', id=post_id))


@main.route('/del-replycomment/<int:id>')
@login_required
def del_rep_comment(id):
    reply_comment = ReplyToComment.query.get_or_404(id)
    post_id = request.args.get('post_id')
    db.session.delete(reply_comment)
    db.session.commit()
    return redirect(url_for('main.post_detail', id=post_id))

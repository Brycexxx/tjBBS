from . import main
from .. import db
from ..models import User, Category, Post, Comment, ReplyToComment, Collection, Follow, MessageBoard, ApplyForBestPost, \
    SystemMessage
from .forms import PostForm, ReplyToCommentForm, UserDetailForm, PwdForm, MessageForm
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from uuid import uuid4
from sqlalchemy import or_
import re, os, hashlib
from ..uploaded_content_verify import ContentVerify


def drop_html(html_body):
    pattern = re.compile(r'<[^>]+>', re.S)
    body = pattern.sub('', html_body)
    return body

def match_src(html_body):
    pattern = re.compile(r'src="(http.+?)"', re.S)
    match_result = pattern.search(html_body)
    img_link = match_result.groups(1)[0]
    return img_link

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
    all_query_results = []
    for i in range(1, len(Category.query.all()) + 1):
        query = Post.query.filter(Post.category_id == i, Post.check == 1)
        all_query_results.append(query.order_by(Post.add_time.desc()).limit(5).all())
    all_query_results.append(Post.query.filter_by(is_best=1, check=1).order_by(Post.view_times.desc()).limit(5).all())
    all_query_results.append(Post.query.filter_by(check=1).order_by(Post.view_times.desc()).limit(5).all())
    all_query_results.append(Post.query.filter_by(check=1).order_by(Post.add_time.desc()).limit(5).all())
    all_query_results.append(SystemMessage.query.filter_by(to_user_id=None).first())
    return render_template('index.html', all_posts=all_query_results)


@main.route('/hot')
def hot():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.view_times.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "热门"
    endpoint = "main.hot"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)


@main.route('/new')
def new():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "最新发布"
    endpoint = "main.new"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)


@main.route('/best')
def best():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(is_best=1).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "精华"
    endpoint = "main.best"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)


@main.route('/book')
def book():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=9).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "书籍资料"
    endpoint = "main.book"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)


@main.route('/transport')
def transport():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=7).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "交通工具"
    endpoint = "main.transport"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/card')
def card():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=6).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "卡，票，券"
    endpoint = "main.card"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/electronic')
def electronic():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=3).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "数码电子"
    endpoint = "main.electronic"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/clothes')
def clothes():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=8).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "服装鞋包"
    endpoint = "main.electronic"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/daily')
def daily():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=4).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "生活用品"
    endpoint = "main.daily"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)


@main.route('/sport')
def sport():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=5).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "运动装备"
    endpoint = "main.sport"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/buy')
def buy():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=2).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "求购"
    endpoint = "main.buy"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/communication')
def communication():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=1).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "交流"
    endpoint = "main.communication"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/finished')
def finished():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=11).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "已售/已购"
    endpoint = "main.finished"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/others')
def others():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=10).order_by(Post.add_time.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    posts = pagination.items
    title = "其他"
    endpoint = "main.others"
    return render_template('posts_list.html', pagination=pagination, posts=posts, title=title, endpoint=endpoint)

@main.route('/user/<int:id>', methods=['GET', 'POST'])
def user(id):
    form = MessageForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        if current_user.is_anonymous:
            return redirect(url_for('auth.login'))

        message_board = MessageBoard(body=form.message.data,
                                     send_user=current_user._get_current_object(),
                                     receive_user=user)
        db.session.add(message_board)
        db.session.commit()
        flash("留言成功", 'ok')
        form.message.data = ""
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination, form=form)


@main.route('/userinfo/', methods=['GET', 'POST'])
@login_required
def userinfo():
    form = UserDetailForm()
    form.avatar.validators = []
    if request.method == 'GET':
        # 显示用户原本的信息
        form.username.data = current_user.username
        form.location.data = current_user.location
        form.info.data = current_user.about_me
    if form.validate_on_submit():
        data = form.data
        if data["avatar"] != "":
            avatar_verify = ContentVerify()
            verify_msg, ok_or_not = avatar_verify.verify_uploaded_avatar(data["avatar"])
            if not ok_or_not:
                flash(verify_msg, 'avatar_error')
                return redirect(url_for('main.userinfo'))
            data["avatar"].seek(0, 0)
            file_avatar = secure_filename(form.avatar.data.filename)
            if not os.path.exists(current_app.config['FC_DIR']):
                os.mkdir(current_app.config['FC_DIR'])
                os.chmod(current_app.config['FC_DIR'])
            current_user.avatar = change_filename(file_avatar)
            form.avatar.data.save(current_app.config['FC_DIR'] + current_user.avatar)

        username_count = User.query.filter_by(username=data['username']).count()
        if data['username'] != current_user.username and username_count == 1:
            flash("昵称已经存在！", 'username_error')
            return redirect(url_for('main.userinfo'))

        # 保存
        current_user.username = data['username']
        current_user.about_me = data['info']
        current_user.location = data['location']
        db.session.add(current_user)
        db.session.commit()
        flash("修改成功！", 'ok')
        return redirect(url_for('main.userinfo'))
    return render_template('users/userinfo.html', form=form)


@main.route('/edit-pwd/', methods=['GET', 'POST'])
@login_required
def edit_pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        if not current_user.verify_password(data['old_pwd']):
            flash("旧密码错误！", 'error')
            return redirect(url_for('main.edit_pwd'))
        current_user.password_hash = generate_password_hash(data['new_pwd'])
        form.old_pwd.data = ''
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("密码修改成功，请重新登录！", 'ok')
        return redirect(url_for('auth.logout'))
    return render_template('users/edit_pwd.html', form=form)


@main.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.receive_messages.order_by(MessageBoard.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    messages = pagination.items
    return render_template('users/messages.html', messages=messages, pagination=pagination)


@main.route('/system-messages')
@login_required
def system_messages():
    page = request.args.get('page', 1, type=int)
    pagination = SystemMessage.query.filter_by(to_user_id=current_user.id). \
        order_by(SystemMessage.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    messages = pagination.items
    return render_template('users/system_messages.html', system_messages=messages, pagination=pagination)


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
    content_verify = ContentVerify()
    verify_msg, ok_or_not = content_verify.verify_uploaded_images(image)
    image.seek(0, 0)
    if image and allowed_file(image.filename) and ok_or_not:
        image_name = secure_filename(image.filename)
        secure_imgname = change_filename(image_name)
        success = '{"url":"http:\/\/'+ current_app.config['URL'] +'\/static\/uploads\/posts\/' + secure_imgname + '"}'
        image.save(os.path.join(current_app.config['POST_DIR'], secure_imgname))
        return success
    else:
        if isinstance(verify_msg[0], dict):
            verify_msg = "图片超出限制，审核失败！"
        elif not allowed_file(image.filename):
            verify_msg = "图片格式错误，上传失败！"
        else:
            verify_msg = verify_msg[0] + "，上传失败！"
        error = '{"error": "' + verify_msg + '"}'
        return error

@main.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    try:
        if request.form['content'] != "" and not form.validate_on_submit():
            flash("标题不能为空！", 'title_error')
            return redirect(url_for('main.post'))
    except:
        pass
    if form.validate_on_submit():
        content_verify = ContentVerify()
        if request.form['content'] == "":
            flash("内容不能为空！", 'error')
            return redirect(url_for('main.post'))
        try:
            img_link = match_src(request.form['content'])
            verify_msg, ok_or_not = content_verify.verify_uploaded_images(img_link)
            if not ok_or_not:
                flash(verify_msg[0] + "，提交失败！", 'error')
                return redirect(url_for('main.post'))
            else:
                pass
        except AttributeError:
            print("用户上传的内容中不包含图片链接！")
        text = request.form['content']
        msg, spam_code, ok_or_not = content_verify.verify_text(text)
        if not ok_or_not:
            if spam_code == 1:
                flash(msg, 'error')
                return redirect(url_for('main.post'))
            else:
                flash(msg, 'error')
                check = 0
        else:
            check = 1
        data = form.data
        post = Post(
            title=data['title'],
            descriptions=text,
            category=Category.query.get(data['category']),
            check=check,
            user=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        if check == 1:
            flash("您的帖子已发布！", 'ok')
        return redirect(url_for('main.post'))
    return render_template('post.html', form=form)


@main.route('/search/<int:page>/')
def search(page):
    keyword = request.args.get('keyword')
    count = []
    items = []
    # 查询帖子
    posts_query = Post.query.filter(
        or_(Post.title.ilike('%' + keyword + '%') if keyword is not None else '',
            Post.descriptions.ilike('%' + keyword + '%') if keyword is not None else '')
    )
    posts_count = posts_query.count()
    count.append(posts_count)
    posts_pagination = posts_query.order_by(Post.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False)
    items.append(posts_pagination.items)
    # 查询用户
    users_query = User.query.filter(User.username.ilike('%' + keyword + '%'))
    users_count = users_query.count()
    count.append(users_count)
    users_pagination = users_query.order_by(User.last_seen.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False)
    items.append(users_pagination.items)

    if posts_count > users_count:
        pagination = posts_pagination
    else:
        pagination = users_pagination
    return render_template('search.html', count=count, keyword=keyword, pagination=pagination, items=items)


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

    # 对帖子发布评论
    if request.method == 'POST' and 'reply_comment_id' not in request.args:
        if not current_user.is_anonymous:
            comment_body = request.form['content']
            if comment_body:
                comment = Comment(body=comment_body, post=post, user=current_user._get_current_object())
                db.session.add(comment)
                db.session.commit()
                flash("您的评论已发布", 'ok')
                return redirect(url_for('main.post_detail', id=post.id, page=-1))
            else:
                flash("请输入评论内容！", 'comment_error')
                return redirect(url_for('main.post_detail', id=post.id, page=-1))
        else:
            return redirect(url_for('auth.login'))

    # 回复帖子的评论
    if form.validate_on_submit():
        if not current_user.is_anonymous:
            data = form.data
            reply_to_comment = ReplyToComment(body=data['reply'], comment=reply_comment,
                                              user=current_user._get_current_object())
            db.session.add(reply_to_comment)
            db.session.commit()
            return redirect(url_for('main.post_detail', id=post.id, page=page))
        else:
            return redirect(url_for('auth.login'))
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
                           follows=follows, title='的粉丝', endpoint='main.followed_by')


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
    return redirect(url_for('main.post_detail', id=post.id))


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


@main.route('/del-messages/<int:id>')
@login_required
def del_message(id):
    message = MessageBoard.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('main.messages'))


@main.route('/del-system-message/<int:id>')
@login_required
def del_system_message(id):
    message = SystemMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('main.system_messages'))


@main.route('/apply-for-best/<int:id>')
@login_required
def apply_for_best(id):
    post = Post.query.get_or_404(id)
    apply_for_best = ApplyForBestPost(
        post=post,
        user=current_user._get_current_object()
    )
    db.session.add(apply_for_best)
    db.session.commit()
    flash("已发出申请，请等待审核")
    return redirect(url_for('main.posts'))

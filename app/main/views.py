from . import main
from .. import db
from ..models import User, Category, IdleItems, Comment
from .forms import PostForm, SearchForm
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from sqlalchemy import or_
import json
import re


def drop_html(html_body):
    pattern = re.compile(r'<[^>]+>', re.S)
    body = pattern.sub('', html_body)
    return body


@main.route('/')
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    pagination = IdleItems.query.order_by(IdleItems.add_time.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, pagination=pagination, posts=posts)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


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


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def idle_item(id):
    idle_item = IdleItems.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    idle_item.view_times += 1
    db.session.add(idle_item)
    db.session.commit()
    if request.method == 'POST':
        comment_body = drop_html(request.form['content'])
        if comment_body:
            comment = Comment(body=comment_body, idle_item=idle_item, user=current_user._get_current_object())
            db.session.add(comment)
            db.session.commit()
            flash("您的评论已发布")
            return redirect(url_for('main.idle_item', id=idle_item.id, page=-1))
        else:
            flash("请输入描述内容！")
    if page == -1:
        page = (idle_item.comments.count() - 1) // current_app.config['PER_PAGE'] + 1
    pagination = idle_item.comments.order_by(Comment.add_time.asc()).paginate(
        page, per_page=current_app.config['PER_PAGE'], error_out=False
    )
    comments = pagination.items
    return render_template('post_details.html', post=idle_item, comments=comments, pagination=pagination)


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


@main.route('/collections')
@login_required
def my_collections():
    return

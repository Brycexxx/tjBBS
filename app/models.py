from . import db, login_manager
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


class Permission:
    USER = 1
    MODERATE = 2
    ADMIN = 4


class Collection(db.Model):
    __tablename__ = "collections"
    collecting_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    collected_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)


class MessageBoard(db.Model):
    __tablename__ = "messageboard"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    send_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "<Message %r to %r>" % (self.send_user, self.to_user)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(128))
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    reply_comments = db.relationship('ReplyToComment',  backref='user', lazy='dynamic')
    apply_for_best_posts = db.relationship('ApplyForBestPost', backref='user', lazy='dynamic')
    system_messages = db.relationship('SystemMessage', backref='to_user', lazy='dynamic')
    send_messages = db.relationship('MessageBoard', foreign_keys=[MessageBoard.send_user_id], backref='send_user', lazy='dynamic')
    receive_messages = db.relationship('MessageBoard', foreign_keys=[MessageBoard.to_user_id], backref='receive_user', lazy='dynamic')
    collections = db.relationship('Collection', foreign_keys=[Collection.collecting_user_id],
                                  backref=db.backref('collecting_user', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['TJ_ADMIN']:
                self.role = Role.query.filter_by(name='ADMIN').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('不可读取密码！')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')  # 解码之前是字节型数据，解码后是字符串类型

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data['confirm'] == self.id:
            self.confirmed = True
            db.session.add(self)
            return True

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def collect(self, post):
        if not self.is_collecting(post):
            c = Collection(collected_post=post, collecting_user=self)
            db.session.add(c)
            db.session.commit()

    def cancel_collect(self, post):
        collection = self.collections.filter_by(collected_post_id=post.id).first()
        if collection:
            db.session.delete(collection)
            db.session.commit()

    def is_collecting(self, post):
        if post.id is None:
            return False
        return self.collections.filter_by(
            collected_post_id=post.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user, follower=self)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            f = Follow.query.filter_by(followed_id=user.id).first()
            if f:
                db.session.delete(f)
                db.session.commit()

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(follower_id=user.id).first() is not None

    def __repr__(self):
        return "<User: %r>" % (self.username)


class AnonymousUser(AnonymousUserMixin):

    def is_admin(self):
        return False

    def is_collecting(self, post):
        return False

    def is_following(self, user):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    permission = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __int__(self, **kwargs):
        super(Role, self).__int__(**kwargs)
        if self.permission is None:
            self.permission = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.USER],
            'Moderate': [Permission.USER, Permission.MODERATE],
            'Admin': [Permission.USER, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def reset_permission(self):
        self.permission = 0

    def add_permission(self, perm):
        self.permission += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permission -= perm

    def has_permission(self, perm):
        return self.permission & perm == perm

    def __repr__(self):
        return "<Role: %r>" % self.name

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    descriptions = db.Column(db.Text)
    images = db.Column(db.String(128))
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_best = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    view_times = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    apply_for_best = db.relationship('ApplyForBestPost', backref='post', uselist=False)
    users = db.relationship('Collection', foreign_keys=[Collection.collected_post_id],
                            backref=db.backref('collected_post', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return '<IdleItems: %r>' % self.id


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    replys = db.relationship('ReplyToComment', backref='comment', lazy='dynamic')

    def __repr__(self):
        return "<Comment to: %r>" % self.post.title


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    @staticmethod
    def insert_categories():
        categories = ['数码', '日用', '书籍', '影音', '鞋服', '其他']
        for c in categories:
            if not Category.query.filter_by(name=c).first():
                category = Category(name=c)
                db.session.add(category)
        db.session.commit()

    def __repr__(self):
        return '<Category: %r>' % self.name


class ReplyToComment(db.Model):
    __tablename__ = "replys_to_comment"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    add_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<ReplyTo Comment %r>" % self.comment_id

class ApplyForBestPost(db.Model):
    __tablename__ = "apply_for_best_posts"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    add_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<%r apply for best post>" % self.post.title

class SystemMessage(db.Model):
    __tablename__ = "system_messages"
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(256))

    def __repr__(self):
        return "<Some System Messages to %r>" % self.to_user.username
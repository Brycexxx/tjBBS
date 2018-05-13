from . import db, login_manager
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 3
    ADMIN = 4


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
    member_since = db.Column(db.DateTime, default=datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    idle_items = db.relationship('IdleItems', backref='user', lazy='dynamic')


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
        return s.dumps({'confirm': self.id}).decode('utf-8') # 解码之前是字节型数据，解码后是字符串类型

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


    def is_admin(self):
        return (self.role_id == 2)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def __repr__(self):
        return "<User: %r>" % (self.username)

class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
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

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Admin': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.ADMIN]
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


    def __repr__(self):
        return "<Role: %r>" % self.name

class IdleItems(db.Model):
    __tablename__ = 'idle_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    descriptions = db.Column(db.Text)
    images = db.Column(db.String(128))
    add_time = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    view_times = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='idle_item', lazy='dynamic')


    def __repr__(self):
        return '<IdleItems: %r>' % self.id

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.now)
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    idle_item_id = db.Column(db.Integer, db.ForeignKey('idle_items.id'))


    def __repr__(self):
        return "<Comment to: %r>" % self.idle_item.title


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    idle_items = db.relationship('IdleItems', backref='category', lazy='dynamic')

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



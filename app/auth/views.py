from . import auth
from flask import render_template, flash, redirect, url_for, request
from .forms import LoginForm, RegisterForm, PwdResetForm, PwdResetRequestForm
from ..models import User, Role
from .. import db
from ..email import send_email
from flask_login import current_user, login_required, login_user, logout_user

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
        and request.endpoint != 'static' \
        and request.blueprint != 'auth':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print('test')
        data = form.data
        user = User(username=data['username'],
                    email=data['email'],
                    password=data['password'])
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '请确认你的帐号', 'auth/email/confirm',
                   user=user, token=token)
        flash('确认邮件已经发送到你的邮箱，请登录后再进行验证！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您的账户已被确认，谢谢！')
    else:
        flash('认证链接已失效！')
    return redirect(url_for('main.index'))


@auth.route('/auth/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/auth/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '账户认证', 'auth/email/confirm',
               user=current_user, token=token)
    flash('认证邮件已经重新发送到您的邮箱！')
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['POST', 'GET'])
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
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/reset-password', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PwdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            flash("重置密码邮件已经发送到你的邮箱")
            return redirect(url_for('auth.login'))
        else:
            flash("无效的邮箱，请重新输入")
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PwdResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("你的密码已经重置，请登录")
            return redirect(url_for('auth.login'))
        else:
            flash("密码重置失败，请重试")
            return redirect(url_for('auth.password_reset_request'))
    return render_template('auth/reset_password.html', form=form)
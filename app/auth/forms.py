from flask_wtf import FlaskForm
from ..models import User
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField

class LoginForm(FlaskForm):
    email = StringField('邮箱帐号', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    rememble_me = BooleanField('自动登录')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64),
                           Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]+$', 0,
                                  '应户名必须是汉字、字母、数字、点和下划线的英文名')])
    email = StringField('邮箱帐号', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='密码不一致，请重新输入！')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册了！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被占用！')

class PwdResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重置密码')

class PwdResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')
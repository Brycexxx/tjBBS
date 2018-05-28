from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email
from wtforms import StringField, PasswordField, SubmitField, BooleanField

class LoginForm(FlaskForm):
    email = StringField('邮箱帐号', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    rememble_me = BooleanField('自动登录')
    submit = SubmitField('登录')
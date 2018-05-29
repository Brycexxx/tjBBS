from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField

class LoginForm(FlaskForm):
    email = StringField('邮箱帐号', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class AdminDetailForm(FlaskForm):
    username = StringField(
        label="昵称",
        validators=[
            DataRequired("昵称不能为空！"),
            Length(1, 64),
            Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]+$', 0, '应户名必须是汉字、字母、数字、点和下划线的英文名')
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称！",
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱！",
        }
    )
    location = StringField(
        label="常住地",
        validators=[
            DataRequired("常住不能为空！")
        ],
        description="常住地",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入常住地！",
        }
    )
    avatar = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像",
    )
    info = TextAreaField(
        label="个性简介",
        validators=[
            DataRequired("简介不能为空！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success",
        }
    )

class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空！"),
            EqualTo('confirm_new_pwd', message='密码不一致，请重新输入！')
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }
    )
    confirm_new_pwd = PasswordField(
        label="确认新密码",
        validators=[
            DataRequired("请再输入一遍新密码！"),

        ],
        description="确认新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请确认新密码！",
        }
    )
    submit = SubmitField(
        label='修改密码',
        render_kw={
            "class": "btn btn-success",
        }
    )

class AddModeratorForm(FlaskForm):
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱！",
        }
    )
    submit = SubmitField(
        label='添加',
        render_kw={
            "class": "btn btn-success",
        }
    )
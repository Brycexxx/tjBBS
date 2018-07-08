from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms import SelectField, StringField, SubmitField, FileField, TextAreaField, PasswordField
from ..models import Category


class PostForm(FlaskForm):
    category = SelectField('请选择分类', coerce=int)
    title = StringField('请输入主题描述', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, **kwargs):
        super(PostForm, self).__init__(**kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.name).all()]


class SearchForm(FlaskForm):
    keyword = StringField('关键字',
                          validators=[DataRequired()],
                          render_kw={
                              'class': 'form-control',
                              'placeholder': '客官你想找什么？'
                          })
    object = SelectField('搜索对象', coerce=int, choices=[(1, '帖子'), (2, '用户')])
    search = SubmitField('搜索', render_kw={'class': 'btn btn-default'})


class ReplyToCommentForm(FlaskForm):
    reply = StringField('回复评论：', validators=[DataRequired("内容不能为空！")],
                        render_kw={
                            'class': 'reply-box-size'
                        })
    submit = SubmitField('发表', render_kw={'class': "btn btn-sm btn-primary"})


class UserDetailForm(FlaskForm):
    username = StringField(
        label="昵称",
        validators=[
            DataRequired("昵称不能为空！"),
            Length(1, 64),
            Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]+$', 0, '用户名必须是汉字、字母、数字、点和下划线的组合')
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称！",
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
            "class": "btn btn-system",
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
            "id": "clear",
            "class": "form-control",
            "placeholder": "请输入旧密码",
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
            "placeholder": "请输入新密码",
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
            "placeholder": "请确认新密码",
        }
    )
    submit = SubmitField(
        label='修改密码',
        render_kw={
            "class": "btn btn-system",
        }
    )

class MessageForm(FlaskForm):
    message = TextAreaField(
        label="留言板",
        validators=[DataRequired("留言不能为空！")],
        render_kw={
            "class": "form-control",
            "rows": 8
        }
    )
    submit = SubmitField(
        label="留言",
        render_kw={
            "class": "btn btn-system"
        }
    )
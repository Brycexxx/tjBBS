from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SelectField, StringField, SubmitField
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
    reply = StringField('回复评论：', validators=[DataRequired()],
                        render_kw={
                            'class': 'reply-box-size'
                        })
    submit = SubmitField('发表', render_kw={'class': "btn btn-sm btn-primary"})

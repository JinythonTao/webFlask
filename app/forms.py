from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名：', render_kw={"id": "name", "placeholder": "请输入用户名"}, validators=[DataRequired()])
    password = PasswordField('密码：', render_kw={"id": "name", "placeholder": "请输入密码"}, validators=[DataRequired()])
    remember_me = BooleanField('记住我：')
    submit = SubmitField('登 录')


# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('用户名：', validators=[DataRequired()])
    email = StringField('邮箱：', validators=[DataRequired(), Email()])
    password = PasswordField('密码：', validators=[DataRequired()])
    password2 = PasswordField(
        '确认密码：', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注 册')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名重复！')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱地址重复！')


# 用户编辑表单
class EditProfileForm(FlaskForm):
    username = StringField('用户名:', validators=[DataRequired()])
    location = StringField('地 址:', validators=[Length(min=0, max=140)])
    avatar = FileField('上传头像:', validators=[FileRequired(message='请选择文件')])
    about_me = TextAreaField('个人说明:', validators=[Length(min=0, max=140)])
    submit = SubmitField('保 存')
    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('用户名{}已存在，请更换其他名字~'.format(username))


# 发布动态表单
class PostForm(FlaskForm):
    post = TextAreaField('有什么新鲜事告诉大家?', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('发 表')


# 重置密码
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('邮箱地址', validators=[DataRequired(), Email()])
    submit = SubmitField('请求重置密码')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('密  码:', validators=[DataRequired()])
    password2 = PasswordField(
        '确认密码:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('提交保存')

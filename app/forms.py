from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
from wtforms import SubmitField
class RegisterForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm = PasswordField('Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp')])
    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class ProfileForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Ảnh đại diện', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Cập nhật')
class MessageForm(FlaskForm):
    content = TextAreaField('Nội dung tin nhắn', validators=[DataRequired(), Length(min=1, max=500)])
class FileUploadForm(FlaskForm):
    file = FileField('Tải lên tệp', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'docx'], 'Chỉ cho phép tệp ảnh và tài liệu!')])
    submit = SubmitField('Tải lên')
class FriendRequestForm(FlaskForm):
    submit = SubmitField('Gửi lời mời')
class UpdateProfileForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Ảnh đại diện', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Cập nhật')

class PostForm(FlaskForm):
    content = TextAreaField('Nội dung', validators=[DataRequired(), Length(min=1, max=1000)])
    image = FileField('Ảnh bài viết', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Đăng bài')

class LikeForm(FlaskForm):
    submit = SubmitField('❤️')

class CommentForm(FlaskForm):
    comment = StringField('Bình luận', validators=[DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Gửi')
class DummyForm(FlaskForm):
    pass
from operator import and_, or_
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import os
from flask_socketio import emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Call, db, User, Post, Comment, Like, Friendship, Message, comment_likes
from .forms import DummyForm, PostForm, CommentForm, FriendRequestForm, MessageForm, ProfileForm, RegisterForm, LoginForm, UpdateProfileForm
from app import oauth, socketio
from flask import current_app
from flask_login import login_user, logout_user
from sqlalchemy.orm import joinedload
from pytz import timezone, utc
import pytz

main = Blueprint('main', __name__)

# Đăng ký OAuth Google
google = oauth.register(
    name='google',
    client_id='xxxxxxxx',
    client_secret='ssssssssss',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'consent',
        'access_type': 'offline'
    }
)

@main.route('/')
@main.route('/home')
@login_required
def home():
    try:
        # Lấy top bài viết trong ngày
        top_daily_posts = Post.get_top_daily_posts()

        # Nếu không có bài nổi bật nào hôm nay, bỏ lọc like
        if top_daily_posts and top_daily_posts[0].get_daily_likes() > 0:
            top_ids = [p.id for p in top_daily_posts]
        else:
            top_ids = []

        # Lấy các bài viết khác (trừ bài đã hiển thị trong top)
        other_posts = Post.get_recent_posts_excluding(top_ids)

        # Gộp bài viết lại
        posts = top_daily_posts + other_posts

        # Chuyển created_at sang múi giờ Hà Nội
        tz_hanoi = timezone('Asia/Ho_Chi_Minh')
        for post in posts:
            if post.created_at:
                utc = pytz.utc
                if post.created_at.tzinfo is None:
                    post.created_at = utc.localize(post.created_at)
                post.created_at_hn = post.created_at.astimezone(tz_hanoi)
            else:
                post.created_at_hn = None
                current_app.logger.warning(f"Bài viết ID {post.id} không có giá trị created_at.")

        # Danh sách người dùng nổi bật
        top_users = User.query.order_by(User.total_hearts.desc()).limit(5).all()

        return render_template('home.html', posts=posts, top_users=top_users)

    except Exception as e:
        current_app.logger.error(f"Lỗi trang chủ: {str(e)}")
        flash('Đã xảy ra lỗi khi tải trang chủ.', 'danger')
        return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return redirect(url_for('main.register'))

        if existing_email:
            flash('Email đã được sử dụng. Vui lòng dùng email khác.', 'danger')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công! Mời bạn đăng nhập.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Sai email hoặc mật khẩu!', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/google/login')
def google_login():
    redirect_uri = url_for('main.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@main.route('/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
    except Exception as e:
        flash('Xác thực Google thất bại. Vui lòng thử lại.', 'danger')
        return redirect(url_for('main.login'))

    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    email = user_info.get('email')

    if email is None:
        flash('Không lấy được thông tin email từ Google.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=user_info.get('name', email.split('@')[0]),
            email=email,
            password=generate_password_hash('google-auth')
        )
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('main.home'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.avatar.data:
            avatar_file = form.avatar.data
            filename = avatar_file.filename
            avatar_path = os.path.join(current_app.root_path, 'static', 'avatars', filename)
            avatar_file.save(avatar_path)
            current_user.avatar = filename

        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', form=form)

@main.route('/friend_requests')
@login_required
def friend_requests():
    requests = Friendship.query.options(joinedload(Friendship.user))\
        .filter_by(friend_id=current_user.id, status='pending').all()
    form = DummyForm()
    return render_template('friend_requests.html', friend_requests=requests, form=form)

@main.route('/accept_friend_request/<int:request_id>')
@login_required
def accept_friend_request(request_id):
    f = Friendship.query.get_or_404(request_id)
    if f.friend_id != current_user.id:
        flash('Không có quyền thao tác.', 'danger')
        return redirect(url_for('main.friend_requests'))

    f.status = 'accepted'
    reverse = Friendship(user_id=f.friend_id, friend_id=f.user_id, status='accepted')
    db.session.add(reverse)
    db.session.commit()
    flash('Đã chấp nhận lời mời kết bạn.', 'success')
    return redirect(url_for('main.friend_requests'))

@main.route('/friends')
@login_required
def friends():
    friends = current_user.get_friends()
    return render_template('friends.html', friends=friends, current_user_id=current_user.id)

@main.route('/call_info/<int:friend_id>')
@login_required
def call_info(friend_id):
    friend = User.query.get_or_404(friend_id)
    friendship = Friendship.query.filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
            and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id)
        ),
        Friendship.status == 'accepted'
    ).first()

    if not friendship:
        return jsonify({'error': 'Bạn chưa kết bạn với người này.'}), 403

    room_id = f"call_{min(current_user.id, friend_id)}_{max(current_user.id, friend_id)}"
    return jsonify({
        'friend_id': friend.id,
        'friend_username': friend.username,
        'room_id': room_id,
        'user_id': current_user.id
    })

@main.route('/messages')
@login_required
def message_home():
    friends = current_user.get_friends()  # danh sách bạn bè
    messages = current_user.get_inbox()   # tin nhắn nhận được
    return render_template('messages_home.html', messages=messages, friends=friends)


@main.route('/messages/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def messages(friend_id):
    friend = User.query.get_or_404(friend_id)
    friendship = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend_id, status='accepted').first()
    if not friendship:
        flash('Bạn chưa kết bạn với người này.', 'warning')
        return redirect(url_for('main.message_home'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = Message(sender_id=current_user.id, receiver_id=friend_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('main.messages', friend_id=friend_id))
        else:
            flash('Tin nhắn không được để trống.', 'warning')

    msgs = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == friend_id),
            and_(Message.sender_id == friend_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()

    tz_hanoi = timezone('Asia/Ho_Chi_Minh')
    for msg in msgs:
        if msg.created_at:
            utc = pytz.utc
            if msg.created_at.tzinfo is None:
                msg.created_at = utc.localize(msg.created_at)
            msg.created_at_hn = msg.created_at.astimezone(tz_hanoi)
        else:
            msg.created_at_hn = None

    return render_template('messages.html', friend=friend, messages=msgs)

@main.route('/search', methods=['GET'])
@login_required
def search_friends():
    query = request.args.get('q', '').strip()
    users = []
    friendships = []

    if query:
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()
        friendships = Friendship.query.filter(
            or_(Friendship.user_id == current_user.id, Friendship.friend_id == current_user.id)
        ).all()

    form = FriendRequestForm()
    return render_template('search_friends.html', users=users, friendships=friendships, form=form)

@main.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateProfileForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash("Thông tin đã được cập nhật.", "success")
        return redirect(url_for('main.user_profile', user_id=user.id))

    friendship = Friendship.query.filter_by(user_id=current_user.id, friend_id=user_id, status='accepted').first()
    pending_request = Friendship.query.filter_by(user_id=current_user.id, friend_id=user_id, status='pending').first()

    return render_template('profile.html', user=user, form=form, friendship=friendship, pending_request=pending_request)

@main.route('/send_message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    form = MessageForm()

    if form.validate_on_submit():
        content = form.content.data.strip()
        if not content:
            flash('Nội dung tin nhắn không được để trống.', 'warning')
            return redirect(url_for('main.send_message', receiver_id=receiver_id))

        message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()
        flash('Tin nhắn đã được gửi!', 'success')
        return redirect(url_for('main.messages', friend_id=receiver_id))

    return render_template('send_message.html', form=form, receiver_username=receiver.username)

@main.route('/chat/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def chat(friend_id):
    friend = User.query.get_or_404(friend_id)
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            message = Message(sender_id=current_user.id, receiver_id=friend_id, content=content)
            db.session.add(message)
            db.session.commit()
            flash('Tin nhắn đã gửi!', 'success')
        return redirect(url_for('main.chat', friend_id=friend_id))

    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == friend_id),
            and_(Message.sender_id == friend_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()

    tz_hanoi = timezone('Asia/Ho_Chi_Minh')
    for msg in messages:
        if msg.created_at:
            utc = pytz.utc
            if msg.created_at.tzinfo is None:
                msg.created_at = utc.localize(msg.created_at)
            msg.created_at_hn = msg.created_at.astimezone(tz_hanoi)
        else:
            msg.created_at_hn = None

    return render_template('chat.html', friend=friend, messages=messages)

@main.route('/received_messages')
@login_required
def received_messages():
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    for msg in messages:
        if msg.created_at:
            msg.created_at_hn = msg.created_at
        else:
            msg.created_at_hn = None
            current_app.logger.warning(f"Tin nhắn ID {msg.id} không có giá trị created_at.")
    return render_template('received_messages.html', messages=messages)

@main.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    if user_id == current_user.id:
        flash("Bạn không thể kết bạn với chính mình.", "warning")
        return redirect(url_for('main.home'))

    existing = Friendship.query.filter_by(user_id=current_user.id, friend_id=user_id).first()
    if existing:
        flash("Bạn đã gửi lời mời rồi hoặc đã là bạn bè.", "info")
    else:
        fr = Friendship(user_id=current_user.id, friend_id=user_id, status='pending')
        db.session.add(fr)
        db.session.commit()
        flash("Đã gửi lời mời kết bạn.", "success")
    return redirect(url_for('main.home'))

@main.route('/respond_friend_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def respond_friend_request(request_id, action):
    fr = Friendship.query.get_or_404(request_id)
    if fr.friend_id != current_user.id:
        flash("Không hợp lệ.", "danger")
        return redirect(url_for('main.friend_requests'))

    if action == 'accept':
        fr.status = 'accepted'
        flash("Đã chấp nhận lời mời kết bạn.", "success")
    elif action == 'reject':
        fr.status = 'rejected'
        flash("Đã từ chối lời mời.", "info")
    db.session.commit()
    return redirect(url_for('main.friend_requests'))

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        try:
            image_file = None
            if form.image.data:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                image = form.image.data
                file_ext = os.path.splitext(image.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                    flash('Chỉ chấp nhận file ảnh (JPG, PNG, GIF)', 'danger')
                    return redirect(url_for('main.create_post'))
                
                filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                image_file = filename

            post = Post(
                content=form.content.data,
                image=image_file,
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(post)
            db.session.commit()
            flash('Bài viết đã được đăng!', 'success')
            return redirect(url_for('main.feed'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Lỗi khi tạo bài viết: {str(e)}")
            flash('Có lỗi xảy ra khi đăng bài', 'danger')
    
    return render_template('create_post.html', form=form)

@main.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for('main.feed'))

@main.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

        if like:
            db.session.delete(like)
            action = 'unliked'
        else:
            like = Like(user_id=current_user.id, post_id=post.id)
            db.session.add(like)
            action = 'liked'
        
        db.session.commit()

        return jsonify({
            'status': 'success',
            'action': action,
            'likes_count': len(post.likes),
            'post_id': post_id
        })

    except Exception as e:
        current_app.logger.error(f"Lỗi khi thích bài viết: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Lỗi máy chủ nội bộ'
        }), 500

@main.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    content = request.form.get('content')
    if not content:
        return jsonify({'status': 'error', 'message': 'Nội dung trống'}), 400
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'comment_html': render_template('_comment.html', comment=comment),
            'comments_container': f'#post-{post_id} .comments-list'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        
        if current_user in comment.liked_by:
            comment.liked_by.remove(current_user)
            action = 'unliked'
        else:
            comment.liked_by.append(current_user)
            action = 'liked'
        
        db.session.commit()

        return jsonify({
            'status': 'success',
            'action': action,
            'likes_count': len(comment.liked_by)
        })

    except Exception as e:
        current_app.logger.error(f"Lỗi khi thích bình luận: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Lỗi máy chủ nội bộ'
        }), 500

@main.route('/reply_comment/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')

    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Nội dung không được để trống'}), 400
        flash('Nội dung không được để trống', 'warning')
        return redirect(url_for('main.feed'))

    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=parent_comment.post_id,
        parent_id=parent_comment.id
    )

    try:
        db.session.add(reply)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            replies_html = render_template('_replies.html', comment=parent_comment)
            return jsonify({'status': 'success', 'replies_html': replies_html})

        flash('Đã trả lời bình luận!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Đã xảy ra lỗi'}), 500
        flash('Đã xảy ra lỗi khi trả lời', 'danger')

    return redirect(url_for('main.feed', _anchor=f'comment-{comment_id}'))

@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    
    if comment.user_id != current_user.id and comment.post.user_id != current_user.id:
        flash('Bạn không có quyền xóa bình luận này', 'danger')
        return redirect(url_for('main.feed'))
    
    for reply in comment.replies:
        db.session.delete(reply)
    
    db.session.delete(comment)
    db.session.commit()
    flash('Bình luận đã được xóa', 'success')
    return redirect(url_for('main.feed', _anchor=f'post-{post_id}'))

@main.route('/feed')
@login_required
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    tz_hanoi = timezone('Asia/Ho_Chi_Minh')
    for post in posts:
        if post.created_at:
            utc = pytz.utc
            if post.created_at.tzinfo is None:
                post.created_at = utc.localize(post.created_at)
            post.created_at_hn = post.created_at.astimezone(tz_hanoi)
        else:
            post.created_at_hn = None
            current_app.logger.warning(f"Bài viết ID {post.id} không có giá trị created_at.")

    post_form = PostForm()
    comment_form = CommentForm()
    return render_template('feed.html', 
                         posts=posts, 
                         post_form=post_form,
                         comment_form=comment_form)

@main.route('/posts')
def list_posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('post_list.html', posts=posts)

@main.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    # Gắn timezone nếu chưa có
    if post.created_at and post.created_at.tzinfo is None:
        post.created_at = utc.localize(post.created_at)

    # Chuyển sang giờ Việt Nam
    post.created_at_hn = post.created_at.astimezone(timezone('Asia/Ho_Chi_Minh')) if post.created_at else None

    return render_template('post_detail.html', post=post)


# WebSocket handlers for call signaling
@socketio.on('join_call')
def on_join_call(data):
    room_id = data['room_id']
    join_room(room_id)
    emit('user_joined', {'user_id': data['user_id']}, room=room_id)

@socketio.on('offer')
def handle_offer(data):
    room_id = data['room_id']
    emit('offer', {'offer': data['offer'], 'from_user': data['user_id']}, room=room_id, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    room_id = data['room_id']
    emit('answer', {'answer': data['answer'], 'from_user': data['user_id']}, room=room_id, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    room_id = data['room_id']
    emit('ice_candidate', {'candidate': data['candidate'], 'from_user': data['user_id']}, room=room_id, include_self=False)

@socketio.on('leave_call')
def on_leave_call(data):
    room_id = data['room_id']
    user_id = data['user_id']
    friend_id = data['friend_id']
    duration = data.get('duration')

    call = Call.query.filter_by(caller_id=user_id, callee_id=friend_id).order_by(Call.created_at.desc()).first()
    if call:
        call.duration = duration
        db.session.commit()

    leave_room(room_id)
    emit('user_left', {'user_id': user_id}, room=room_id)
    
    
    
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Post, Comment
from functools import wraps

# Create admin blueprint
admin = Blueprint('admin', __name__)

# Decorator to restrict access to admin users only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bạn cần quyền admin để truy cập trang này.', 'danger')
            return redirect(url_for('main.feed'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard showing overview of system statistics"""
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_posts=total_posts,
                         total_comments=total_comments,
                         active_users=active_users)

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """View and manage all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@admin.route('/admin/user/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể vô hiệu hóa chính mình!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'kích hoạt' if user.is_active else 'vô hiệu hóa'
    flash(f'Người dùng {user.username} đã được {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể thay đổi quyền admin của chính mình!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    status = 'admin' if user.is_admin else 'người dùng thường'
    flash(f'Người dùng {user.username} giờ là {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/posts')
@login_required
@admin_required
def manage_posts():
    """View and manage all posts"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/posts.html', posts=posts)

@admin.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Bài viết đã được xóa.', 'success')
    return redirect(url_for('admin.manage_posts'))

@admin.route('/admin/comments')
@login_required
@admin_required
def manage_comments():
    """View and manage all comments"""
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/comments.html', comments=comments)

@admin.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Bình luận đã được xóa.', 'success')
    return redirect(url_for('admin.manage_comments'))
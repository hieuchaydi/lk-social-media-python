from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import func, or_
from app import db
from pytz import timezone

# Timezone mặc định
tz = timezone('Asia/Ho_Chi_Minh')

# Bảng trung gian cho lượt thích bình luận
comment_likes = db.Table('comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(tz))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200), default='default.jpg')
    total_hearts = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    posts = db.relationship('Post', back_populates='user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', lazy=True, cascade='all, delete-orphan')
    post_likes = db.relationship('Like', back_populates='user', lazy=True)
    comment_likes = db.relationship('Comment', secondary=comment_likes, back_populates='liked_by', lazy='dynamic')

    # Messages
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver', lazy=True)

    # Friends
    sent_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.user_id', back_populates='user', lazy=True)
    received_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.friend_id', back_populates='friend', lazy=True)

    # Calls
    calls_made = db.relationship('Call', foreign_keys='Call.caller_id', back_populates='caller', lazy=True)
    calls_received = db.relationship('Call', foreign_keys='Call.callee_id', back_populates='callee', lazy=True)

    def get_friends(self):
        friendships = Friendship.query.filter(
            ((Friendship.user_id == self.id) | (Friendship.friend_id == self.id)) &
            (Friendship.status == 'accepted')
        ).all()
        return [fs.friend if fs.user_id == self.id else fs.user for fs in friendships]

    def update_hearts_count(self):
        self.total_hearts = sum(post.like_count() for post in self.posts)
        db.session.commit()

    def get_inbox(self):
        return Message.query.filter_by(receiver_id=self.id).order_by(Message.created_at.desc()).all()

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))

    user = db.relationship('User', foreign_keys=[user_id], back_populates='sent_friend_requests')
    friend = db.relationship('User', foreign_keys=[friend_id], back_populates='received_friend_requests')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz), index=True)
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(tz))

    user = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='post', lazy=True, cascade='all, delete-orphan')

    def like_count(self):
        return len(self.likes)

    def get_daily_likes(self):
        today = date.today()
        return Like.query.filter(
            Like.post_id == self.id,
            func.date(Like.created_at) == today
        ).count()

    @classmethod
    def get_top_daily_posts(cls, limit=5, min_daily_likes=1):
        today = date.today()
        daily_likes = (
            db.session.query(
                Like.post_id,
                func.count(Like.id).label('daily_likes')
            )
            .filter(func.date(Like.created_at) == today)
            .group_by(Like.post_id)
            .subquery()
        )
        return (
            cls.query
            .outerjoin(daily_likes, cls.id == daily_likes.c.post_id)
            .order_by(
                db.desc(daily_likes.c.daily_likes),
                db.desc(cls.created_at)
            )
            .limit(limit)
            .all()
        )

    @classmethod
    def get_recent_posts_excluding(cls, exclude_ids, limit=20):
        return cls.query.filter(~cls.id.in_(exclude_ids)).order_by(cls.created_at.desc()).limit(limit).all()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')
    replies = db.relationship('Comment',
                            backref=db.backref('parent', remote_side=[id]),
                            lazy='select',
                            cascade='all, delete-orphan')
    liked_by = db.relationship('User', secondary=comment_likes, back_populates='comment_likes', lazy='dynamic')

    def like_count(self):
        return self.liked_by.count()

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))

    user = db.relationship('User', back_populates='post_likes')
    post = db.relationship('Post', back_populates='likes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_like'),
    )

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(tz))

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    callee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))
    duration = db.Column(db.Integer)  # đơn vị: giây

    caller = db.relationship('User', foreign_keys=[caller_id], back_populates='calls_made')
    callee = db.relationship('User', foreign_keys=[callee_id], back_populates='calls_received')

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_serializer import SerializerMixin
import uuid

from .app import app
db = SQLAlchemy(app)


class UserAccount(db.Model, SerializerMixin):
    __tablename__ = "user_account"
    __table_args__ = (
        db.UniqueConstraint(
            'user_id'
            'username',
            'email',
            name='id_username_email_constraint'
        ),
    )
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    display_name = db.Column(db.Text)
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    URL = db.Column(db.Text)
    DOB = db.Column(db.Date)
    visible = db.Column(db.Boolean)
    private = db.Column(db.Boolean)
    touched_ts = db.Column(db.DateTime)


class Login(db.Model, SerializerMixin):
    __tablename__ = "login"
    log_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID)
    browser_id = db.Column(UUID)
    device_id = db.Column(UUID)
    login_ts = db.Column(db.DateTime)


class Browser(db.Model, SerializerMixin):
    __tablename__ = "browser"
    browser_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    browser_name = db.Column(db.Text)
    browser_version = db.Column(db.Text)


class Device(db.Model, SerializerMixin):
    __tablename__ = "device"
    device_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_browser = db.Column(UUID)
    device_owner_user = db.Column(UUID)


class Chirp(db.Model, SerializerMixin):
    __tablename__ = "chirp"
    chirp_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Text)
    device_id = db.Column(UUID)
    created_ts = db.Column(db.DateTime)
    chirp_content = db.Column(db.Text)
    image_uri = db.Column(db.Text)
    visible = db.Column(db.Boolean)
    touched_ts = db.Column(db.DateTime)


class Following(db.Model, SerializerMixin):
    __tablename__ = "following"
    follow_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower = db.Column(UUID)
    following = db.Column(UUID)
    created_ts = db.Column(db.DateTime)


class ReChirp(db.Model, SerializerMixin):
    __tablename__ = "rechirp"
    re_chirp_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chirp_id = db.Column(UUID)
    device_id = db.Column(UUID)
    re_user_id = db.Column(UUID)
    rechirp_quote = db.Column(db.Text)
    created_ts = db.Column(db.DateTime)
    visible = db.Column(db.Boolean)
    touched_ts = db.Column(db.DateTime)


class DirectMessage(db.Model, SerializerMixin):
    __tablename__ = "direct_message"
    dm_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_user_id = db.Column(UUID)
    recipient_user_id = db.Column(UUID)
    message = db.Column(db.Text)
    created_ts = db.Column(db.DateTime)


class Block(db.Model, SerializerMixin):
    __tablename__ = "block"
    block_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID)
    blocked_user_id = db.Column(UUID)
    created_ts = db.Column(db.DateTime)


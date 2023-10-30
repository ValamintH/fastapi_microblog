from datetime import datetime
from hashlib import md5

import sqlalchemy as sa
from dependencies.db import Base
from models.posts import Post
from sqlalchemy.orm import backref, relationship
from werkzeug.security import check_password_hash, generate_password_hash

followers = sa.Table(
    "followers",
    Base.metadata,
    sa.Column("follower_id", sa.ForeignKey("users.id")),
    sa.Column("followed_id", sa.ForeignKey("users.id")),
)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(64), index=True, unique=True)
    email = sa.Column(sa.String(120), index=True, unique=True)
    password_hash = sa.Column(sa.String(128))
    about_me = sa.Column(sa.String(140))
    last_seen = sa.Column(sa.DateTime, default=datetime.utcnow)
    posts = relationship("Post", backref="author", lazy="dynamic")
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest,
            size,
        )

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id
        )
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

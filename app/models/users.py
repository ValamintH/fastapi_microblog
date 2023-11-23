from datetime import datetime
from hashlib import md5

import sqlalchemy as sa
from dependencies.db import Base
from models.followers import Followers
from models.posts import Post
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import object_session
from werkzeug.security import check_password_hash, generate_password_hash


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
        secondary=Followers.__table__,
        primaryjoin=(Followers.__table__.c.follower_id == id),
        secondaryjoin=(Followers.__table__.c.followed_id == id),
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

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(Followers.__table__.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        session = object_session(self)
        followed = (
            session.query(Post)
            .join(Followers.__table__, (Followers.__table__.c.followed_id == Post.user_id))  # noqa
            .filter(Followers.__table__.c.follower_id == self.id)
        )
        own = session.query(Post).filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

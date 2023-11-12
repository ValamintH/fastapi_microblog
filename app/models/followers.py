import sqlalchemy as sa
from dependencies.db import Base


class Followers(Base):
    __tablename__ = "followers"

    follower_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True, nullable=True)
    followed_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True, nullable=True)

from datetime import datetime

import sqlalchemy as sa
from dependencies.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = sa.Column(sa.Integer, primary_key=True)
    body = sa.Column(sa.String(140))
    timestamp = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    def __repr__(self):
        return "<Post {}>".format(self.body)

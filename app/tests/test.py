from datetime import datetime, timedelta

import pytest
from dependencies.db import Base, engine, get_db
from fastapi.testclient import TestClient
from main import app
from models.posts import Post
from models.users import User

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_password_hashing():
    u = User(username="samantha")
    u.set_password("cat")
    assert not u.check_password("dog")
    assert u.check_password("cat")


def test_avatar():
    u = User(username="john", email="john@example.com")
    assert u.avatar(128) == (
        "https://www.gravatar.com/avatar/" "d4c74594d841139328695756648b6bd6" "?d=identicon&s=128"
    )


@pytest.mark.asyncio
async def test_follow():
    db = await get_db().__anext__()
    u1 = User(username="jerry", email="jerry@example.com")
    u2 = User(username="susan", email="susan@example.com")
    db.add(u1)
    db.add(u2)
    db.commit()
    assert u1.followed.all() == []
    assert u1.followers.all() == []

    u1.follow(u2)
    db.commit()
    assert u1.is_following(u2)
    assert u1.followed.count() == 1
    assert u1.followed.first().username == "susan"
    assert u2.followers.count() == 1
    assert u2.followers.first().username == "jerry"

    u1.unfollow(u2)
    db.commit()
    assert not u1.is_following(u2)
    assert u1.followed.count() == 0
    assert u2.followers.count() == 0


@pytest.mark.asyncio
async def test_follow_posts():
    db = await get_db().__anext__()

    # create four users
    u1 = User(username="john", email="john@example.com")
    u2 = User(username="sam", email="sam@example.com")
    u3 = User(username="mary", email="mary@example.com")
    u4 = User(username="david", email="david@example.com")
    db.add_all([u1, u2, u3, u4])

    # create four posts
    now = datetime.utcnow()
    p1 = Post(body="post from john", author=u1, timestamp=now + timedelta(seconds=1))
    p2 = Post(body="post from sam", author=u2, timestamp=now + timedelta(seconds=4))
    p3 = Post(body="post from mary", author=u3, timestamp=now + timedelta(seconds=3))
    p4 = Post(body="post from david", author=u4, timestamp=now + timedelta(seconds=2))
    db.add_all([p1, p2, p3, p4])
    db.commit()

    # set up the followers
    u1.follow(u2)  # john follows sam
    u1.follow(u4)  # john follows david
    u2.follow(u3)  # sam follows mary
    u3.follow(u4)  # mary follows david
    db.commit()

    # check the followed posts of each user
    f1 = u1.followed_posts()
    f2 = u2.followed_posts()
    f3 = u3.followed_posts()
    f4 = u4.followed_posts()

    for f, p in zip(f1, [p2, p4, p1]):
        assert repr(f) == repr(p)

    for f, p in zip(f2, [p2, p3]):
        assert repr(f) == repr(p)

    for f, p in zip(f3, [p3, p4]):
        assert repr(f) == repr(p)

    assert repr(f4[0]) == repr(p4)

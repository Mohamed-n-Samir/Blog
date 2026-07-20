from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Column,
    Table,
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base

import math

from app.models.schemas import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole),
        default=UserRole.USER,
    )
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    image_file: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[Post]] = relationship(back_populates="author")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Self-referential relationship for following/followers
    following: Mapped[list[User]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == followers.c.follower_id",
        secondaryjoin="User.id == followers.c.followed_id",
        back_populates="followers",
    )
    followers: Mapped[list[User]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == followers.c.followed_id",
        secondaryjoin="User.id == followers.c.follower_id",
        back_populates="following",
    )

    liked_posts: Mapped[list[Post]] = relationship(
        "Post",
        secondary="post_likes",
        back_populates="likes",
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/imgs/profile_pics/default.png"


followers = Table(
    "followers",
    Base.metadata,
    Column(
        "follower_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "followed_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


post_likes = Table(
    "post_likes",
    Base.metadata,
    Column(
        "post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    image_file: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
        default=None,
    )
    tags: Mapped[list[Tag]] = relationship(secondary=post_tags, back_populates="posts")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True
    )

    author: Mapped[User] = relationship(back_populates="posts")
    category: Mapped[Category | None] = relationship(back_populates="posts")

    likes: Mapped[list[User]] = relationship(
        "User",
        secondary=post_likes,
        back_populates="liked_posts",
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/blog_images/{self.image_file}"
        return "/static/imgs/blog_images/post_placeholder.avif"

    @property
    def likes_count(self) -> int:
        try:
            return len(self.likes)
        except Exception:
            return 0

    @property
    def comments_count(self) -> int:
        try:
            return len(self.comments)
        except Exception:
            return 0

    @property
    def reading_time_minutes(self):
        word_count = len(self.content.split())
        words_per_minute = 200
        return math.ceil(word_count / words_per_minute)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    # Inverse relationship side
    posts: Mapped[list[Post]] = relationship(secondary=post_tags, back_populates="tags")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    posts: Mapped[list[Post]] = relationship(back_populates="category")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    author: Mapped[User] = relationship(back_populates="comments")
    post: Mapped[Post] = relationship(back_populates="comments")

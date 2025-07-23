import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy_utils import PasswordType, force_auto_coercion
from sqlalchemy.orm import relationship

Base = declarative_base()
force_auto_coercion()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, index=True)
    avatar_url = Column(String(256), default="default_avatar.png")
    username = Column(String(32), unique=True, nullable=False)
    display_name = Column(String(32), nullable=False)
    password = Column(PasswordType(max_length=128, schemes=["pbkdf2_sha512"]), nullable=False)
    is_online = Column(Boolean, default=False)
    last_online_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    registered_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    access_tokens = relationship(
        "UserAccessToken",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    invite_codes = relationship(
        "InviteCode",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

class UserAccessToken(Base):
    __tablename__ = "user_access_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(String(36), ForeignKey("users.uuid"), nullable=False)
    access_token = Column(String(256), unique=True, nullable=False)
    device_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="access_tokens")

class InviteCode(Base):
    __tablename__ = "invite_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_by_user_uuid = Column(String(36), ForeignKey("users.uuid"), nullable=True)
    used_times = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="invite_codes")

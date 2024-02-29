from sqlalchemy import String, Enum, BigInteger, Column, DateTime, Boolean, UUID, ForeignKey, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .const import ProxyType, DATABASE_URL, SettingsType
from datetime import datetime
import uuid


engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class BaseModelMixin(Base):
    __abstract__ = True
    id = Column(UUID, primary_key=True, unique=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now)


class Users(BaseModelMixin):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String(50), nullable=True)
    full_name = Column(String(50), nullable=True)


class Proxy(BaseModelMixin):
    __tablename__ = "proxy"
    type = Column(Enum(ProxyType), nullable=False)
    host = Column(String(255), nullable=False)
    country = Column(String(50), nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'))


class Message(BaseModelMixin):
    __tablename__ = 'message'
    telegram_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    value = Column(Text)
    video_id = Column(String(20))
    user_id = Column(UUID, ForeignKey('users.id'))


class ProxySettings(BaseModelMixin):
    __tablename__ = "proxy_settings"
    proxy_country = Column(String(50), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'))


class Settings(BaseModelMixin):
    __tablename__ = "settings"
    name = Column(String(255), unique=True)
    code = Column(String(255), unique=True)
    description = Column(String(255))
    type = Column(Enum(SettingsType))
    value = Column(Text())


def init_models():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with open('settings_fixture.json', 'r') as f:
        items = eval(str(f.read()))

    for item in items:
        fields = item['fields']
        setting = Settings(
            name=fields["name"],
            code=fields["code"],
            type=fields["type"],
            value=fields["value"],
            description=fields['description']
        )
        session.add(setting)
        session.commit()
        session.refresh(setting)

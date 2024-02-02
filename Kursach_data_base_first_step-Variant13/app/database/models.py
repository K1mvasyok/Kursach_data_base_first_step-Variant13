from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, select, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from config import SQLALCHEMY_URL, ADMIN_TELEGRAM_ID

engine = create_async_engine(SQLALCHEMY_URL, echo=True)
async_session = AsyncSession(engine)
Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

class Klient(Base):
    __tablename__ = 'klients'

    id = Column(Integer, primary_key=True)
    passport = Column(Integer)
    fio_klient = Column(String)
    address = Column(String)
    phone_number = Column(String)
    telegram_id = Column(BigInteger, unique=True)

    arendas = relationship('Arenda', back_populates='klient')

class Studio_of_movie(Base):
    __tablename__ = 'studios_of_a_movies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)

    movies = relationship('MovieStudio', back_populates='studio')

class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    movies = relationship('MovieGenre', back_populates='genre')

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    studio_id = Column(Integer, ForeignKey('studios_of_a_movies.id'))
    fio_director = Column(String)
    performers_of_the_main_roles = Column(String)
    year_of_release = Column(Integer)
    annotation = Column(String)
    cost = Column(Integer)

    studios = relationship('MovieStudio', back_populates='movie')
    arendas = relationship('Arenda', back_populates='movie')
    genres = relationship('MovieGenre', back_populates='movie')

class Arenda(Base):
    __tablename__ = 'arenda'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    passport = Column(Integer, ForeignKey('klients.passport'))
    cost = Column(Integer)
    time_to_start = Column(DateTime)
    time_to_finish = Column(DateTime)

    movie = relationship('Movie', back_populates='arendas')
    klient = relationship('Klient', back_populates='arendas')

class MovieGenre(Base):
    __tablename__ = 'movie_genre'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    genre_id = Column(Integer, ForeignKey('genre.id'))

    movie = relationship('Movie', back_populates='genres')
    genre = relationship('Genre', back_populates='movies')

class MovieStudio(Base):
    __tablename__ = 'movie_studio'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    studio_id = Column(Integer, ForeignKey('studios_of_a_movies.id'))

    movie = relationship('Movie', back_populates='studios')
    studio = relationship('Studio_of_movie', back_populates='movies')

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from app.database.requests import get_admin_by_telegram_id
        admin_exists = await get_admin_by_telegram_id(ADMIN_TELEGRAM_ID)
        if not admin_exists:
            new_admin = Admin(telegram_id=ADMIN_TELEGRAM_ID)
            conn.add(new_admin)
            await conn.commit()
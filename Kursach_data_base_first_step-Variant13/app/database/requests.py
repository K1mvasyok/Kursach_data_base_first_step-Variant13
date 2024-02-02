from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound

from app.database.models import Genre, Movie, Studio_of_movie, Admin
from app.database.models import async_session 


async def get_movies():
    async with async_session as session:
        result = await session.execute(select(Movie))
        return result.scalars().all()

async def get_movie_by_id(movie_id):
    async with async_session as session:
        result = await session.execute(select(Movie).where(Movie.id == movie_id))
        return result.scalar()

async def get_genre():
    async with async_session as session:
        result = await session.execute(select(Genre))
        return result.scalars().all()

async def get_movie_by_id(movie_id):
    async with async_session as session:
        result = await session.execute(select(Movie).where(Movie.id == movie_id))
        return result.scalar()

async def get_movies_by_genre(genre_name):
    async with async_session as session:
        query = select(Movie).join(Genre).where(Genre.name == genre_name)
        result = await session.execute(query)
        return result.scalars().all()

async def get_genre_by_id(genre_id):
    async with async_session as session:
        result = await session.execute(select(Genre).where(Genre.id == genre_id))
        return result.scalar()

async def get_studio_by_id(studio_id):
    async with async_session as session:
        query = select(Studio_of_movie).where(Studio_of_movie.id == studio_id)
        result = await session.execute(query)
        studio_of_movie = result.scalar()
        return studio_of_movie if studio_of_movie else None

async def get_directors():
    async with async_session as session:
        result = await session.execute(select(Movie.fio_director).distinct())
        return [director[0] for director in result.all()]
    
async def get_movies_by_director(director_name):
    async with async_session as session:
        query = select(Movie).where(Movie.fio_director == director_name)
        result = await session.execute(query)
        return result.scalars().all()

async def get_studios():
    async with async_session as session:
        result = await session.execute(select(Studio_of_movie))
        return result.scalars().all()

async def get_movies_by_studio(studio_id):
    async with async_session as session:
        query = select(Movie).join(Studio_of_movie).where(Studio_of_movie.id == studio_id)
        result = await session.execute(query)
        movies = result.scalars().all()
        return movies

async def get_admin_by_telegram_id(telegram_id):
    async with async_session as session:
        result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        try:
            admin = result.scalar_one()
            return admin
        except NoResultFound:
            return None



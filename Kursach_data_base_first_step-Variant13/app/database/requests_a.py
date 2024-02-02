from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload 

from app.database.models import Genre, Movie, Studio_of_movie, Arenda, Klient
from app.database.models import async_session
from app.database.requests import get_movie_by_id


async def delete_movie_from_db(movie_id):
    async with async_session as conn:
        movie = await get_movie_by_id(movie_id)
        if movie:
            conn.delete(movie)
            await conn.commit()
            return True
        return False

async def get_genre_by_name(genre_name):
    async with async_session as session:
        result = await session.execute(select(Genre).where(Genre.name == genre_name))
        return result.scalar()

async def get_studio_by_name(studio_name):
    async with async_session as session:
        result = await session.execute(select(Studio_of_movie).where(Studio_of_movie.name == studio_name))
        return result.scalar()
    
async def get_movies_in_rent():
    async with async_session as session:
        stmt = (
            select(Movie, Arenda, Klient)
            .join(Arenda, Movie.arendas)
            .join(Klient, Arenda.klient)
            .options(selectinload(Movie.arendas).selectinload(Arenda.klient))
        )
        result = await session.execute(stmt)
        data = result.all()
        return data

async def get_movies_over_10_days():
    async with async_session as session:
        ten_days_ago = datetime.now() - timedelta(days=10)
        stmt = (
            select(Movie, Arenda, Klient)
            .join(Arenda, Movie.arendas)
            .join(Klient, Arenda.klient)
            .filter(
                and_(
                    Arenda.time_to_start <= ten_days_ago,
                )
            )
        )
        result = await session.execute(stmt)
        data = result.all()
        return data
    
async def save_movie_to_db(data: dict):
    try:
        async with async_session as session:
            async with session.begin():
                genre_name = data.get('genre')
                if genre_name:
                    genre = await session.execute(select(Genre).where(Genre.name == genre_name))
                    genre = genre.scalar() or Genre(name=genre_name)
                    await session.merge(genre)

                studio_id = data.get('studio')
                if studio_id:
                    studio_id = int(studio_id)
                else:
                    studio_name = data.get('studio')
                    studio = await session.execute(select(Studio_of_movie).where(Studio_of_movie.name == studio_name))
                    studio = studio.scalar() or Studio_of_movie(name=studio_name)
                    await session.merge(studio)
                    studio_id = studio.id

                movie_data = {
                    'name': data.get('name'),
                    'genre_id': genre.id if genre_name else None,
                    'studio_id': studio_id,
                    'fio_director': data.get('director'),
                    'performers_of_the_main_roles': data.get('actors'),
                    'year_of_release': data.get('year'),
                    'annotation': data.get('annotation'),
                    'cost': data.get('cost')
                }

                movie = Movie(**movie_data)
                await session.merge(movie)

            await session.commit()
    except Exception as e:
        print(f"Error saving movie to database: {e}")

async def save_genre_to_db(data: dict):
    try:
        async with async_session as session:
            async with session.begin():
                genre_name = data.get('name_genre')
                if genre_name:
                    genre = await session.execute(select(Genre).where(Genre.name == genre_name))
                    genre = genre.scalar() or Genre(name=genre_name)
                    await session.merge(genre)

            await session.commit()
    except Exception as e:
        print(f"Error saving genre to database: {e}")

async def save_studio_to_db(data: dict):
    try:
        async with async_session as session:
            async with session.begin():
                studio_name = data.get('name_studio')
                studio_country = data.get('country_studio')

                if studio_name and studio_country:
                    studio = await session.execute(
                        select(Studio_of_movie).where(
                            and_(Studio_of_movie.name == studio_name, Studio_of_movie.country == studio_country)
                        )
                    )
                    studio = studio.scalar() or Studio_of_movie(name=studio_name, country=studio_country)
                    await session.merge(studio)

            await session.commit()
    except Exception as e:
        print(f"Error saving studio to database: {e}") 
      
async def get_all_movies():
    async with async_session as session:
        movies = await session.execute(select(Movie))
        return movies.scalars().all()

async def delete_movie_by_id(movie_id):
    async with async_session as session:
        movie = await session.get(Movie, movie_id)
        if movie:
            await session.delete(movie)
            await session.commit()
            return True
        else:
            return False
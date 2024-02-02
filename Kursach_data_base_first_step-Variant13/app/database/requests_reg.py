from datetime import datetime
from datetime import timezone
from sqlalchemy import select, and_
from app.database.models import async_session

from app.database.models import Klient, Arenda, Movie


async def save_user_to_db(telegram_id, data):
    async with async_session as session:
        klient_instance = await session.merge(Klient(telegram_id=telegram_id))
        klient_instance.passport = data['passport']
        klient_instance.fio_klient = data['fio_klient']
        klient_instance.address = data['address']
        klient_instance.phone_number = data['phone_number']

        await session.commit()

async def save_arenda_data(movie_id, passport):
    movie_cost = await get_movie_cost(movie_id)
    arenda_data = {
        "movie_id": movie_id,
        "passport": passport,
        "cost": movie_cost,
        "time_to_start": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "time_to_finish": None
        }
    async with async_session as session:
        await session.execute(Arenda.__table__.insert().values(arenda_data))
        await session.commit()

async def get_movie_cost(movie_id):
    async with async_session as session:
        query = select(Movie.cost).where(Movie.id == movie_id)
        result = await session.execute(query)
        return result.scalar()

async def get_user_data(telegram_id):
    async with async_session as session:
        query = select(Klient).where(Klient.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar()
        return user

async def is_user_registered_db(telegram_id):
    async with async_session as session:
        query = select(Klient).where(Klient.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar() is not None
    
async def get_user_data_by_telegram_id(telegram_id):
    async with async_session as session:
        query = select(Klient).where(Klient.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar()
        return user
    
async def get_rented_movies_by_user(telegram_id):
    async with async_session as session:
        query = (
            select(Arenda, Movie)
            .join(Movie, Arenda.movie_id == Movie.id)
            .join(Klient, Arenda.passport == Klient.passport)
            .where(and_(Klient.telegram_id == telegram_id, Arenda.time_to_finish.is_(None)))
            .order_by(Arenda.time_to_start)
        )
        result = await session.execute(query)
        return result.all()
    
async def finish_rental_in_db(arenda_id, user_id):
    async with async_session as session:
        arenda = await session.get(Arenda, arenda_id)
        if arenda:            
            await session.delete(arenda)
            await session.commit()
            return True
        else:
            return False
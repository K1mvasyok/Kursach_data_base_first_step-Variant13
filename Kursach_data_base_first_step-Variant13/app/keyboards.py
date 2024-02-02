from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.database.requests import get_genre, get_movies, get_directors, get_studios, get_movies_by_director, get_movies_by_genre, get_movies_by_studio

async def menu(user_id, user_registered_func):
    is_user_registered = await user_registered_func(user_id)
    registration_button = [KeyboardButton(text="📌 Регистрация")] if not is_user_registered else []
    profile_button = [KeyboardButton(text="📋 Моя анкета")] if is_user_registered else []
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 Фильмы"), KeyboardButton(text="💡 Сортировка по режиссеру")],
            [KeyboardButton(text="💣 Сортировка по жанру"), KeyboardButton(text="📀 Сортировка по киностудии")],
            registration_button + profile_button
        ], resize_keyboard=True, input_field_placeholder="Выберите пункт ниже")

async def return_to_menu():
    return InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")

async def rent_movie_button(movie_id):
    return InlineKeyboardButton(text="🎬 Взять в аренду", callback_data=f"rent_movie:{movie_id}")

async def movies_all(movie_id=None):
    movies = await get_movies()
    keyboard = [[InlineKeyboardButton(text=movie.name, callback_data=f'movie_id:{movie.id}_details')] for movie in movies]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def genre():
    genres = await get_genre()
    keyboard = [[InlineKeyboardButton(text=genre.name, callback_data=f'genre_name:{genre.name}')] for genre in genres]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def director():
    directors = await get_directors()
    keyboard = [[InlineKeyboardButton(text=director, callback_data=f'director_name:{director}')] for director in directors]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def studio():
    studios = await get_studios()
    keyboard = [[InlineKeyboardButton(text=studio.name, callback_data=f'studio_id:{studio.id}')] for studio in studios]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def movies_director(director_name, movie_id=None):
    movies = await get_movies_by_director(director_name)
    keyboard = [[InlineKeyboardButton(text=movie.name, callback_data=f'movie_id:{movie.id}_details')] for movie in movies]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def movies_by_genre(genre_name):
    movies = await get_movies_by_genre(genre_name)
    keyboard = [[InlineKeyboardButton(text=movie.name, callback_data=f'movie_id:{movie.id}_details')] for movie in movies]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def movies_by_studio(studio_id):
    movies = await get_movies_by_studio(studio_id)
    keyboard = [[InlineKeyboardButton(text=movie.name, callback_data=f'movie_id:{movie.id}_details')] for movie in movies]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def finish_rental_buttons(rented_movies):
    buttons = []
    for arenda, movie in rented_movies:
        button_text = f"Завершить аренду фильма: {movie.name}"
        callback_data = f"finish_rental:{arenda.id}"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_delete_movie_keyboard():
    movies = await get_movies()
    keyboard = [[InlineKeyboardButton(text=movie.name, callback_data=f'delete_movie:{movie.id}')] for movie in movies]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def genre_for_add_movie():
    genres = await get_genre()
    keyboard = [[InlineKeyboardButton(text=genre.name, callback_data=f'add_movie_genre_name:{genre.name}')] for genre in genres]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def studio_for_add_movie():
    studios = await get_studios()
    keyboard = [[InlineKeyboardButton(text=studio.name, callback_data=f'add_movie_studio_name:{studio.id}')] for studio in studios]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

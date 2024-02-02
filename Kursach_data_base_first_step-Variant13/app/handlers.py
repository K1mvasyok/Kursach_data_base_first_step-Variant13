from aiogram import F, Router
from aiogram.types import Message
from aiogram import types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb

from app.database.requests import get_movie_by_id, get_genre_by_id, get_studio_by_id, get_admin_by_telegram_id
from app.database.requests_reg import save_user_to_db, is_user_registered_db, get_user_data_by_telegram_id, save_arenda_data, get_user_data, get_rented_movies_by_user, finish_rental_in_db, get_rented_movies_by_user

router_u = Router()
    
class AddNewUser(StatesGroup):
    passport = State()
    fio_klient = State()
    adress = State()
    phone_number = State()
    telegram_id = State()

@router_u.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    admin = await get_admin_by_telegram_id(user_id)
    if admin is None:
        await message.answer(f'Привет 👋🏼,\nЯ - чат-бот видеопроката\n\n'
                             f'Я могу показать: \n\n'
                             f'• Все фильмы \n'
                             f'• Фильмы по выбранному режиссеру\n'
                             f'• Фильмы по выбранному жанру\n'
                             f'• Фильмы по выбранной киностудии\n\n'
                             f'А так же вы можете взять понравившийся фильм в аренду')
        await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu(user_id, is_user_registered_db))
    else:
        await message.answer("Меню администратора", reply_markup=await kb.menu(user_id, is_user_registered_db))

@router_u.message(F.text == 'Меню')
async def Menu(message: Message):
    user_id = message.from_user.id
    await message.answer('🔮 Главное меню', reply_markup=kb.menu(user_id, is_user_registered_db))

@router_u.message(F.text == '🎥 Фильмы')
async def Movie(message: Message):
    await message.answer(f'Выберите фильм, чтобы узнать подробную информацию:', reply_markup=await kb.movies_all())

@router_u.message(F.text == '💣 Сортировка по жанру')
async def Genre(message: Message):
    await message.answer(f'Выберите жанр:', reply_markup=await kb.genre())

@router_u.message(F.text == '💡 Сортировка по режиссеру')
async def Director(message: Message):
    await message.answer(f'Выберете режиссера:', reply_markup=await kb.director())

@router_u.message(F.text == '📀 Сортировка по киностудии')
async def Studio(message: Message):
    await message.answer(f'Выберите киностудию:', reply_markup=await kb.studio())

@router_u.message(F.text == '📌 Регистрация')
async def cmd_register(message: Message, state: FSMContext) -> None: 
    user_id = message.from_user.id
    if await is_user_registered_db(user_id):
        await message.answer("Вы уже зарегистрированы.")
    else:
        await message.answer("Для регистрации введите свои данные: серию и номер паспорта без пробела")
        await state.set_state(AddNewUser.passport)

@router_u.message(F.text == '📋 Моя анкета')
async def view_profile(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data_by_telegram_id(user_id)
    if user_data:
        profile_text = (
            f"📋 Ваша анкета:\n\n"
            f"Паспорт: <b>{user_data.passport}</b>\n"
            f"ФИО: <b>{user_data.fio_klient}</b>\n"
            f"Адрес: <b>{user_data.address}</b>\n"
            f"Номер телефона: <b>{user_data.phone_number}</b>\n"
        )
        rented_movies = await get_rented_movies_by_user(user_id)
        if rented_movies:
            profile_text += "\n🎥 Фильмы в аренде:\n"
            for arenda, movie in rented_movies:
                profile_text += f"\n<b>{movie.name}</b>\n"
                profile_text += f"Начало аренды: {arenda.time_to_start}\n"
                profile_text += f"Цена аренды: {arenda.cost}\n"
            finish_rental_markup = await kb.finish_rental_buttons(rented_movies)
            await message.answer(profile_text, reply_markup=finish_rental_markup)
        else:
            await message.answer(profile_text, reply_markup=await kb.menu(user_id, is_user_registered_db))
    else:
        await message.answer("Ваша анкета не найдена. Возможно, вы еще не зарегистрированы.")
        
@router_u.callback_query(F.data.startswith("genre_name:"))
async def movies_by_genre(query: types.CallbackQuery):
    genre_name = query.data.split(":")[1]
    movies_markup = await kb.movies_by_genre(genre_name)
    if movies_markup.inline_keyboard:
        await query.message.answer(f'{genre_name}:', reply_markup=movies_markup)
    else:
        await query.message.answer('Фильмов по выбранному жанру нет.')

@router_u.callback_query(F.data.startswith("director_name:"))
async def movies_by_director(query: types.CallbackQuery):
    director_name = query.data.split(":")[1]
    await query.message.answer(f'{director_name}:', reply_markup=await kb.movies_director(director_name))

@router_u.callback_query(F.data.startswith("studio_id:"))
async def movies_by_studio(query: types.CallbackQuery):
    studio_id = int(query.data.split(":")[1])
    movies_markup = await kb.movies_by_studio(studio_id)
    if movies_markup.inline_keyboard:
        studio = await get_studio_by_id(studio_id)
        await query.message.answer(f'{studio.name}:', reply_markup=movies_markup)
    else:
        await query.message.answer('Фильмов для выбранной киностудии нет.')

@router_u.callback_query(F.data.startswith("return_to_menu"))
async def return_to_menu(query: types.CallbackQuery):
    user_id = query.from_user.id
    await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu(user_id, is_user_registered_db))

@router_u.callback_query(F.data.startswith("movie_id:"))
async def movie_details(query: types.CallbackQuery):
    user_id = query.from_user.id 
    is_registered = await is_user_registered_db(user_id)
    movie_id_str = query.data.split(":")[1].split("_")[0]
    movie_id = int(movie_id_str)
    movie = await get_movie_by_id(movie_id)
    if movie:
        genre = await get_genre_by_id(movie.genre_id)
        studio = await get_studio_by_id(movie.studio_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [await kb.rent_movie_button(movie_id)] if is_registered else [],
            [await kb.return_to_menu()]
        ])
        await query.message.answer(
            f'<b>{movie.name}</b>\n\n'
            f'<i>Режиссер:</i> {movie.fio_director}\n'
            f'<i>Жанр:</i> {genre.name}\n'
            f'<i>Киностудии:</i> {studio.name}\n'
            f'<i>Актёры в главных ролях:</i> {movie.performers_of_the_main_roles}\n'
            f'<i>Год выпуска:</i> {movie.year_of_release}\n\n'
            f'<i>Описание:</i> {movie.annotation}\n\n'
            f'<i>Стоимость аренды:</i> <b>{movie.cost}₽/сутки</b>\n', reply_markup=keyboard)
    else:
        await query.message.answer('Фильм не найден в базе данных.')

@router_u.callback_query(F.data.startswith("rent_movie:"))
async def rent_movie(query: types.CallbackQuery):
    user_id = query.from_user.id
    movie_id = int(query.data.split(":")[1])
    is_registered = await is_user_registered_db(user_id)
    if not is_registered:
        await query.message.answer("Для аренды фильма необходимо зарегистрироваться. Воспользуйтесь командой /start")
        return
    user_data = await get_user_data(user_id)
    await save_arenda_data(movie_id, user_data.passport)
    await query.message.answer("Фильм взят в аренду! 🎉")
    await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu(user_id, is_user_registered_db))

@router_u.callback_query(F.data.startswith("finish_rental"))
async def finish_rental(query: types.CallbackQuery):
    _, arenda_id = query.data.split(":")
    user_id = query.from_user.id
    success = await finish_rental_in_db(arenda_id, user_id)
    if success:
        await query.answer("Аренда успешно завершена!")
        await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu(user_id, is_user_registered_db))
    else:
        await query.answer("Ошибка: аренда не найдена или не принадлежит текущему пользователю.")
        await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu(user_id, is_user_registered_db))
        
@router_u.message(AddNewUser.passport)
async def process_passport(message: Message, state: FSMContext) -> None:
    await state.update_data(passport=message.text)
    await message.answer("Теперь введите ваше ФИО.")
    await state.set_state(AddNewUser.fio_klient)

@router_u.message(AddNewUser.fio_klient)
async def process_fio(message: Message, state: FSMContext) -> None:
    await state.update_data(fio_klient=message.text)
    await message.answer("Теперь введите ваш адрес.")
    await state.set_state(AddNewUser.adress)

@router_u.message(AddNewUser.adress)
async def process_address(message: Message, state: FSMContext) -> None:
    await state.update_data(address=message.text)
    await message.answer("Теперь введите ваш номер телефона цифрами")
    await state.set_state(AddNewUser.phone_number)

@router_u.message(AddNewUser.phone_number)
async def process_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    message_text = (
        f"Спасибо за регистрацию!\n\n"
        f"Паспорт: <b>{data['passport']}</b>\n"
        f"ФИО: <b>{data['fio_klient']}</b>\n"
        f"Адрес: <b>{data['address']}</b>\n"
        f"Номер телефона: <b>{data['phone_number']}</b>\n\n"
        f"Если все верно, нажмите на кнопку снизу")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Всё верно", callback_data="register")]])
    await message.answer(message_text, reply_markup=keyboard)

@router_u.callback_query(F.data.startswith("register"))
async def register_user(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    await save_user_to_db(query.from_user.id, data)
    await state.clear()
    await query.message.answer("Регистрация завершена. Спасибо за регистрацию!")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu(user_id, is_user_registered_db))
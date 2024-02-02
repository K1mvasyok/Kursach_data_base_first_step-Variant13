import pandas as pd
import io
import os
import tempfile
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime 


import app.keyboards as kb
from app.database.requests_a import get_movies_in_rent, get_movies_over_10_days, save_movie_to_db, get_all_movies, delete_movie_by_id, save_genre_to_db, save_studio_to_db
from config import ADMIN_TELEGRAM_ID

router_a = Router()

class AddMovieStates(StatesGroup):
    name = State()
    director = State()
    genre = State()
    studio = State()
    actors = State()
    year = State()
    annotation = State()
    cost = State()

class AddGenryStates(StatesGroup):
    name_genre = State()

class AddStudioStates(StatesGroup):
    name_studio = State()
    country_studio = State()

@router_a.message(Command("commands"))
async def start_add_movie(message: Message, state: FSMContext) -> None:
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f"Список всех доступных команд\n\n "
                             f"/movies_in_rent - Отчёт о всех фильмов находящихся в аренде, с краткой информацией о пользователе\n\n"
                             f"/movies_overdue - Отчёт о всех фильмов находящихся в аренде, более 10-ти дней, с краткой информацией о пользователе\n\n"
                             f"/add_movie - Запуск процесса добавления нового фильма в базу данных\n\n"
                             f"/add_genre - Запуск процесса добавления нового жанра в базу данных\n\n"
                             f"/add_studio - Запуск процесса добавления новой киностудии в базу данных\n\n"                             
                             f"/delete_movie - Удаление фильма из базы данных\n\n")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

            
@router_a.message(Command("movies_in_rent"))
async def movies_in_rent(message: types.Message):
    movies_in_rent_data = await get_movies_in_rent()
    await send_movies_data(message, movies_in_rent_data, 'Фильмов в аренде')

@router_a.message(Command("movies_overdue"))
async def movies_overdue(message: types.Message):
    movies_overdue_data = await get_movies_over_10_days()
    await send_movies_data(message, movies_overdue_data, 'Фильмы в аренде больше 10-ти дней')

async def send_movies_data(message, movies_data, message_text):
    user_id = message.from_user.id
    if user_id == ADMIN_TELEGRAM_ID:
        if movies_data:
            # Создаем DataFrame из списка
            df = pd.DataFrame([{
                "Movie_Name": movie.name,
                "Arenda_Start_Date": arenda.time_to_start,
                "Klient_ID": klient.id,
                "Klient_FIO": klient.fio_klient,
                "Klient_Telegram_ID": klient.telegram_id,
            } for movie, arenda, klient in movies_data], columns=["Movie_Name", "Arenda_Start_Date", "Klient_ID", "Klient_FIO", "Klient_Telegram_ID"])

            # Добавляем текущую дату в первую строку данных
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header_df = pd.DataFrame([{"Дата создания файла": current_date}])
            df = pd.concat([header_df, df], ignore_index=True)

            excel_content = io.BytesIO()
            with pd.ExcelWriter(excel_content, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Sheet1", index=False)
                worksheet = writer.sheets["Sheet1"]
                # Расширяем столбцы по ширине данных
                for i, col in enumerate(df.columns):
                    max_len = df[col].astype(str).apply(len).max()
                    worksheet.set_column(i, i, max_len + 2)  # +2 для дополнительного пространства
    
            # Отправляем Excel-файл с использованием BufferedInputFile
            input_file = BufferedInputFile(excel_content.getvalue(), filename="send_movies_data.xlsx")
            await message.answer_document(input_file, caption=message_text)
        else:
            await message.answer(f'Ошибка - не получается получить отчёт.')
    else:
        await message.answer('У вас нет прав на выполнение этой команды.')

# Процесс добавления фильма администратором
@router_a.message(Command("add_movie"))
async def start_add_movie(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer("Давайте добавим новый фильм. Введите название фильма:")
        await state.set_state(AddMovieStates.name)
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.message(AddMovieStates.name)
async def process_movie_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите режиссера фильма:")
    await state.set_state(AddMovieStates.director)

@router_a.message(AddMovieStates.director)
async def process_movie_director(message: Message, state: FSMContext):
    await state.update_data(director=message.text)
    await message.answer("Выберите существующий жанр", reply_markup=await kb.genre_for_add_movie())
    
@router_a.callback_query(F.data.startswith("add_movie_genre_name:"))
async def process_selected_genre(query: types.CallbackQuery, state: FSMContext):
    genre = query.data.split(":")[1]
    await state.update_data(genre=genre)    
    await query.message.answer("Выберите существующую киностудию", reply_markup=await kb.studio_for_add_movie())

@router_a.callback_query(F.data.startswith("add_movie_studio_name:"))
async def process_selected_genre(query: types.CallbackQuery, state: FSMContext):
    studio_id = query.data.split(":")[1]
    await state.update_data(studio=studio_id)
    await query.message.answer("Введите актеров фильма:")      
    await state.set_state(AddMovieStates.actors)

@router_a.message(AddMovieStates.actors)
async def process_movie_actors(message: Message, state: FSMContext):
    await state.update_data(actors=message.text)
    await message.answer("Введите год выпуска:")
    await state.set_state(AddMovieStates.year)

@router_a.message(AddMovieStates.year)
async def process_movie_year(message: Message, state: FSMContext):
    year = int(message.text)
    await state.update_data(year=year)
    await message.answer("Введите аннотацию к фильму:")
    await state.set_state(AddMovieStates.annotation)

@router_a.message(AddMovieStates.annotation)
async def process_movie_annotation(message: Message, state: FSMContext):
    annotation_text = message.text
    if annotation_text:
        await state.update_data(annotation=annotation_text)
        await message.answer("Введите стоимость аренды:")
        await state.set_state(AddMovieStates.cost)
    else:
        await message.answer("Введите корректную аннотацию к фильму. Попробуйте снова:")

@router_a.message(AddMovieStates.cost)
async def process_movie_cost(message: Message, state: FSMContext):
    cost = float(message.text)
    await state.update_data(cost=cost)
    data = await state.get_data()
    await save_movie_to_db(data)
    await message.answer("Фильм успешно добавлен в базу данных!")
    await show_movie_summary(message=message, data=data)
    await state.clear()      

async def show_movie_summary(message: Message, data: dict):
    text = (f"Добавлен новый фильм:\n\n"
           f"Название: <b>{data['name']}</b>\n"
           f"Режиссер: <b>{data['director']}</b>\n" 
           f"Жанр: <b>{data['genre']}</b>\n" 
           f"Киностудия: <b>{data['studio']}</b>\n" 
           f"Актеры: <b>{data['actors']}</b>\n" 
           f"Год выпуска: <b>{data['year']}</b>\n" 
           f"Аннотация: <b>{data['annotation']}</b>\n" 
           f"Стоимость аренды: <b>{data['cost']}</b>\n")
    await message.answer(text)
    
# Процесс удаления фильма администратором    
@router_a.message(Command("delete_movie"))
async def delete_movie_command(message: Message):
    inline_keyboard = await kb.create_delete_movie_keyboard()
    await message.answer("Выберите фильм для удаления:", reply_markup=inline_keyboard)
    
@router_a.callback_query(F.data.startswith("delete_movie:"))
async def delete_movie_callback(query: types.CallbackQuery):
    movie_id = int(query.data.split(":")[1])
    await delete_movie_by_id(movie_id)
    await query.message.answer(f"Фильм успешно удален из базы данных!")

# Процесс добавления жанра администратором
@router_a.message(Command("add_genre"))
async def start_add_genry(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer("Давайте добавим новый жанр. Введите название жанра:")
        await state.set_state(AddGenryStates.name_genre)        
    else:
        await message.answer('У вас нет прав на выполнение этой команды.')
        
@router_a.message(AddGenryStates.name_genre)
async def process_genry(message: Message, state: FSMContext):
    await state.update_data(name_genre=message.text)
    data = await state.get_data()
    await save_genre_to_db(data)
    await show_genry_summary(message=message, data=data)    
    await message.answer("Жанр успешно добавлен в базу данных!")
    await state.clear()
    
async def show_genry_summary(message: Message, data: dict):
    text = (f"Добавлен новый жанр:\n\n"
           f"Название: <b>{data['name_genre']}</b>\n")
    await message.answer(text)
    
# Процесс добавления киностудии администратором
@router_a.message(Command("add_studio"))
async def start_add_studio(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer("Давайте добавую киностудию. Введите название киностудии:")
        await state.set_state(AddStudioStates.name_studio)        
    else:
        await message.answer('У вас нет прав на выполнение этой команды.')
        
@router_a.message(AddStudioStates.name_studio)
async def process_studio_name(message: Message, state: FSMContext):
    await state.update_data(name_studio=message.text)  
    await message.answer("Введите страны киностудии:")
    await state.set_state(AddStudioStates.country_studio)
    
@router_a.message(AddStudioStates.country_studio)
async def process_studio_counry(message: Message, state: FSMContext):
    await state.update_data(country_studio=message.text)
    data = await state.get_data()
    await save_studio_to_db(data)
    await show_studio_summary(message=message, data=data)    
    await message.answer("Жанр успешно добавлен в базу данных!")
    await state.clear()
    
async def show_studio_summary(message: Message, data: dict):
    text = (f"Добавлена новая киностудия:\n\n"
           f"Название: <b>{data['name_studio']}</b>\n"
           f"Страна: <b>{data['country_studio']}</b>\n")
    await message.answer(text)
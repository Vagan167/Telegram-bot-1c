import requests
from bs4 import BeautifulSoup
import schedule
import time
import logging
import asyncio
from prettytable import PrettyTable
from aiogram.types import ParseMode

from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Location
import sqlite3 as sq
import Token as tk
import markups as mk
import Info as i_f
import os

from getpass import getpass

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

# класс для обработчика состояний 
class ProfileMenu(StatesGroup):
    # имя
    create_profile_name = State()
    # пароль
    create_profile_password = State()
    # компания
    create_profile_company = State()
    # должность
    create_profile_position = State()
    # бд
    create_profile_db = State()

class Kon(StatesGroup):
    create_name_kon = State()
    create_company_kon = State()
    create_questions_kon = State()

users_data = {}
buttons_status = {}

# Создаем сессию
session = requests.Session()
session.headers.update(i_f.headers)
# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)
response = requests.request("POST", i_f.data_url, headers=i_f.headers, data=i_f.payload)

# Создаем бота и диспетчерf
bot = Bot(token=tk.token)
dp = Dispatcher(bot, storage=MemoryStorage())

def update_cookies():
    with open('cookies.txt', 'r') as f:
        cookies = f.read().strip()
    headers_two['Cookie'] = cookies

# Основной хэндлер start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup = mk.btn_profile_menu)

# Основной хэндлер для помощи
@dp.message_handler(commands=['help', 'info', 'помощь'])
async def help_process(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"ID этой беседы: {chat_id}")

# хэндлер чтобы узнать id темы в беседе
@dp.message_handler(lambda message: message.text =='id темы')
async def get_thread_id(message: types.Message):
    if message.message_thread_id is not None:
        thread_id = message.message_thread_id
        await message.reply(f"ID этой темы: {thread_id}")

# Хэндлер типа message.text для того чтобы узнать обновление Бухгалтерия БИТ 
@dp.message_handler(lambda message: message.text == 'Узнать текущее обновление Бит(1С:Бухгалтерия предприятия/КОРП 3.0)')
async def s(message: types.Message):
	response = requests.request("POST", i_f.data_url, headers=i_f.headers, data=i_f.payload)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, 'html.parser')
		tr_tags = soup.find_all('tr')
		if not tr_tags:
			logging.info("Теги <tr> не найдены.")
		for index, tag in enumerate(tr_tags):
			if index in [1, 2]:
				td_tags = tag.find_all('td')
				if len(td_tags) >= 4:
					config = td_tags[0].text.strip()
					current_version = td_tags[1].text.strip()
					await bot.send_message(message.chat.id, '--------------------------------------------------')
					#planned_version = td_tags[2].text.strip()
					release_date = td_tags[3].text.strip()                                               
					await bot.send_message(message.chat.id, f'Конфигурация: {config},\nТекущая версия: {current_version},\nДата релиза: {release_date}')
				else:
					logging.error(f'Ошибка при запросе данных: {response.status_code}')
	else:
		logging.error(f'Ошибка при запросе данных: {response.status_code}')

@dp.message_handler(lambda message: message.text == 'Обновление Технологической платформы 8.3')
async def sssss(message: types.Message):
    update_cookies()  # Обновляем куки перед запросом
    response = requests.post(i_f.data_two_url, headers=headers_two, data=i_f.payload_two)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_tags = soup.find_all('tr', {'parent-group': '481'})
        
        if not tr_tags:
            logging.info("Теги <tr> не найдены.")
            return
        
        for index, tag in enumerate(tr_tags):
            if index in [19]:
                td_tags = tag.find_all('td')
                
                if len(td_tags) >= 4:
                    config = td_tags[0].get_text(strip=True)
                    current_version = insert_slash_once(td_tags[1].get_text(strip=True), 9)
                    release_date = insert_slash_once(td_tags[2].get_text(strip=True), 8)
                    
                    message_text = (
                        f"Конфигурация: {config},\n"
                        f"Текущая версия: {current_version},\n"
                        f"Дата релиза: {release_date}"
                    )
                    
                    await bot.send_message(message.chat.id, '--------------------------------------------------')
                    await bot.send_message(message.chat.id, message_text)
                else:
                    logging.error(f'Недостаточно данных в строке: {index}')
    else:
        logging.error(f'Ошибка при запросе данных: {response.status_code}')

# Хэндлер типа message.text для того чтобы узнать обновление ЗУП ITS
@dp.message_handler(lambda message: message.text == 'Узнать текущее обновление')
async def sa(message: types.Message):
    response = requests.post(i_f.data_two_url, headers=i_f.headers_two, data=i_f.payload_two)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_tags = soup.find_all('tr', {'parent-group': '4'})
        
        if not tr_tags:
            logging.info("Теги <tr> не найдены.")
            return
        
        for index, tag in enumerate(tr_tags):
            if index in [59, 61, 62]:
                td_tags = tag.find_all('td')
                
                if len(td_tags) >= 4:
                    config = td_tags[0].get_text(strip=True)
                    current_version = insert_slash_once(td_tags[1].get_text(strip=True), 9)
                    release_date = insert_slash_once(td_tags[2].get_text(strip=True), 8)
                    
                    message_text = (
                        f"Конфигурация: {config},\n"
                        f"Текущая версия: {current_version},\n"
                        f"Дата релиза: {release_date}"
                    )
                    
                    await bot.send_message(message.chat.id, '--------------------------------------------------')
                    await bot.send_message(message.chat.id, message_text)
                else:
                    logging.error(f'Недостаточно данных в строке: {index}')
    else:
        logging.error(f'Ошибка при запросе данных: {response.status_code}')

# Функция для парсинга данных с сайта 1
def parse_site_1():
    response = requests.post(i_f.data_url, headers=i_f.headers, data=i_f.payload)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_tags = soup.find_all('tr')
        data = []
        for index in [1, 2]:
            if index < len(tr_tags):
                td_tags = tr_tags[index].find_all('td')
                if len(td_tags) >= 4:
                    config = td_tags[0].text.strip()
                    current_version = td_tags[1].text.strip()
                    release_date = td_tags[3].text.strip()  # Дату можно игнорировать
                    data.append((config, current_version, release_date))
        return data
    else:
        return []

def parse_site_2():
    response = requests.post(i_f.data_two_url, headers=i_f.headers_two, data=i_f.payload_two)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Парсим два набора данных
        tr_tags = soup.find_all('tr', {'parent-group': '4'})
        tr_tags_two = soup.find_all('tr', {'parent-group': '481'})
        data = []
        data_two = []
        
        # Парсинг первого набора
        for index in [59, 61, 62, 82, 38, 66, 49]:
            if index < len(tr_tags):
                td_tags = tr_tags[index].find_all('td')
                if len(td_tags) >= 4:
                    config = td_tags[0].text.strip()
                    current_version = td_tags[1].text.strip()
                    release_date = td_tags[2].text.strip()
                    data.append((config, current_version, release_date))

        
        # Парсинг второго набора
        for index in [19]:
            if index < len(tr_tags_two):
                td_tags_two = tr_tags_two[index].find_all('td')
                if len(td_tags_two) >= 4:
                    config = td_tags_two[0].text.strip()
                    current_version = td_tags_two[1].text.strip()
                    release_date = td_tags_two[2].text.strip()
                    data_two.append((config, current_version, release_date))

        return data, data_two
    else:
        return [], []

# Функция для получения данных из базы данных
def get_db_data():
    with sq.connect('sq_baze/profil/profile.db') as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, CONFIG TEXT, VERSION TEXT, DATA TEXT)")
        cur.execute("SELECT * FROM users")
        return {row[0]: (row[1], row[2], row[3]) for row in cur.fetchall()}

# Функция для обновления базы данных
def update_db(new_data):
    with sq.connect('sq_baze/profil/profile.db') as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, CONFIG TEXT, VERSION TEXT, DATA TEXT)")
        
        # Получаем существующие записи
        cur.execute("SELECT * FROM users")
        existing_ids = {row[0]: row for row in cur.fetchall()}

        # Обновляем или вставляем новые записи
        for index, (config, version, release_date) in enumerate(new_data, start=1):
            if index in existing_ids:
                cur.execute("UPDATE users SET CONFIG = ?, VERSION = ?, DATA = ? WHERE id = ?", 
                            (config, version, release_date, index))
            else:
                cur.execute("INSERT INTO users (id, CONFIG, VERSION, DATA) VALUES (?, ?, ?, ?)", 
                            (index, config, version, release_date))
        con.commit()

# Хэндлер для сравнения данных
@dp.message_handler(lambda message: message.text.lower() == 'сравнить данные')
async def compare_data(message: types.Message):
    # Парсим данные с обоих сайтов
    site_1_data = parse_site_1()
    site_2_data, site_2_data_two = parse_site_2()  # Парсим данные с сайта 2
    
    # Объединяем все данные
    all_data = site_1_data + site_2_data + site_2_data_two
    
    # Получаем данные из базы данных
    db_data = get_db_data()
    
    # Обновляем базу данных с новыми данными
    update_db(all_data)

    # Проверка изменений
    updates = []
    for idx, (config, version, _) in enumerate(all_data, start=1):
        if idx in db_data:
            db_config, db_version, _ = db_data[idx]
            if (config, version) != (db_config, db_version):
                updates.append(f"Конфигурация: {config}, Версия: {version}")
        else:
            updates.append(f"Конфигурация: {config}, Версия: {version}")
    
    # Отправка обновлений пользователю
    if updates:
        update_message = "\n".join(updates)
        await bot.send_message(message.chat.id, f"Обновления найдены:\n{update_message}")
    else:
        await bot.send_message(message.chat.id, "Обновлений нет.")

# Функция для вставки слэша
def insert_slash_once(text, n):
    if len(text) > n:
        return text[:n] + '/' + text[n:]
    return text

# Заявка типа message.text для того чтобы клиент создал заявку на создание пользователя в 1с
@dp.message_handler(lambda message: message.text == 'Заявка на создание пользователя в 1С')
async def create_profile_1c(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Напишите ФИО')
    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            user_id INTEGER,  -- Добавляем поле для user_id
            NAME TEXT,
            PASSWORD TEXT,
            COMPANY TEXT,
            message_id TEXT,
            db TEXT,
            que TEXT
        )""")
        con.commit()
    # Сохраняем ID пользователя сразу при создании заявки
    async with state.proxy() as data:
        data['id'] = message.from_user.id
        users_data[message.from_user.id] = data

    await ProfileMenu.create_profile_name.set()

# обработчик состояний для заявки имя
@dp.message_handler(state=ProfileMenu.create_profile_name)
async def time_profile_name(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Напишите пароль')
    async with state.proxy() as data:
        data['name'] = message.text
    await ProfileMenu.create_profile_password.set()

# обработчик состояний для заявки пароль
@dp.message_handler(state=ProfileMenu.create_profile_password)
async def time_profile_password(message:  types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Напишите название компании в которой вы работаете')
    async with state.proxy() as data:
        data['password'] = message.text
    await ProfileMenu.create_profile_company.set()

# обработчик состояний для заявки компания
@dp.message_handler(state=ProfileMenu.create_profile_company)
async def time_profile_company(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Какая у вас должность?')
    async with state.proxy() as data:
        data['company'] = message.text
    await ProfileMenu.create_profile_position.set()

# Хэндлер для завершения заявки с кнопкой "Отменить заявку"
@dp.message_handler(state=ProfileMenu.create_profile_position)
async def time_profile_position(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Какая база данных?(К примеру: База данных Бухгалтерия или Зарплата и управление персоналом и т.д)')
    async with state.proxy() as data:
        data['position'] = message.text
    await ProfileMenu.create_profile_db.set()

@dp.message_handler(state=ProfileMenu.create_profile_db)
async def time_profile_position(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['db'] = message.text

    # Генерация уникального идентификатора для заявки
    request_id = f"{message.from_user.id}_{int(time.time())}"
    
    result_message = (
        f"Новая заявка на создание пользователя:\n"
        f"ФИО: {data['name']}\n"
        f"Пароль: {data['password']}\n"
        f"Компания: {data['company']}\n"
        f"Должность: {data['position']}\n"
        f"База данных: {data['db']}\n"
    )

    # Создание инлайн-кнопок "Создать пользователя" и "Отменить заявку"
    markup = InlineKeyboardMarkup()
    create_button = InlineKeyboardButton(text="Создать пользователя", callback_data=f'user_created_{request_id}')
    cancel_button = InlineKeyboardButton(text="Отменить заявку", callback_data=f'user_created_Otmena_{request_id}')
    
    markup.add(create_button, cancel_button)

    # Определяем chat_id и thread_id для отправки сообщения
    chat_id = -1002166563393
    thread_id = 10

    # Отправляем сообщение с инлайн-кнопками в нужный чат
    sent_message = await bot.send_message(chat_id, result_message, message_thread_id=thread_id, reply_markup=markup)

    # Сохраняем ID отправленного сообщения
    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (id, user_id, NAME, PASSWORD, COMPANY, message_id, db) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (request_id, message.from_user.id, data['name'], data['password'], data['company'], sent_message.message_id, data['db']))
        con.commit()

    await message.reply('Заявка рассматривается! Бот вам напишет, когда пользователь будет создан.')
    await state.finish()

# Хэндлер типа message.text для того чтобы узнать обновление ЗУП ITS
@dp.message_handler(lambda message: message.text == 'Заявка на консультацию с IT работником компании "ALGORITM23"')
async def sa(message: types.Message, state: FSMContext):
    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            user_id INTEGER,  -- Добавляем поле для user_id
            NAME TEXT,
            PASSWORD TEXT,
            COMPANY TEXT,
            message_id TEXT,
            db TEXT,
            que TEXT
        )""")
        con.commit()  

    await bot.send_message(message.chat.id, 'Напишите ФИО')
    async with state.proxy() as data:
        data['username'] = message.from_user.username
        data['id_two'] = message.from_user.id
        users_data[message.from_user.id] = data

    await Kon.create_name_kon.set()

@dp.message_handler(state=Kon.create_name_kon)
async def name_kon(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Напишите название компании в которой вы работаете.')
    async with state.proxy() as data:
        data['name_two'] = message.text
    await Kon.create_company_kon.set()

@dp.message_handler(state=Kon.create_company_kon)
async def company_kon(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Задайте вопрос.')
    async with state.proxy() as data:
        data['company_two'] = message.text
    await Kon.create_questions_kon.set()

@dp.message_handler(state=Kon.create_questions_kon)
async def questions_kon(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['que'] = message.text
    # Генерация уникального идентификатора для заявки
    request_id = f"{message.from_user.id}_{int(time.time())}"
    result_message = (
        f"Запрос на консультацию:\n"
        f"ФИО: {data['name_two']}\n"
        f"Компания: {data['company_two']}\n"
        f"Вопрос: {data['que']}\n"
        f"Телеграмм клиента: <a href='https://t.me/{data['username']}'>@{data['username']}</a>\n"
    )

    # Создание инлайн-кнопок "Создать пользователя" и "Отменить заявку"
    markup = InlineKeyboardMarkup()
    cancel_button = InlineKeyboardButton(text="Отменить заявку", callback_data=f'user_created_Otmena_{request_id}')
    
    markup.add(cancel_button)

    # Определяем chat_id и thread_id для отправки сообщения
    chat_id = -1002166563393
    thread_id = 10

    # Отправляем сообщение с инлайн-кнопками в нужный чат
    sent_message = await bot.send_message(chat_id, result_message, parse_mode=ParseMode.HTML, message_thread_id=thread_id, reply_markup=markup)

    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (id, user_id, NAME, COMPANY, message_id, que) VALUES (?, ?, ?, ?, ?, ?)",
                    (request_id, message.from_user.id, data['name_two'], data['company_two'], sent_message.message_id, data['que']))
        con.commit()
    # Сохраняем ID отправленного сообщения
    await message.reply('Заявка рассматривается! Сотрудник вам напишет в личные сообщения.')
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('user_created_') and not c.data.startswith('user_created_Otmena_'))
async def process_callback_button_create(callback_query: types.CallbackQuery):
    request_id = callback_query.data.replace('user_created_', '')

    # Открываем соединение с базой данных
    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        # Извлекаем данные пользователя из базы данных по request_id
        cur.execute("SELECT user_id, NAME, PASSWORD, COMPANY, db FROM users WHERE id = ?", (request_id,))
        result = cur.fetchone()

        if result:  # Если заявка найдена
            user_id, name, password, company, db = result

            # Здесь идет логика создания пользователя в 1С
            # Для демонстрации используем сообщение о создании пользователя
            await bot.send_message(user_id, f"Ваш аккаунт создан.\nИмя: {name}\nПароль: {password}\nБаза данных: {db}")
            
            # Уведомляем администраторов о создании пользователя
            await bot.send_message(callback_query.message.chat.id, 'Пользователь успешно создан.', message_thread_id=callback_query.message.message_thread_id)

            # Удаляем заявку из базы данных после успешного создания пользователя
            cur.execute("DELETE FROM users WHERE id = ?", (request_id,))
            con.commit()
        else:
            # Если заявка не найдена
            await bot.send_message(callback_query.message.chat.id, 'Ошибка: Заявка не найдена.', message_thread_id=callback_query.message.message_thread_id)

    # Отправляем ответ на callback, чтобы убрать "крутящийся" индикатор
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('user_created_Otmena_'))
async def process_callback_button_Otmena(callback_query: types.CallbackQuery):
    request_id = callback_query.data.replace('user_created_Otmena_', '')
    
    chat_id = -1002166563393
    thread_id = 10

    with sq.connect('sq_baze/profil/USER.db') as con:
        cur = con.cursor()
        # Извлекаем user_id и message_id для удаления сообщения
        cur.execute("SELECT user_id, message_id FROM users WHERE id = ?", (request_id,))
        result = cur.fetchone()

        if result:  # Заявка найдена
            user_id, message_id = result

            # Удаляем заявку из базы данных
            cur.execute("DELETE FROM users WHERE id = ?", (request_id,))
            con.commit()

            # Отправляем уведомление пользователю об отмене заявки
            await bot.send_message(user_id, "Заявка была отклонена.Попробуйте заного создать заявку или обратитесь к IT сотруднику компании 'ALGORITM23'")
            await bot.send_message(chat_id, 'Заявка отклонена.', message_thread_id=thread_id)

            # Удаляем сообщение с заявкой из беседы
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            # Логируем ошибку, если заявка не найдена
            await bot.send_message(chat_id, 'Ошибка: Заявка не найдена.', message_thread_id=thread_id)

    await callback_query.answer()



# Запуск бота
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, loop=loop, skip_updates=True)
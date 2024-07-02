import asyncio
import pandas as pd
import db
from cfg import *

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    db.create_table()

    user_id = message.from_user.id
    is_registered = db.check_if_user_registered(user_id)

    if not is_registered:
        await UserInput.waiting_for_last_name.set()
        await message.answer("Привет! Вводи свои данные с учётом регистров, иначе есть шанс неудачной регистрации.\n\nВведи свою фамилию:")
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        chs_block = KeyboardButton("Выбрать блок")
        tech_sup = KeyboardButton("Написать в техподдержку")
        keyboard.add(chs_block, tech_sup)
        await message.answer("Вы уже зарегистрированы.", reply_markup=keyboard)

@dp.message_handler(state=UserInput.waiting_for_last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["last_name"] = message.text
    await state.update_data(user_data)
    await message.answer("Теперь введи свое полное имя:")
    await UserInput.next()

@dp.message_handler(state=UserInput.waiting_for_first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["first_name"] = message.text
    await state.update_data(user_data)
    await message.answer("Введи номер блока\nПример: 101:")
    await UserInput.next()

@dp.message_handler(state=UserInput.waiting_for_block_number)
async def get_block_number(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if len(message.text) != 3 or not message.text.isdigit():
        await message.answer("Номер блока должен состоять из 3 цифр. Попробуйте снова:")
        return

    user_data["block_number"] = message.text
    await state.update_data(user_data)
    await message.answer("Введи номер комнаты (2/3):")
    await UserInput.next()

@dp.message_handler(state=UserInput.waiting_for_room_number)
async def get_room_number(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    id = message.from_user.id

    if len(message.text) != 1 or not message.text.isdigit():
        await message.answer("Номер комнаты должен состоять из 1 цифры. Попробуйте снова:")
        return

    user_data["room_number"] = message.text
    await state.update_data(user_data)

    await state.finish()

    last_name = user_data["last_name"]
    first_name = user_data["first_name"]
    block_number = user_data["block_number"]
    room_number = user_data["room_number"]

    table = pd.read_excel('Obshaga.xlsx', engine="openpyxl")

    is_user_exist = (table['last_name'] == last_name) & (table['first_name'] == first_name)

    if is_user_exist.any():
        await message.answer("Пользователь найден в общежитии. Добавление в базу данных...")
        db.add_user(id, last_name, first_name, block_number, room_number)
        await message.answer("Данные успешно добавлены в базу данных.")

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        chs_block = KeyboardButton("Выбрать блок")
        tech_sup = KeyboardButton("Написать в техподдержку")
        keyboard.add(chs_block, tech_sup)

        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer("Такой человек в общежитии не проживает.")

# ============= Choose block ===========
@dp.message_handler(lambda message: message.text == "Написать в техподдержку", state="*")
async def tech_sup(message: types.Message):
    user_id = message.from_user.id
    is_registered = db.check_if_user_registered(user_id)

    if is_registered:
        await message.answer(f"Писать в случае:\n-Бот неисравен\n-Ввели некорректные данные\n-Выселились/Переселились\n\nКонтакты: {tech_help}")
    else:
        await message.answer("Не смог найти вас в базе данных. Пропишите /start.")

@dp.message_handler(lambda message: message.text == "Выбрать блок", state="*")
async def choose_block(message: types.Message):
    user_id = message.from_user.id
    is_registered = db.check_if_user_registered(user_id)

    if is_registered:
        await UserInput.waiting_for_block_to_choose.set()
        await message.answer("Введите номер блока:")
    else:
        await message.answer("Не смог найти вас в базе данных. Пропишите /start.")


@dp.message_handler(state=UserInput.waiting_for_block_to_choose)
async def get_block_to_choose(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["block_number"] = message.text
    await state.update_data(user_data)
    await message.answer("Введите номер комнаты:")
    await UserInput.next()


@dp.message_handler(state=UserInput.waiting_for_room_to_choose)
async def get_room_to_choose(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    user_data["room_number"] = message.text
    await state.update_data(user_data)

    block_number = user_data["block_number"]
    room_number = user_data["room_number"]

    if not block_number.isdigit() or not room_number.isdigit():
        await message.answer("Номер блока и комнаты должны быть числами. Пожалуйста, введите их снова.")
        await state.set_state(UserInput.waiting_for_block_to_choose.state)
        return

    if db.check_room_exists(block_number, room_number):
        inline_chsbl = types.InlineKeyboardMarkup()
        resget = types.InlineKeyboardButton('Узнать проживающих', callback_data='get_residents')
        wrmsg = types.InlineKeyboardButton('Написать сообщение', callback_data='write_message')
        inline_chsbl.add(resget, wrmsg)
        await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=inline_chsbl)
    else:
        await message.answer("Такого блока или комнаты не существует. Введите другой № блока.")
        await state.set_state(UserInput.waiting_for_block_to_choose.state)


@dp.callback_query_handler(lambda c: c.data == 'get_residents', state="*")
async def show_residents(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    block_number = user_data["block_number"]
    room_number= user_data["room_number"]

    residents = db.get_residents(block_number, room_number)

    if residents:
        residents_str = "\n".join([f"{resident[1]} {resident[2]}" for resident in residents])
        await bot.send_message(callback_query.from_user.id, f"Проживающие в {block_number}/{room_number}:\n{residents_str}")
    else:
        await bot.send_message(callback_query.from_user.id, "В этой комнате никто не проживает.")

@dp.callback_query_handler(lambda c: c.data == 'write_message', state="*")
async def ask_for_message_text(callback_query: types.CallbackQuery, state: FSMContext):
    await UserInput.waiting_for_message_text.set()
    await bot.send_message(callback_query.from_user.id, "Введите текст сообщения:")

@dp.message_handler(state=UserInput.waiting_for_message_text)
async def send_message_to_residents(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    block_number = user_data["block_number"]
    room_number= user_data["room_number"]

    residents = db.get_residents(block_number, room_number)

    if residents:
        full_name = db.get_name_from_db(message.from_user.id)
        if full_name is not None:
            message_text = message.text + "\n\nОтправлено от {}".format(full_name)
        else:
            message_text = message.text + "\n\nОтправлено от {}".format(message.from_user.full_name)
        await send_messages_to_residents(residents, message_text, message)
        await message.answer("Сообщение успешно отправлено.")
    else:
        await message.answer("В этой комнате никто не проживает.")

    await state.finish()

async def send_messages_to_residents(residents, message_text, message):
    for resident in residents:
        keyboard = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton('Ответить', callback_data=f'reply_{message.from_user.id}')
        keyboard.add(reply_button)
        await bot.send_message(resident[0], message_text, parse_mode='Markdown', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('reply_'))
async def reply_message(callback_query: types.CallbackQuery, state: FSMContext):
    sender_id = callback_query.data.split('_')[1]

    await state.update_data(sender_id=sender_id)

    await UserInput.waiting_for_response.set()

    await bot.send_message(callback_query.from_user.id, "Введите ваш ответ:")

@dp.message_handler(state=UserInput.waiting_for_response)
async def send_response(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sender_id = data['sender_id']

    response_text = message.text

    full_name = db.get_name_from_db(message.from_user.id)

    await bot.send_message(sender_id, f"Ответ от {full_name}:\n\n{response_text}")

    await state.finish()

# =========================================

if __name__ == "__main__":
    asyncio.run(dp.start_polling())

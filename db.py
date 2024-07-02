import sqlite3

def connect_to_database():
    """
    Подключение к базе данных residents.db.

    Returns:
        sqlite3.Connection: Объект соединения.
    """

    return sqlite3.connect("residents.db")


def create_table():
    """
    Создание таблицы users.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        block_number INTEGER NOT NULL,
        room_number INTEGER NOT NULL,
        admin INTEGER DEFAULT 0
    );
    """)

    connection.commit()
    connection.close()



def add_user(id, last_name, first_name, block_number, room_number):
    """
    Добавление пользователя в таблицу.

    Args:
        last_name (str): Фамилия.
        first_name (str): Имя.
        block_number (int): Номер блока.
        room_number (int): Номер комнаты.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO users (id, last_name, first_name, block_number, room_number)
    VALUES (?, ?, ?, ?, ?)
    """, (id, last_name, first_name, block_number, room_number))

    connection.commit()
    connection.close()


def check_room_exists(block_number, room_number):
    """
    Проверка, существует ли комната.

    Args:
        block_number (int): Номер блока.
        room_number (int): Номер комнаты.

    Returns:
        bool: True, если комната существует, False - otherwise.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM users
    WHERE block_number = ? AND room_number = ?
    """, (block_number, room_number))


    room_exists = cursor.fetchone()[0]

    connection.close()

    return bool(room_exists)


def get_residents(block_number, room_number):
    """
    Получение списка жильцов.

    Args:
        block_number (int): Номер блока.
        room_number (int): Номер комнаты.

    Returns:
        list: Список жильцов.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, last_name, first_name FROM users
    WHERE block_number = ? AND room_number = ?
    """, (block_number, room_number))

    residents = cursor.fetchall()

    connection.close()

    return residents


def check_if_user_registered(user_id):
    """
    Проверка регистрации пользователя.

    Args:
        user_id (int): ID пользователя.

    Returns:
        bool: True, если пользователь зарегистрирован, False - otherwise.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM users
    WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()[0]

    connection.close()

    return bool(result)


def get_name_from_db(user_id):
    """
    Получение имени пользователя.

    Args:
        user_id (int): ID пользователя.

    Returns:
        str: Имя пользователя.
    """

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT first_name, last_name FROM users
    WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    if result:
        first_name, last_name = result
        return f"{first_name} {last_name}"
    else:
        return None

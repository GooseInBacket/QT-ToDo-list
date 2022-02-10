import sqlite3
# from datetime import datetime
from typing import Tuple
from loguru import logger


class DataBase:
    """Класс работы с БД"""

    def __init__(self):
        self.__connect = sqlite3.connect('data.sqlite3')
        self.__cursor = self.__connect.cursor()
        self.create_items_table()
        self.create_new_table()
        if not self.get_all_items():
            self.set_default_item()

    def add_task_to(self, table_name: str, task: Tuple[str], date) -> None:
        """Добавить задачу в указанную таблицу"""
        self.__cursor.execute(f'''INSERT INTO {table_name} VALUES(?, ?, ?)''', (task, 0, date))
        if table_name != 'Все':
            self.__cursor.execute(f'''INSERT INTO Все VALUES(?, ?, ?)''', (task, 0, date))
        self.__connect.commit()
        logger.success(f'"{task}" на дату {date} удачно добавлен в "{table_name}"')

    def add_new_item_in_main_list(self, item: Tuple[str]) -> None:
        """Добавить элементы в таблицу главного окна"""
        self.__cursor.execute('INSERT INTO main_items VALUES(?);', item)
        item = '_'.join(item[0].split())
        self.__cursor.execute(f"""CREATE TABLE IF NOT EXISTS {item}
        (items TEXT, 
        status INTEGER, 
        data timestamp);""")
        self.__connect.commit()
        logger.success(f'"{item}" удачно добавлен в главное меню')

    def create_items_table(self) -> None:
        """Создать новый элемент в таблице главного окна"""
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS main_items(items TEXT);""")
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
        id INTEGER,
        color TEXT, 
        font INTEGER, 
        icon INTEGER);""")

    def create_new_table(self) -> None:
        """
        Создать новую таблицу в БД из списка элементов таблицы главного окна
        :return: None
        """
        list_table = map(lambda x: x[0], self.get_all_items())
        for name in list_table:
            name = '_'.join(name.split())
            self.__cursor.execute(f"""CREATE TABLE IF NOT EXISTS {name}
            (items TEXT, 
            status INTEGER,
            data timestamp);""")
        logger.info('Таблицы обновлены')

    def get_all_tasks_from(self, table_name: str) -> list:
        """
        Получить все элементы из указанной таблицы
        :param table_name: имя таблицы
        :return:
        """
        return self.__cursor.execute(f"""SELECT * FROM {table_name}""").fetchall()

    def get_all_items(self) -> list:
        """
        Получить все элементы из таблицы главного окна
        :return: list
        """
        return self.__cursor.execute("SELECT * FROM main_items").fetchall()

    def get_from(self, table_name: str, search: str) -> tuple:
        """
        Получить элемент из указанной таблицы
        :param table_name: имя таблицы
        :param search: элемент поиска
        :return: tuple
        """
        return self.__cursor.execute(
            f"SELECT * FROM {table_name} WHERE items='{search}';").fetchone()

    def set_default_item(self) -> None:
        """Установить дефолтные элементы для главного окна"""
        data = [('Мой день',), ('Важно',), ('Запланировано',), ('Все',),
                ('Завершенные',), ('Назначить мне',), ('Задачи',)]
        settings = (1, "background-color: rgb(255, 255, 255);", 14, 16)

        self.__cursor.executemany("INSERT INTO main_items VALUES(?);", data)
        self.__cursor.execute("INSERT INTO settings VALUES(?, ?, ?, ?);", settings)
        self.__connect.commit()
        logger.info('Элементы главного окна созданы')

    @logger.catch()
    def refresh_status(self, table_name: str, item: str) -> None:
        """
        Обновить статус выполнения элемента в таблицк
        :param table_name: имя таблицы
        :param item: название элемента
        :return: None
        """
        *data, date = self.get_from(table_name, item)
        status = 0 if data[1] else 1

        upd = f"""UPDATE {table_name} SET status = {status} WHERE items = '{item}';"""
        upd_all = f"""UPDATE Все SET status = {status} WHERE items = '{item}';"""
        upd_done = f"""INSERT INTO Завершенные VALUES(?, ?, ?)"""

        self.__cursor.execute(upd)
        self.__cursor.execute(upd_all)
        if status:
            self.__cursor.execute(upd_done, (data[0], status, date))
            self.delete(table_name, data[0])
            self.delete('Все', data[0])
        else:
            self.delete('Завершенные', data[0])

        self.__connect.commit()
        logger.info(f'Элемент "{item}" статус = {status}')

    def delete(self, table_name: str, item: str) -> None:
        """
        Удаление элемента из таблицы
        :param table_name: имя таблицы
        :param item: элемент удлаления
        :return: None
        """
        self.__cursor.execute(f"""DELETE FROM {table_name} WHERE items='{item}';""")
        self.__connect.commit()
        logger.success(f'Элемент "{item}" удалён из таблицы "{table_name}"')

    def delete_table(self, table_name: str) -> None:
        """
        Удаление таблицы из БД
        :param table_name: название таблицы
        :return: None
        """
        self.delete('main_items', table_name)
        table_name = '_'.join(table_name.split())
        self.__cursor.execute(f"""DROP TABLE IF EXISTS {table_name};""")
        self.__connect.commit()
        logger.success(f'Таблица "{table_name}" удалена')

    def edit(self, table_name: str, item: str | int, new_item: str, column='items') -> None:
        """
        Изменения элемента в таблице
        :param table_name: имя таблицы
        :param item: старое название
        :param new_item: новое название
        :param column: колонка в таблице
        :return: None
        """
        self.__cursor.execute(
            f"""UPDATE {table_name} SET {column} = '{new_item}' WHERE items='{item}';""")
        self.__connect.commit()
        logger.success(f'Элемент "{item}" из таблицы "{table_name}" изменен на "{new_item}"')

    def rename_table(self, old_name: str, new_name: str) -> None:
        """
        Переименовать таблицу (пока спорно)
        :param old_name:
        :param new_name:
        :return:
        """
        self.__cursor.execute(
            f'''UPDATE main_items SET items = '{old_name}' WHERE items="{new_name}";''')
        old_name = '_'.join(old_name.split())
        self.__cursor.execute(f"""ALTER TABLE '{old_name}' RENAME TO '{new_name}';""")
        self.__connect.commit()

    def get_settings(self, item: str = '*'):
        return self.__cursor.execute(f"SELECT {item} FROM settings WHERE id=1;").fetchone()[0]

    def update_settings(self, col: str, new_item: str | int, old_item: str | int):
        self.__cursor.execute(
            f"""UPDATE settings SET {col}='{new_item}' WHERE {col}='{old_item}';""")
        self.__connect.commit()
        logger.info(f'Настройки изменены | {col}:{old_item} => {new_item}')

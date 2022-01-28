import sqlite3
from typing import Tuple


class DataBase:
    def __init__(self):
        self.__connect = sqlite3.connect('data.sqlite3')
        self.__cursor = self.__connect.cursor()
        self.create_items_table()
        self.create_new_table()
        if not self.get_all_items():
            self.set_default_item()

    def add_task_to(self, table_name: str, task: Tuple[str]) -> None:
        self.__cursor.execute(f'''INSERT INTO {table_name} VALUES(?, ?)''', (task, 0))
        self.__connect.commit()

    def add_new_item_in_main_list(self, item: Tuple[str]):
        self.__cursor.execute('INSERT INTO main_items VALUES(?);', item)
        item = '_'.join(item[0].split())
        self.__cursor.execute(f"""CREATE TABLE IF NOT EXISTS {item}(items TEXT, status INTEGER);""")
        self.__connect.commit()

    def create_items_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS main_items(items TEXT, 
        status INTEGER);""")

    def create_new_table(self):
        list_table = map(lambda x: x[0], self.get_all_items())
        for name in list_table:
            name = '_'.join(name.split())
            self.__cursor.execute(f"""CREATE TABLE IF NOT EXISTS {name}
            (items TEXT, 
            status INTEGER);""")

    def get_all_tasks_from(self, table_name: str) -> list:
        return self.__cursor.execute(f"""SELECT * FROM {table_name}""").fetchall()

    def get_all_items(self) -> list:
        return self.__cursor.execute("SELECT * FROM main_items").fetchall()

    def get_from(self, table_name: str, search: str) -> tuple:
        return self.__cursor.execute(f"SELECT * FROM {table_name} WHERE items='{search}'").fetchone()

    def set_default_item(self) -> None:
        data = [('Мой день',), ('Важно',), ('Запланировано',), ('Все',),
                ('Завершенные',), ('Назначить мне',), ('Задачи',)]
        self.__cursor.executemany("INSERT INTO main_items VALUES(?);", data)
        self.__connect.commit()

    def refresh_status(self, table_name: str, item: str) -> None:
        status = 0 if self.get_from(table_name, item)[1] else 1
        self.__cursor.execute(
            f"""UPDATE {table_name} SET status = {status} WHERE items = '{item}'""")
        self.__connect.commit()

    def delete(self, table_name: str, item: str) -> None:
        self.__cursor.execute(f"""DELETE FROM {table_name} WHERE items='{item}';""")
        self.__connect.commit()

    def delete_table(self, table_name: str):
        self.delete('main_items', table_name)
        table_name = '_'.join(table_name.split())
        self.__cursor.execute(f"""DROP TABLE IF EXISTS {table_name};""")
        self.__connect.commit()

    def edit(self, table_name: str, item: str | int, new_item: str, column='items'):
        self.__cursor.execute(
            f"""UPDATE {table_name} SET {column} = '{new_item}' WHERE items='{item}'""")
        self.__connect.commit()


# DataBase().delete_table('Еще один')
# DataBase().delete_table('Мой список')

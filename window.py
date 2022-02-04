from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QDate, QTime, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu

from Windows.add_win import Ui_Form
from Windows.task_win import Ui_Form as Task
from Windows.add_task import Ui_Form as Ui_AddTask
from Windows.settings_win import Ui_Form as Ui_Settings

from data_base import DataBase
from datetime import datetime

from loguru import logger
from settings import *

DB = DataBase()


class AddWindow(QWidget, Ui_Form):
    """
    Класс окна добавления нового элемента меню в главном окне
    """
    window_closed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.window_settings()

    @logger.catch(message='Ошибка настроек окна "Создать список"')
    def window_settings(self) -> None:
        # иконка + цвет
        self.setWindowIcon(QIcon(icon_plus))
        self.setStyleSheet(DB.get_settings('color'))

        # кнопки
        self.cancel.clicked.connect(self.quit)
        self.submit.clicked.connect(self.set_item)

        # hotkey
        self.submit.setShortcut('Return')
        self.cancel.setShortcut('Escape')

    def set_item(self) -> None:
        """
        Создать новый список задач
        :return: None
        """
        name = self.name_item.text(),
        if name[0]:
            DB.add_new_item_in_main_list(name)
        self.quit()

    def quit(self) -> None:
        """
        Обработчик выхода из окна добавления элемента
        :return: None
        """
        self.name_item.setText('')
        self.window_closed.emit()
        self.close()


class TaskWindow(QWidget, Task):
    """
    Класс окна со списком задач
    """

    def __init__(self, win_name: str, icon):
        super(TaskWindow, self).__init__()

        self.setupUi(self)

        self.__window_name = '_'.join(win_name.split())
        self.add_win = AddTask(self.__window_name)

        self.window_settings(icon, win_name)
        self.update_tasks()

    @logger.catch(message='Ошибка настроек окна со списком задач')
    def window_settings(self, icon, name):
        self.setWindowIcon(icon)
        self.setWindowTitle(name)
        self.name.setText(name)

        text = f'Сегодня {datetime.today().date()}' if name == 'Мой день' else ''
        self.date.setText(text)

        self.add.setIcon(QIcon(icon_plus))
        self.setStyleSheet(DB.get_settings('color'))

        self.add.clicked.connect(self.add_task)
        self.list_todo.itemDoubleClicked.connect(self.double_clicked)
        self.list_todo.installEventFilter(self)

    def add_task(self) -> None:
        """
        Событие нажатия на кнопку "Добавить задачу"
        :return: None
        """
        self.add_win.window_closed.connect(self.update_tasks)
        self.add_win.show()

    @logger.catch(message='Невозможно обновить список задач')
    def update_tasks(self) -> None:
        self.list_todo.clear()
        for name in map(lambda x: f' {x[0]}', DB.get_all_tasks_from(self.__window_name)):
            self.create_task(name)

    @logger.catch(message='Невозможно создать задачу')
    def create_task(self, name: str) -> None:
        """
        Создать задачу для списка задач
        :param name: текст задачи
        :return: None
        """
        status = DB.get_from(self.__window_name, name[1:])[1]
        icon = QIcon(icon_mark_with_mark) if status else QIcon(icon_mark_round)
        size = DB.get_settings('icon')

        self.list_todo.addItem(QListWidgetItem(icon, name))
        self.list_todo.setIconSize(QSize(size, size))

    def double_clicked(self, item) -> None:
        """
        Обработчик двойного клика по задаче
        :param item: событие нажатия по элементу
        :return: None
        """
        text = item.text()[1:]
        status = DB.get_from(self.__window_name, text)[1]
        DB.refresh_status(self.__window_name, text)
        item.setIcon(QIcon(icon_mark_with_mark) if status else QIcon(icon_mark_round))
        self.update_tasks()

    def eventFilter(self, source, event) -> bool:
        """
        Обработчик контекстного меню
        :return: bool
        """
        if event.type() == QEvent.ContextMenu and source is self.list_todo:
            item = source.itemAt(event.pos())
            if item is not None:
                text = item.text()[1:]

                menu = QMenu()
                delete_action = menu.addAction(QIcon(icon_bin), 'Удалить')
                edit_action = menu.addAction(QIcon(icon_refresh), 'Изменить')
                # move_action = menu.addAction(QIcon(icon_move), 'Перенести в')

                action = menu.exec_(event.globalPos())
                if action == delete_action:
                    self.delete(text)
                elif action == edit_action:
                    self.edit(text, QIcon(edit_action.icon()))
            return True
        return super().eventFilter(source, event)

    @logger.catch(message='Задачу не удаётся удалить')
    def delete(self, item: str) -> None:
        """
        Обработчик события контекстного меню "Удалить"
        :param item: Объект удаления
        :return: None
        """
        DB.delete(self.__window_name, item)
        self.update_tasks()

    @logger.catch(message='Задачу не удаётся изменить')
    def edit(self, item: str, icon: QIcon) -> None:
        """
        Обработчик события контекстного меню "Изменить"
        :param item: имя объекта
        :param icon: иконка объекта
        :return: None
        """
        self.edit_win = EditWin(item, self.__window_name, icon)
        self.edit_win.window_closed.connect(self.update_tasks)
        self.edit_win.show()


class AddTask(QWidget, Ui_AddTask):
    """
    Класс окна добавления элемента в список задач
    """
    window_closed = QtCore.pyqtSignal()

    def __init__(self, window_name: str):
        super(AddTask, self).__init__()
        self.setupUi(self)
        self.window_settings(window_name)

    @logger.catch(message='Ошибка настроек окна "Добавить"')
    def window_settings(self, win_name: str):
        self.setWindowIcon(QIcon(icon_plus))
        self.setStyleSheet(DB.get_settings('color'))
        self.date.setDate(QDate(datetime.today().date()))
        self.date.setTime(QTime(datetime.today().time()))

        # кнопки
        self.cancel.clicked.connect(self.quit)
        self.add.clicked.connect(lambda x: self.set_task(win_name))

        # hotkey
        self.cancel.setShortcut('Escape')
        self.add.setShortcut('Return')

    @logger.catch(message='Невозможно создать задачу')
    def set_task(self, win_name) -> None:
        """
        Обработчик события "Добавить задачу"
        :return: None
        """
        task = self.task_line.text()
        if task:
            DB.add_task_to(win_name, task, self.date.text())
        self.quit()

    def quit(self) -> None:
        """
        Обработчик события "Назад"
        :return: None
        """
        self.task_line.setText('')
        self.window_closed.emit()
        self.close()


class EditWin(QWidget, Ui_Form):
    """
    Класс окна редактирования элементов из контекстного меню
    """
    window_closed = QtCore.pyqtSignal()

    def __init__(self, old_task_name: str | int, name_table: str, icon):
        super().__init__()

        self.setupUi(self)
        self.window_settings(icon, old_task_name, name_table)

    @logger.catch(message='Ошибка настроек окна "Изменить"')
    def window_settings(self, icon, old_name, table_name):
        self.setStyleSheet(DB.get_settings('color'))
        self.setWindowTitle('Изменить задачу')
        self.setWindowIcon(icon)
        self.name_item.setPlaceholderText('Введите новое название')
        self.label.setText(old_name)

        self.cancel.clicked.connect(self.quit)
        self.submit.clicked.connect(lambda x: self.edit(old_name, table_name))
        self.submit.setText('Изменить')

        self.cancel.setShortcut('Escape')
        self.submit.setShortcut('Return')

    def quit(self) -> None:
        self.name_item.setText('')
        self.window_closed.emit()
        self.close()

    @logger.catch(message='Невозможно изменить объект')
    def edit(self, old_name, table_name) -> None:
        """
        Обработчик подтверждения изменения
        :return: None
        """
        new_task = self.name_item.text()
        if new_task:
            DB.edit(table_name, old_name, new_task)
        self.quit()


class SettingWin(QWidget, Ui_Settings):
    """Класс окна настроек"""

    window_closed = QtCore.pyqtSignal()

    def __init__(self, icon: QIcon = None, parent=None):
        super(SettingWin, self).__init__(parent)

        self.setupUi(self)
        self.window_settings(icon)

    @logger.catch(message='Ошибка настроек окна "Настройки"')
    def window_settings(self, icon: QIcon = None) -> None:

        self.spinBox.setValue(DB.get_settings('icon'))
        self.setStyleSheet(DB.get_settings('color'))

        self.pink.clicked.connect(lambda ch, btn=self.pink: self.set_color(btn))
        self.black.clicked.connect(lambda ch, btn=self.black: self.set_color(btn))
        self.white.clicked.connect(lambda ch, btn=self.white: self.set_color(btn))
        self.gray.clicked.connect(lambda ch, btn=self.gray: self.set_color(btn))

        self.cancel.clicked.connect(self.quit)
        self.submit.clicked.connect(self.save_settings)

    @classmethod
    @logger.catch(message='Невозможно изменить цвет')
    def set_color(cls, bttn):
        old_color = DB.get_settings('color')
        new_color = bttn.styleSheet()
        DB.update_settings('color', new_color, old_color)

    def quit(self):
        self.window_closed.emit()
        self.destroy()

    def save_settings(self):
        old_icon = DB.get_settings('icon')
        new_icon = int(self.spinBox.text())
        DB.update_settings('icon', new_icon, old_icon)
        self.quit()

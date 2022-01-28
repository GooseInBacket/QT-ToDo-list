import sys
from PyQt5.QtCore import QSize, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMenu
from Windows.main_win import Ui_MainWindow
from data_base import DataBase
from window import AddWindow, TaskWindow, SettingWin
from loguru import logger
from settings import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """
        Класс основного окна
        """
        super().__init__()

        self.setupUi(self)
        self.create_button()
        self.__data_base = DataBase()
        self.__window = AddWindow()

        self.create_main_menu()
        self.setWindowIcon(QIcon(icon_todo))

        self.settings.setText('')
        self.settings.setIcon(QIcon(icon_setting))
        self.settings.setIconSize(QSize(size_si, size_si))

        self.add.clicked.connect(self.add_new_item)
        self.settings.clicked.connect(self.settings_win)
        self.main_list.itemClicked.connect(self.click)
        self.main_list.installEventFilter(self)

    def create_main_menu(self) -> None:
        """
        Создаёт / обновляет список элементов
        :return: None
        """
        self.main_list.clear()
        list_item = map(lambda x: f'| {x[0]}', self.__data_base.get_all_items())
        for i, name in enumerate(list_item):
            self.create_item(i, name)
        logger.info('Главное окно обновлено')

    def add_new_item(self) -> None:
        """
        Добавляет новый элемент в список главного окна
        :return: None
        """
        self.__window.window_closed.connect(self.create_main_menu)
        self.__window.show()

    def create_button(self) -> None:
        """
        Создание абстрактной кнопки c "Создать" с иконкой
        :return: None
        """
        icon = QIcon(icon_plus)
        self.add.setIcon(icon)
        self.add.setText(' Создать список')
        self.add.setIconSize(QSize(size_ti, size_ti))

    def create_item(self, i: int, name: str) -> None:
        """
        Создаёт объект списка в главном окне
        :param i: номер элемента
        :param name: имя элемента
        :return: None
        """
        item = QListWidgetItem()
        if i < 7:
            icon = QIcon(f'Icon/item_{i + 1}.png')
        else:
            icon = QIcon(icon_todo)
        item.setIcon(icon)
        item.setText(name)

        self.main_list.addItem(item)
        self.main_list.setIconSize(QSize(size_ti, size_ti))

    def click(self, item) -> None:
        """Обработчик нажатия на объект в списке"""
        self.task_win = TaskWindow(item.text()[2:], QIcon(item.icon()))
        self.task_win.show()

    def eventFilter(self, source, event) -> bool:
        """
        Обработчик нажатия на правую кнопку мыши + контекстное меню
        :return: bool
        """
        if event.type() == QEvent.ContextMenu and source is self.main_list:
            item = source.itemAt(event.pos())
            if item is not None:
                text = item.text()[2:]
                if text not in 'Мой день, Важно, Запланировано, ' \
                               'Все, Завершенные, Назначить мне, Задачи'.split(', '):
                    menu = QMenu()
                    delete_action = menu.addAction('Удалить')
                    delete_action.setIcon(QIcon(icon_bin))

                    action = menu.exec_(event.globalPos())
                    if action == delete_action:
                        self.delete(text)
            return True
        return super().eventFilter(source, event)

    def delete(self, item: str) -> None:
        """
        Обработчик функции "удалить" в контекстном меню
        :param item: объект нажатия
        :return: None
        """
        self.__data_base.delete_table(item)
        self.create_main_menu()

    def settings_win(self) -> None:
        """
        Обработчик нажатия на кнопку настроек
        :return: None
        """
        self.stgs = SettingWin()
        self.stgs.show()


def run():
    """Функция запуска приложения"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

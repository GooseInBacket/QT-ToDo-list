import sys
from PyQt5.QtCore import QSize, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMenu
from Windows.main_win import Ui_MainWindow
from data_base import DataBase
from window import AddWindow, TaskWindow, SettingWin


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.create_button()
        self.__data_base = DataBase()
        self.__window = AddWindow()

        self.create_main_menu()
        self.setWindowIcon(QIcon('Icon/to-do.png'))

        self.settings.setText('')
        self.settings.setIcon(QIcon('Icon/settings.png'))
        self.settings.setIconSize(QSize(20, 20))

        self.add.clicked.connect(self.add_new_item)
        self.settings.clicked.connect(self.settings_win)
        self.main_list.itemClicked.connect(self.click)
        self.main_list.installEventFilter(self)

    def create_main_menu(self) -> None:
        self.main_list.clear()
        list_item = map(lambda x: f'| {x[0]}', self.__data_base.get_all_items())
        for i, name in enumerate(list_item):
            self.create_item(i, name)

    def add_new_item(self) -> None:
        self.__window.window_closed.connect(self.create_main_menu)
        self.__window.show()

    def create_button(self) -> None:
        icon = QIcon(f'Icon/plus.png')
        self.add.setIcon(icon)
        self.add.setText(' Создать список')
        self.add.setIconSize(QSize(15, 15))

    def create_item(self, i: int, name: str) -> None:
        item = QListWidgetItem()
        if i < 7:
            icon = QIcon(f'Icon/item_{i + 1}.png')
        else:
            icon = QIcon(f'Icon/to-do.png')
        item.setIcon(icon)
        item.setText(name)

        self.main_list.addItem(item)
        self.main_list.setIconSize(QSize(15, 15))

    def click(self, item) -> None:
        self.task_win = TaskWindow(item.text()[2:], QIcon(item.icon()))
        self.task_win.show()

    def eventFilter(self, source, event) -> bool:
        if event.type() == QEvent.ContextMenu and source is self.main_list:
            item = source.itemAt(event.pos())
            if item is not None:
                text = item.text()[2:]
                if text not in 'Мой день, Важно, Запланировано, ' \
                               'Все, Завершенные, Назначить мне, Задачи'.split(', '):
                    menu = QMenu()
                    delete_action = menu.addAction('Удалить')
                    delete_action.setIcon(QIcon('Icon/bin (1).png'))

                    action = menu.exec_(event.globalPos())
                    if action == delete_action:
                        self.delete(text)
            return True
        return super().eventFilter(source, event)

    def delete(self, item: str) -> None:
        self.__data_base.delete_table(item)
        self.create_main_menu()

    def settings_win(self) -> None:
        self.stgs = SettingWin()
        self.stgs.show()


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

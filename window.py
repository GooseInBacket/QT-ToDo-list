from PyQt5.QtCore import pyqtSignal, QSize, QDate, QTime, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction

from Windows.add_win import Ui_Form
from Windows.task_win import Ui_Form as Task
from Windows.add_task import Ui_Form as Ui_AddTask

from data_base import DataBase
from datetime import datetime


class AddWindow(QWidget, Ui_Form):
    window_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon('Icon/plus.png'))
        self.__data_base = DataBase()

        self.cancel.clicked.connect(self.quit)
        self.submit.clicked.connect(self.set_item)

    def set_item(self):
        name = (self.name_item.text(),)
        if name[0]:
            self.__data_base.add_new_item_in_main_list(name)
        self.quit()

    def quit(self):
        self.name_item.setText('')
        self.window_closed.emit()
        self.close()


class TaskWindow(QWidget, Task):
    def __init__(self, win_name: str, icon):
        super(TaskWindow, self).__init__()
        self.setupUi(self)
        self.__data_base = DataBase()

        self.setWindowIcon(icon)
        self.__window_name = '_'.join(win_name.split())
        self.add.setIcon(QIcon(f'Icon/plus.png'))

        self.setWindowTitle(win_name)
        self.name.setText(win_name)

        self.update_tasks()
        self.set_date(win_name)

        self.add_win = AddTask(self.__window_name)
        self.__edit_win = AddWindow()

        self.add.clicked.connect(self.add_task)
        self.list_todo.itemDoubleClicked.connect(self.double_clicked)
        self.list_todo.installEventFilter(self)

    def add_task(self):
        self.add_win.window_closed.connect(self.update_tasks)
        self.add_win.show()

    def update_tasks(self):
        self.list_todo.clear()
        tasks = map(lambda x: f' {x[0]}', self.__data_base.get_all_tasks_from(self.__window_name))
        for name in tasks:
            self.create_item(name)

    def create_item(self, name: str):
        item = QListWidgetItem()
        status = self.__data_base.get_from(self.__window_name, name[1:])[1]

        if status:
            item.setIcon(QIcon('Icon/check-mark-round.png'))
        else:
            item.setIcon(QIcon('Icon/check_round.png'))
        item.setText(name)

        self.list_todo.addItem(item)
        self.list_todo.setIconSize(QSize(15, 15))

    def set_date(self, name_window: str):
        if name_window == 'Мой день':
            self.date.setText(f'Сегодня {datetime.today().date()}')
        else:
            self.date.setText('')

    def double_clicked(self, item):
        text = item.text()[1:]
        status = self.__data_base.get_from(self.__window_name, text)[1]
        self.__data_base.refresh_status(self.__window_name, text)
        if status:
            item.setIcon(QIcon('Icon/check-mark-round.png'))
        else:
            item.setIcon(QIcon('Icon/check_round.png'))
        self.update_tasks()

    def eventFilter(self, source, event) -> bool:
        if event.type() == QEvent.ContextMenu and source is self.list_todo:
            item = source.itemAt(event.pos())
            if item is not None:
                text = item.text()[1:]

                menu = QMenu()
                delete_action = menu.addAction('Удалить')
                delete_action.setIcon(QIcon('Icon/bin (1).png'))

                edit_action = menu.addAction('Изменить')
                edit_action.setIcon(QIcon('Icon/refresh.png'))

                action = menu.exec_(event.globalPos())
                if action == delete_action:
                    self.delete(text)
                elif action == edit_action:
                    self.edit(text, QIcon(edit_action.icon()))
            return True
        return super().eventFilter(source, event)

    def delete(self, item: str):
        self.__data_base.delete(self.__window_name, item)
        self.update_tasks()

    def edit(self, item, icon):
        self.edit_win = EditWin(item, self.__window_name, icon)
        self.edit_win.window_closed.connect(self.update_tasks)
        self.edit_win.show()


class AddTask(QWidget, Ui_AddTask):
    window_closed = pyqtSignal()

    def __init__(self, window_name: str):
        super(AddTask, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon('Icon/plus.png'))
        self.__window_name = window_name
        self.__data_base = DataBase()

        self.date.setDate(QDate(datetime.today().date()))
        self.date.setTime(QTime(datetime.today().time()))

        self.cancel.clicked.connect(self.quit)
        self.add.clicked.connect(self.set_task)

    def set_task(self):
        task = self.task_line.text()
        if task:
            self.__data_base.add_task_to(self.__window_name, task)
        self.quit()

    def quit(self):
        self.task_line.setText('')
        self.window_closed.emit()
        self.close()


class EditWin(QWidget, Ui_Form):
    window_closed = pyqtSignal()

    def __init__(self, old_task_name: str | int, name_table: str, icon):
        super().__init__()
        self.__name_table = name_table
        self.__data_base = DataBase()
        self.setupUi(self)
        self.__old_task_name = old_task_name

        self.setWindowTitle('Изменить задачу')
        self.setWindowIcon(icon)
        self.name_item.setPlaceholderText('Введите новое название')
        self.label.setText(self.__old_task_name)

        self.cancel.clicked.connect(self.quit)
        self.submit.setText('Изменить')
        self.submit.clicked.connect(self.edit)

    def quit(self):
        self.name_item.setText('')
        self.window_closed.emit()
        self.close()

    def edit(self):
        new_task = self.name_item.text()
        if new_task:
            self.__data_base.edit(self.__name_table, self.__old_task_name, new_task)
        self.quit()


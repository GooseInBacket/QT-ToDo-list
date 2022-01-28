from main_window import run
from data_base import DataBase
from loguru import logger

if __name__ == '__main__':
    logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', encoding='UTF-8')
    dataBase = DataBase()
    run()
